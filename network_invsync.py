'''
Network InvSync - Verify ISE and YAML inventory are synchronized.

REQUIRMENTS:
$ python3 -m pip install -r requirements.txt

A ise_svc-net-auto.json file is loaded from ../network_confg/
Update ise_cfg_file VAR @ line 39 as required. Expected format is:
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
}
dXNlcm5hbWU6cGFzc3dvcmQ= is a Base64 encoding of string username:password

USAGE:
$ python3 network_invsync.py -i {ISE Admin Node FQDN}
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import requests # Required for API POST
import xmltodict # Requird to convert POST XML response to DICT
import pprint # Optional to Pretty Print Responses
import json # Required to process *.json ISE config file
import urllib3 # Required to disable SSL Warnings
import ipdb # Optional Debug. ipdb.set_trace()

from argparse import ArgumentParser # Required for Command Line Argument parsing
from nornir import InitNornir # Required for YAML
from nornir.core.filter import F

# Import custom modules
from modules._network_xtval import xtval
from modules._network_diffgen import diffgen

# Define Objects
pp = pprint.PrettyPrinter(indent=4)
ise_cfg_file = '../network_config/ise_svc-net-auto.json'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    ''' MAIN FUNCTION '''

    # Process Command Line Argument
    parser = ArgumentParser(description='Usage:')
    parser.add_argument('-i', '--ise', type=str, required=True,
                        help='ISE Admin Node FQDN')
    arg = parser.parse_args()

    ISENODE = arg.ise

    # Read *.json config for required ISE values.
    with open(ise_cfg_file) as ise_f:
        ise_settings = json.load(ise_f)

    OAUTH = ise_settings["OAUTH"]

    # ##########################################################################
    # GET ISE Host List and save to ilist = []
    # ##########################################################################

    ilist = []

    # Define Global API POST request values
    payload = {}
    headers = {
      'Accept': 'application/vnd.com.cisco.ise.network.networkdevice.1.1+xml',
      'Accept-Search-Result': 'application/vnd.com.cisco.ise.ers.searchresult.2.0+xm',
      'Authorization': OAUTH
    }

    # Define POST request URI
    url = "https://" + str(ISENODE) + ":9060/ers/config/networkdevice"

    # POST GET Response. User verify=False to disable SSL wanrings
    response = requests.request("GET", url, headers=headers, data = payload, verify=False)

    # pp.pprint(response.text.encode('utf8'))

    # Convert to Python Dict {}
    xdoc = xmltodict.parse(response.text.encode('utf8'))

    # Parse through XTVAL module to extract required values
    ids = xtval(xdoc, '@id')
    hosts = xtval(xdoc, '@name')

    # Generate ISE ilist []
    i = 0
    for id in ids:
        url = "https://" + str(ISENODE) + ":9060/ers/config/networkdevice/" + id

        response = requests.request("GET", url, headers=headers, data = payload, verify=False)

        xdoc = xmltodict.parse(response.text.encode('utf8'))

        # The xdoc Dict is a structure of non-indexable OrderedDicts within OrderedDicts
        # Not very pretty. As such, all we can do is dirty find using the PATTERN in
        # ise_setting JSON structure.
        PATTERN = ise_settings["PATTERN"]

        x = 0
        for p in PATTERN:
            if str(xdoc).find(str(p['TYPE'])) != -1:
                ilist.append (hosts[i])
                x += 1

        i += 1

    # ##########################################################################
    # GET YAML Host Lsit and save to ylist[]
    # ##########################################################################

    ylist = []

    nr = InitNornir(config_file='config.yaml')
    filter  = nr.filter(F(groups__contains='PROD'))
    for i in filter.inventory.hosts.keys():
        ylist.append(i)

    # ##########################################################################
    # DIFF
    # ##########################################################################

    idiff, ydiff = diffgen(ilist, ylist)

    print('\n** Configured on ISE but not in YAML:')
    print(idiff)
    print('\n** Configured in YAML but not on ISE:')
    print(ydiff)

if __name__ == "__main__":
    main()
