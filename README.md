# dayzquery

Small Python module to decode the DayZ rules binary response.

## Requirements

Python >= 3.9, [python-a2s](https://github.com/Yepoleb/python-a2s)

## Install

`pip3 install .`

## API

### Functions

* `dayzquery.dayz_rules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`
* `async dayzquery.dayz_arules(address, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)`
* `dayzquery.dayz_rules_decode(rules_resp, encoding=DEFAULT_ENCODING)`

`dayz_rules_decode` decodes a `a2s.rules(encoding=None)` response, the other functions work just like their a2s counterpart.

### Return Values

All functions return a DayzRules instance. Some documentation is included in the source file.

## License

MIT
