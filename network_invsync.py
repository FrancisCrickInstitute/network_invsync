'''
Network InvSync - Verify ISE and YAML inventory are synchronized.

REQUIRMENTS:
$ python3 -m pip install -r requirements.txt

A JSON file is loaded from *../network_confg/ise_ers.json
Update ise_cfg_file VAR @ line 42'ish as required. Expected format is:
{
    "OAUTH": "Basic dXNlcm5hbWU6cGFzc3dvcmQ=",
    "iPATTERN": ["A", "B", "C"],
    "xPATTERN": ["X", "Y", "Z"],
}
...where
dXNlcm5hbWU6cGFzc3dvcmQ= is a Base64 encoding of string "username:password"
iPATTERN: is the host name pattern we want to match
xPATTERN: is the host name pattern we want to exclude

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
PP = pprint.PrettyPrinter()
ise_cfg_file = '../network_config/ise_ers.json'

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    ''' MAIN FUNCTION '''

    print('\nQuerying ISE & YAML. Please Wait...')

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
    iPATTERN = ise_settings["iPATTERN"] # Include Pattern
    xPATTERN = ise_settings["xPATTERN"] # Exclude Pattern

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

    # Define POST request URI.
    # Truely herendous hack due to Cisco ISE page size limitation of 100 results!!!
    # If you have more than 100 devices you need two posts to accomodate each page.
    # Also, by default ISE has a max size of 20 so this needs to be increased to
    # max 100: ?size=100&page=* where * is a page number.
    # Without this, ERS returns a max of 20 nodes (why Cisco?).
    # See: https://community.cisco.com/t5/network-access-control/ers-returns-max-20-endpoints/m-p/3499483

    xdoc = [] # Reset

    MAX_PAGES = 10

    for p in range(MAX_PAGES):

        url = "https://" + str(ISENODE) + ":9060/ers/config/networkdevice?size=100&page=" + str(p+1)

        # POST GET Response. User verify=False to disable SSL wanrings
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        # Convert to Python Dict {} and append to xdoc []
        xdoc.append(xmltodict.parse(response.text.encode('utf8')))

    # print(pp.pprint(xdoc))

    # Parse through XTVAL module to extract required values
    ids = xtval(xdoc, '@id')
    hosts = xtval(xdoc, '@name')

    # Loop through hosts. If host name contains iPATTERN and not xPATTERN append
    # to ilist
    for host in hosts:
        if any(iPAT in host for iPAT in iPATTERN) and not any(xPAT in host for xPAT in xPATTERN):
            ilist.append(host)


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
    PP.pprint(idiff)
    print('\n** Configured in YAML but not on ISE:')
    PP.pprint(ydiff)
    print('\n')

if __name__ == "__main__":
    main()
