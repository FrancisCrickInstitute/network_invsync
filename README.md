# Network InvSync Python Script - Verify ISE, Nornir YAML and NetDisco Inventories are Synchronised

*network_invsync.py* uses an ISE API, NetDisco API and Nornir YAML query to get a list of Network Devices. A DIFF operations is used to compare the lists and post the differences to Slack.

NOTE: ISE must be configured with a valid ERS Operator Account.

## Usage
```
python3 network_invsync.py {-d | Debug [OPTIONAL]} {-v | Verbose Debug [OPTIONAL]}
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
│   ├── network_invsync.py
│   ├── modules/
│   │   ├── diffgen.py
│   │   ├── ise_api.py
│   │   ├── netdisco_api.py
│   │   ├── nornir_yml.py
│   │   ├── slackpost.py
│   │   ├── xtval.py
│   ├── config/
│   │   ├── invsync_cfg.json [1]
│   │   ├── ise_cfg.json [2]
│   │   ├── netdisco_cfg.json [3]
│   │   ├── nornir_cfg.json [4]
│   ├── README.md [THIS README]
├── network_inventory/
│   ├── groups.yaml
│   ├── hosts.yaml
│   ├── defaults.yaml
├── network_config/
│   ├── slack_network_auto.json [5]

```

- A JSON Configuration file is loaded from *invsync_cfg.json* [1]. Expected format is:

```
{
    "iPATTERN": ["ROUTER-A","ROUTER-B","SWITCH-C"],
    "xPATTERN": ["ROUTER-X","ROUTER-Y","SWITCH-Z"],
    "dSTRIP": ["mycompany.mydomain"],
    "yFILTER": ["YAML Group/ Host"],
    "SLACKPOST": 1
}
```

... where:<br />
*iPATTERN* is the a pattern to include (i.e. ["A", "B", "C"] will match Router-A, Router-B, Router-C) and add to the list to be DIFF'ed.<br />
*xPATTERN* is the a pattern to exclude (i.e. ["X", "Y", "Z"] will match Router-X, Router-Y, Router-Z) and NOT add to the list to be DIFF'ed.<br />
*dSTRIP* is any domain suffix to strip from hostnames pulled from ISE or NetDisco to maintain parity with Nornir YAML Inventory.<br />
*yFILTER* is the YAML filter used by NORNIR to filter the hosts.yaml [4]. <br />

- An ISE ERS JSON Configuration file is loaded from *ise_cfg.json* [2]. Expected format is:

```
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
    "URL": "ISE Admon Node FQDN",
    "PAGES": "ISE Page Size Limitation"
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

*URL* is the FQDN of the ISE Admin Node.<br/>
*PAGES* is the ISE page limitation. To calculate, take the total number of Network Devices and divide by 100 (e.g. for 191, pages will be 2).

- A NetDisco Configuration file is loaded from *netdisco_cfg* [3]. Expected format is:

```
{
    "USERNAME": "Valid NetDisco Username",
    "PASSWORD": "Valid NetDisco Password",
    "URL": "Valid NetDisco FQDN:PORT e.g. netdisco.mycompany.mytopleveldomain:5000"
}
```

... where:<br />
*USERNAME* & *PASSWORD* are valid NetDisco credentials
*URL* is the URL of NetDisco & TCP Port (if applicable). Go to http://{URL}/swagger-ui/ to get started.

- A YAML Configuration file is loaded *nornir_cfg.yaml* [4]. It references the .yaml files in *network_inventory* folder. The file also defines the number of concurrent connections supported.

- Where SLACKPOST = 1 in , expectation is there is a *slack_network_auto.json* [5] file in *network_config* folder. This defines the OAUTH_TOKEN and CHANNEL required to post to your Slack environment. Expected format is:

```
{
  "OAUTH_TOKEN": "<REMOVED>",
  "WEBHOOK": "https://hooks.slack.com/services/<REMOVED>",
  "USE_WEBHOOK": 0,
  "CHANNEL": <SLACK CHANNEL>"
}
```

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
