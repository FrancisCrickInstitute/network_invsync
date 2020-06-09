# Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronised

*network_invsync.py* uses an ISE API request to get a list of Network Devices. It also uses NORNIR to get a list of Network Devices configured in the YAML Inventory. A Python DIFF operations is used to compare the lists and post the differences to Slack.


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
│   ├── pattern.json [1]
│   ├── config.yaml [2]
│   ├── README.md [THIS README]
├── network_inventory [3]
│   ├── groups.yaml
│   ├── hosts.yaml
│   ├── defaults.yaml
├── network_config
│   ├── ise_ers.json [4]
│   ├── slack_network_auto.json [5]

```

- A Pattern JSON Configuration file is loaded from *pattern.json* [1]. Expected format is:

```
{
    "iPATTERN": ["A", "B", "C"],
    "xPATTERN": ["X", "Y", "Z"]
}
```

... where:<br />
*iPATTERN* is the a pattern to include (i.e. ["A", "B", "C"] will match Router-A, Router-B, Router-C) and add to the list to be DIFF'ed.<br />
*xPATTERN* is the a pattern to exclude (i.e. ["X", "Y", "Z"] will match Router-X, Router-Y, Router-Z) and NOT add to the list to be DIFF'ed.<br />


- A YAML Configuration file is loaded *config.yaml* in the working directory [2]. This is used by NORNIR to build a list of hosts given a *-y* CLI argument. It references the .yaml files in *network_inventory* [3] folder. The file also defines the number of concurrent connections supported.

- An ISE ERS JSON Configuration file is loaded from *ise_ers.json* [4]. Expected format is:

```
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
}
```

... where:<br />
*dXNlcm5hbWU6cGFzc3dvcmQ=* is a Base64 encoding of the actual string *username:password*. Go to https://www.base64encode.org/ and change to valid ISE ERS Credentials.<br />

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
