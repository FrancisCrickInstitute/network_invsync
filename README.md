# Network InvSync - Verify ISE and YAML inventory are synchronised.

## Requirements
```
python3 -m pip install -r requirements.txt
```

## Usage
```
python3 network_invsync.py -i {ISE Admin Node FQDN}
```
A JSON file is loaded from *../network_confg/ise_svc-net-auto.json*

Expected format is:

```
{
     "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
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
