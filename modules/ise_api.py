'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import json # Required to process JSON requests
import requests # Required for API POST
import xmltodict # Requird to convert POST XML response to DICT
import pprint # Optional to Pretty Print Responses
import ipdb # Optional Debug. ipdb.set_trace()

from modules.xtval import xtval

pp = pprint.PrettyPrinter()

def ise_api(SESSION_TK):

    print('\n' + '#' * 10 + ' ISE API Query ' + '#' * 10 + '\n')

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG ISE SESSION_TK REceived:')
        print(pp.pprint(SESSION_TK))

    # Read .json config for required ISE values.
    ise_f = 'config/ise_api.json' # Script Config File.

    with open(ise_f) as ise_f:
        ise = json.load(ise_f)

    OAUTH = ise["OAUTH"]
    URL = ise['URL']
    PAGES = ise['PAGES']

    # Define Global API POST request values
    payload = {}
    headers = {
      'Accept': 'application/vnd.com.cisco.ise.network.networkdevice.1.1+xml',
      'Accept-Search-Result': 'application/vnd.com.cisco.ise.ers.searchresult.2.0+xm',
      'Authorization': OAUTH,
      'cache-control': 'no-cache'
    }

    # Define POST request URI.
    # Truely herendous hack due to Cisco ISE page size limitation of 100 results!!!
    # If you have more than 100 devices you need two posts to accomodate each page.
    # Also, by default ISE has a max size of 20 so this needs to be increased to
    # max 100: ?size=100&page=* where * is a page number.
    # Without this, ERS returns a max of 20 nodes (why Cisco?).
    # See: https://community.cisco.com/t5/network-access-control/ers-returns-max-20-endpoints/m-p/3499483

    xdoc = []

    for page in range(PAGES):

        url = "https://" + str(URL) + ":9060/ers/config/networkdevice?size=100&page=" + str(page+1)

        # POST GET Response. User verify=False to disable SSL wanrings
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        # Curiosity with ISE and occasional polling where it returns 401. Retry
        # but with delay

        if response.status_code == 200:
            pass

        if response.status_code == 401:
            time.sleep(5)
            response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        # Convert to Python Dict {} and append to xdoc []
        xdoc.append(xmltodict.parse(response.text.encode('utf8')))

    if SESSION_TK['vDEBUG']: # True
        print('\n***DEBUG ISE POST GET Response:')
        print(pp.pprint(xdoc))

    # Parse through XTVAL module to extract required values
    # ids = xtval(xdoc, '@id')
    hosts = xtval(xdoc, '@name')

    # Loop through hosts. If host name contains iPATTERN and not xPATTERN append
    # to ilist
    ilist = []

    for host in hosts:
        if any(iPAT in host for iPAT in SESSION_TK['iPATTERN']) and not any(xPAT in host for xPAT in SESSION_TK['xPATTERN']):
            ilist.append(host)

    if SESSION_TK['bDEBUG']: # True
        print('\n**DEBUG ISE Filtered List Generated:')
        print(pp.pprint(ilist))

    return ilist
