import io
from dataclasses import dataclass

import a2s
import a2s.byteio
from a2s.defaults import DEFAULT_TIMEOUT, DEFAULT_ENCODING


"""
Names are based around the documentation at
https://community.bistudio.com/wiki/Arma_3:_ServerBrowserProtocol3
I do not understand their meaning at the time of writing as I have never played DayZ.
"""

DLC_FROSTLINE = 2

@dataclass
class DayzMod:
    """Some hash value for identification probably"""
    hash: int

    """Length of the workshop ID in bytes, only useful if it someday contains additional data"""
    workshop_id_len: int

    """Steam Workshop ID of the mod"""
    workshop_id: int

    """Mod name"""
    name: str

@dataclass
class DayzRules:
    """Protocol version, always 2"""
    protocol_version: int

    """Overflow flags, meaning unknown"""
    overflow_flags: int

    """Flags to indicate which DLCs are present in the response, only known values are 0 or DLC_FROSTLINE"""
    dlc_flags: int

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
    rules_resp = a2s.rules(address, timeout, encoding=None)
    return dayz_rules_decode(rules_resp, encoding)

async def dayz_arules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING):
    rules_resp = await a2s.arules(address, timeout, encoding=None)
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

    protocol_version = reader.read_uint8()
    overflow_flags = reader.read_uint8()
    dlc_flags = reader.read_uint16()

    dlcs = []
    for i in range(dlc_flags.bit_count()):
        dlcs.append(reader.read_uint32())

    mods_count = reader.read_uint8()
    mods = []
    for i in range(mods_count):
        mod_hash = reader.read_uint32()
        workshop_id_len = reader.read_uint8()
        workshop_id = int.from_bytes(reader.read(workshop_id_len & 0x0F), "little")
        string_length = reader.read_uint8()
        name = reader.read(string_length).decode(encoding, errors="replace")
        mods.append(DayzMod(mod_hash, workshop_id_len, workshop_id, name))

    signatures_count = reader.read_uint8()
    signatures = []
    for i in range(signatures_count):
        name_len = reader.read_uint8()
        name = reader.read(name_len).decode(encoding, errors="replace")
        signatures.append(name)

    allowed_build = bool(int(rules_resp[b"allowedBuild"].decode(encoding)))
    dedicated = bool(int(rules_resp[b"dedicated"].decode(encoding)))
    island = rules_resp[b"island"].decode(encoding)
    language = int(rules_resp[b"language"].decode(encoding))
    platform = rules_resp[b"platform"].decode(encoding)
    required_build = rules_resp[b"requiredBuild"].decode(encoding)
    required_version = rules_resp[b"requiredVersion"].decode(encoding)
    time_left = int(rules_resp[b"timeLeft"].decode(encoding))

    return DayzRules(
        protocol_version, overflow_flags, dlc_flags, dlcs, mods_count, mods,
        signatures_count, signatures, allowed_build, dedicated, island, language, platform,
        required_build, required_version, time_left)
