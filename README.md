# Network InvSync - Verify ISE and YAML inventory are synchronised.

## Requirements
```
python3 -m pip install -r requirements.txt
```

## Usage
```
python3 network_invsync.py -i {ISE Admin Node FQDN}
```
A JSON file is loaded from *../network_confg/ise_ers.json*

Expected format is:

```
{
     "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
     "PATTERN": [{"TYPE": "example-1"}, {"TYPE": "example-2"}]
}
```

*dXNlcm5hbWU6cGFzc3dvcmQ=* is a Base64 encoding of string *username:password*

## Change History

### Version 18.05.2020
- Original Version

### Version 18.05.2020_2
- Updated README.md

### Version 19.05.2020
- Support ISE Device Type filtering.

### Version 19.05.2020_2
- Hack to work with ISE paging limitations. Cleanup required!

### Version 20.05.2020
- Minor improvements to print output
