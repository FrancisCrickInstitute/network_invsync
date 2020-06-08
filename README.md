# Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronised

*network_invsync.py* uses an ISE API request to get a list of Network Devices. It also uses NORNIR to get a list of Network Devices configured in the YAML Inventory. A Python DIFF operations is used to compare the lists and post the differences to Slack.

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
│   ├── config.yaml [1]
│   ├── README.md [THIS README]
├── network_inventory [2]
│   ├── groups.yaml
│   ├── hosts.yaml
│   ├── defaults.yaml
├── network_config
│   ├── slack_network_auto.json[3]
│   ├── ise_ers.json[4]
```
- Expectation is there is a *config.yaml* in the working directory [1]. This is used by NORNIR to build a list of hosts given a *-y* CLI argument. It references the .yaml files in *network_inventory* [2] folder. The file also defines the number of concurrent connections supported.

- An ISE configuration file is loaded from *ise_ers.json* [4]. Expected format is:

```
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
    "iPATTERN": ["A", "B", "C"],
    "xPATTERN": ["X", "Y", "Z"],
}
```

... where:<br />
*dXNlcm5hbWU6cGFzc3dvcmQ=* is a Base64 encoding of the actual string *username:password*. Go to https://www.base64encode.org/<br />
*iPATTERN* is the host name pattern to match<br />
*xPATTERN* is the host name pattern to exclude<br />

- Where the *-s* (Post-to-Slack) CLI argument is passed, expectation is there is a *slack_network_auto.json* [3] file in *network_config* folder. This defines the OAUTH token and CHANNEL required to post to your Slack environment. Expected format is:

```
{
  "OAUTH_TOKEN": "<REMOVED>",
  "WEBHOOK": "https://hooks.slack.com/services/<REMOVED>",
  "USE_WEBHOOK": 0,
  "CHANNEL": <SLACK CHANNEL>"
}
```

## Usage
```
python3 network_invsync.py -i {ISE PSN DNS} -s [OPTIONAL]
```

## To-Do
n/a


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

### VERSION 08.06.2020
- Updated README.md
