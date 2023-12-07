import io

import a2s
import a2s.byteio
from a2s.datacls import DataclsMeta
from a2s.defaults import DEFAULT_TIMEOUT, DEFAULT_ENCODING


"""
Names are based around the documentation at
https://community.bistudio.com/wiki/Arma_3:_ServerBrowserProtocol3
I do not understand their meaning at the time of writing as I have never played DayZ.
"""

class DayzMod(metaclass=DataclsMeta):
    """Some hash value for identification probably"""
    hash: int

    """Length of the workshop ID in bytes, only useful if it someday contains additional data"""
    workshop_id_len: int

    """Steam Workshop ID of the mod"""
    workshop_id: int

    """Mod name"""
    name: str

class DayzRules(metaclass=DataclsMeta):
    unknown_0: int

    unknown_1: int

    """Raw value for number of DLC hash entries, you should prefer len(dlcs)"""
    dlcs_count: int

    unknown_3: int

    """DLC hash entries"""
    dlcs: list[int]

    """Raw value for number of mod entries, you should prefer len(mods)"""
    mods_count: int

    """Mod entries"""
    mods: list[DayzMod]

    """Raw value for number of signature entries, you should prefer len(signatures)"""
    signatures_count: int

    """List of signatures"""
    signatures: list[str]

    """Values in the unencoded response part, too lazy to figure them out"""
    allowed_build: bool
    dedicated: bool
    island: str
    language: int
    platform: str
    required_build: str
    required_version: str
    time_left: int



def dayz_rules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING):
    rules_resp = a2s.rules(address, timeout, encoding)
    return dayz_rules_decode(rules_resp, encoding)

async def dayz_arules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING):
    rules_resp = await a2s.arules(address, timeout, encoding)
    return dayz_rules_decode(rules_resp, encoding)


def dayz_rules_decode(rules_resp, encoding=DEFAULT_ENCODING):
    bin_items = []
    for key, content in rules_resp.items():
        if len(key) == 2:
            key_int = int.from_bytes(key, "little")
            bin_items.append((key_int, content))
    bin_items.sort()
    bin_content = b"".join(x[1] for x in bin_items)

    ESCAPE_SEQUENCES = [(b"\x01\x02", b"\x00"), (b"\x01\x03", b"\xFF"), (b"\x01\x01", b"\x01")]
    for seq, char in ESCAPE_SEQUENCES:
        bin_content = bin_content.replace(seq, char)

    bin_stream = io.BytesIO(bin_content)
    reader = a2s.byteio.ByteReader(bin_stream, endian="<")

    result = DayzRules()
    result.unknown_0 = reader.read_uint8()
    result.unknown_1 = reader.read_uint8()
    result.dlcs_count = reader.read_uint8()
    result.unknown_3 = reader.read_uint8()

    result.dlcs = []
    for i in range(result.dlcs_count):
        result.dlcs.append(reader.read_uint32())

    result.mods_count = reader.read_uint8()
    result.mods = []
    for i in range(result.mods_count):
        mod = DayzMod()
        mod.hash = reader.read_uint32()
        mod.workshop_id_len = reader.read_uint8()
        mod.workshop_id = int.from_bytes(reader.read(mod.workshop_id_len & 0x0F), "little")
        string_length = reader.read_uint8()
        mod.name = reader.read(string_length).decode(encoding, errors="replace")
        result.mods.append(mod)

    result.signatures_count = reader.read_uint8()
    result.signatures = []
    for i in range(result.signatures_count):
        name_len = reader.read_uint8()
        name = reader.read(name_len).decode(encoding, errors="replace")
        result.signatures.append(name)

    result.allowed_build = bool(int(rules_resp[b"allowedBuild"].decode(encoding)))
    result.dedicated = bool(int(rules_resp[b"dedicated"].decode(encoding)))
    result.island = rules_resp[b"island"].decode(encoding)
    result.language = int(rules_resp[b"language"].decode(encoding))
    result.platform = rules_resp[b"platform"].decode(encoding)
    result.required_build = rules_resp[b"requiredBuild"].decode(encoding)
    result.required_version = rules_resp[b"requiredVersion"].decode(encoding)
    result.time_left = int(rules_resp[b"timeLeft"].decode(encoding))

    return result
