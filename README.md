# Network InvSync Python Script - Verify ISE, Nornir YAML and NetDisco Inventories are Synchronised

*network_invsync.py* uses an ISE API, NetDisco API and Nornir YAML query to get a list of Network Devices. A DIFF operations is used to compare the lists and post the differences to Slack.

NOTE: ISE must be configured with a valid ERS Operator Account.

## Usage
```
python3 network_invsync.py
```


## Requirements
```
python3 -m pip install -r requirements.txt
```

Expected folder structure is:

```
$
.
├── network_invsync/
│   ├── invsync.py
│   ├── common/
│   │   ├── _slack_api.py
│   │   ├── _session_tk.py
│   ├── modules/
│   │   ├── _diffgen.py
│   │   ├── _ise_api.py
│   │   ├── _netdisco_api.py
│   │   ├── _nornir_yml.py
│   │   ├── _xtval.py
│   ├── config/
│   │   ├── app_cfg.json [1]
│   │   ├── nornir_cfg.json [2]
│   ├── README.md [THIS README]
├── network_inventory/
│   ├── groups.yaml
│   ├── hosts.yaml
│   ├── defaults.yaml
├── network_config/
│   ├── network_vault.json [3]

```

- A JSON Configuration file is loaded from *invsync_cfg.json* [1]. Expected format is:

```
{
    "IPATTERN": ["ROUTER-A","ROUTER-B","SWITCH-C"],
    "XPATTERN": ["ROUTER-X","ROUTER-Y","SWITCH-Z"],
    "DOM_STRIP": ["mycompany.mydomain"]
    "YAML_FILTERFILTER": ["YAML Group/ Host"],
    "SLACK_POST": {0 = No slack Post, 1 = Slack Post},
    "DEBUG": {0 = Debug Off, 1 = Basic Debug, 2 = Verbose Debug}
}
```

... where:<br />
*IPATTERN* is the a pattern to include (i.e. ["A", "B", "C"] will match Router-A, Router-B, Router-C) and add to the list to be DIFF'ed.<br />
*XPATTERN* is the a pattern to exclude (i.e. ["X", "Y", "Z"] will match Router-X, Router-Y, Router-Z) and NOT add to the list to be DIFF'ed.<br />
*DOM_STRIP* is any domain suffix to strip from hostnames pulled from ISE or NetDisco to maintain parity with Nornir YAML Inventory.<br />
*YAML_FILTER* is the YAML filter used by NORNIR to filter the hosts.yaml [4]. <br />

- *nornir_cfg.yaml* [2] A YAML Configuration file is loaded . It references the .yaml files in *network_inventory* folder. The file also defines the number of concurrent connections supported.

- *network_vault.json* [3] A JSON Configuration file is loaded to generate the SESSION_TK. Expected format is:

```
{
    "SLACK_OAUTH_TOKEN": "your_token_here",
    "SLACK_WEBHOOK": "your_webhook_here",
    "SLACK_USE_WEBHOOK": 0,
    "SLACK_CHANNEL": "your_channel_here",
    "ISE_OAUTH_TOKEN": "dXNlcm5hbWU6cGFzc3dvcmQ=",
    "ISE_URL": "<REMOVED>",
    "ISE_PAGES": 2,
    "NETDISCO_USERNAME": "<REMOVED>",
    "NETDISCO_PASSWORD": "<REMOVED>",
    "NETDISCO_URL": "<REMOVED>",
    "AAA_UN": "<REMOVED>",
    "AAA_PW": "<REMOVED>",
    "AAA_EN": "<REMOVED>",
    "SNMP_KEY": "<REMOVED>",
    "NTP_KEY": "<REMOVED>",
    "NTP_MD5": "<REMOVED>",
    "RADIUS_PAC": "<REMOVED>"
}
```

... where:<br />
*dXNlcm5hbWU6cGFzc3dvcmQ=* is a Base64 encoding of the actual string *username:password*. To generate, in Python interpreter type the following and replace username:password with valid ISE ERS credentials:<br/>

```
>>> message = "username:password"
>>> message_bytes = message.encode('ascii')
>>> base64_bytes = base64.b64encode(message_bytes)
>>> base64_bytes
b'dXNlcm5hbWU6cGFzc3dvcmQ='
```

*ISE_URL* is the FQDN of the ISE Admin Node.<br/>
*ISE_PAGES* is the ISE page limitation. To calculate, take the total number of Network Devices and divide by 100 (e.g. for 191, pages will be 2).
*NETDISCO_USERNAME* & *NETDISCO_PASSWORD* are valid NetDisco credentials
*NETDISCO_URL* is the URL of NetDisco & TCP Port (if applicable). Go to http://{URL}/swagger-ui/ to get started.

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

### Version 22.05.2020
- Redesigned to search ISE hosts on PATTERN extracted from ise_ers.json as ISE TYPE is to vague in our deployment.

### Version 22.05.2020_2
- Added Slack Posting

### Version 08.06.2020
- Minor Slack post cleanup.

### Version 08.06.2020
- Updated README.md

### Version 09.06.2020
- Split Pattern and ISE Configuration into two separate files.
- Updated README.md

### Version 10.06.2020
- Created config.json to store all custom attributes.
- Added Slack CLI Argument.

### Version 11.06.2020
- Moved ISE Config file from ../network_config to local folder.
- Added Example ISE and CFG JSON files.
- Added Debug CLI argument.
- Updated README.md

### Version 02.07.2020
- Git Checkpoint

### Version 02.07.2020_2
- Major overhaul to support querying of NetDisco. Functions now modularised.

### Version 02.07.2020_3
- Corrected error in Slack Posting and minor printing tweaks.

### Version 02.07.2020_4
- Moved all config files into /config folder

### Version 03.07.2020
- Moved ISE URL into ise_api.json instead of a CLI Argument.

### Version 06.07.2020
- Logging cleanup.
- README.md updated.

### Version 06.07.2020_2
- Corrected minor typo

### Version 08.07.2020
- Moved slackpost function to slackpost module.
- Parsed through PYLINT linter.

### Version 30.09.2020
- Major rewrite to align with network_vault.json centralised credential repo.

### Version 01.10.2020
- Minor cleanup

### Version 01.10.2020_2
- Captured System username and hostname and included in log.

### Version 12.10.2020
- Updated SESSION_TK YAML Filter Reference from yFILTER to YAMLF.

### Version 05.05.2021
- Major rewrite to align structure with team practices. 
