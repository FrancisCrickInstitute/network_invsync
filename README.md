# Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronised

*network_invsync.py* uses an ISE API request to get a list of Network Devices. It also uses NORNIR to get a list of Network Devices configured in the YAML Inventory. A Python DIFF operations is used to compare the lists and post the differences to Slack.

NOTE: ISE must be configured with a valid ERS Operator Account.

## Usage
```
python3 network_invsync.py -i {ISE PSN DNS} -s [OPTIONAL]
```


## Requirements
```
python3 -m pip install -r requirements.txt
```

Expected folder structure is:

```
$
.
├── network_invsync
│   ├── network_invsync.py
│   ├── invsync_cfg.json [1]
│   ├── invsync_ise.json [2]
│   ├── config.yaml [3]
│   ├── README.md [THIS README]
├── network_inventory
│   ├── groups.yaml
│   ├── hosts.yaml [4]
│   ├── defaults.yaml
├── network_config
│   ├── slack_network_auto.json [5]

```

- A JSON Configuration file is loaded from *invsync_cfg.json* [1]. Expected format is:

```
{
    "iPATTERN": ["A", "B", "C"],
    "xPATTERN": ["X", "Y", "Z"],
    "mPAGES": 2
    "yFILTER": ["YAML Group/ Host"]
}
```

... where:<br />
*iPATTERN* is the a pattern to include (i.e. ["A", "B", "C"] will match Router-A, Router-B, Router-C) and add to the list to be DIFF'ed.<br />
*xPATTERN* is the a pattern to exclude (i.e. ["X", "Y", "Z"] will match Router-X, Router-Y, Router-Z) and NOT add to the list to be DIFF'ed.<br />
*mPAGES* is the maximum number of pages supported by the ISE API GET Request. This should be reflective of your environment (i.e. On the ISE PSN Node > Administration > Network Resources > Network Devices. Take total number of devices and divide by 100 to get Max Pages).<br />
*yFILTER* is the YAML filter used by NORNIR to filter the hosts.yaml [4]. <br />

- An ISE ERS JSON Configuration file is loaded from *invsync_ise.json* [2]. Expected format is:

```
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
}
```

... where:<br />
*dXNlcm5hbWU6cGFzc3dvcmQ=* is a Base64 encoding of the actual string *username:password*. To generate, in Python interpreter type the following and replace username:password with valid ISE ERS credentials:

```
>>> message = "username:password"
>>> message_bytes = message.encode('ascii')
>>> base64_bytes = base64.b64encode(message_bytes)
>>> base64_bytes
b'dXNlcm5hbWU6cGFzc3dvcmQ='
```

- A YAML Configuration file is loaded *config.yaml* [3]. It references the .yaml files in *network_inventory* folder. The file also defines the number of concurrent connections supported.

- Where the *-s* (Post-to-Slack) CLI argument is passed, expectation is there is a *slack_network_auto.json* [5] file in *network_config* folder. This defines the OAUTH_TOKEN and CHANNEL required to post to your Slack environment. Expected format is:

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
