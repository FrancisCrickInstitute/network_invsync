'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import requests # Required for API POST
import xmltodict # Requird to convert POST XML response to DICT
import pprint # Optional to Pretty Print Responses
import json # Required to process *.json ISE config file and Slack Posting
import slack # Required for Slack Post. NOTE: 'pip install slackclient'
import ssl # Required for Slack Post.
import urllib3 # Required to disable SSL Warnings
import time # Require for requests delay function
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

SLACK_LOG = []

def slackpost(SLACK_LOG):
    ''' Post to Slack Function '''

    try:
        # Comment out:
        #
        # for line in SLACK_LOG:
        #    post_to_slack(line)
        #
        # At the end of the main function to disable!

        # Build our message_string to post to Slack
        message_string = ""

        for line in SLACK_LOG:
            message_string += str(line)
            message_string += '\n'

        # Build our JSON payload to post to Slack
        message_data = []
        message_data.append({"type": "section", "text": {"type": "mrkdwn", "text": message_string}})

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Read *.json config for required tokens
        with open("../network_config/slack_network_auto.json") as slack_f:
            slack_settings = json.load(slack_f)

        OATH = slack_settings["OAUTH_TOKEN"]
        SLACKCHANNEL = slack_settings["CHANNEL"]

        # Establish Slack Web Client
        client = slack.WebClient(token=OATH, ssl=ssl_context)

        # Post slack_msg to Slack Channel
        client.chat_postMessage(
            channel=SLACKCHANNEL,
            blocks=message_data)

        slackpost_status = True

    except:
        slackpost_status = False

    return slackpost_status

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

    MAX_PAGES = 2

    for page in range(MAX_PAGES):

        url = "https://" + str(ISENODE) + ":9060/ers/config/networkdevice?size=100&page=" + str(page+1)

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

    # print(PP.pprint(xdoc))

    # Parse through XTVAL module to extract required values
    # ids = xtval(xdoc, '@id')
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

    # WRITE SLACK_LOG to slackpost() function for processing
    SLACK_LOG.append('Network InvSync Script Results...')
    if idiff:
        SLACK_LOG.append('\n** Configured on ISE but not in YAML:')
        for i in idiff:
            SLACK_LOG.append(i)
    if ydiff:
        SLACK_LOG.append('\n** Configured in YAML but not on ISE:')
        for y in ydiff:
            SLACK_LOG.append(y)

    if not idiff and not ydiff:
        SLACK_LOG.append('\n** No Difference Found Between YAML and ISE Inventory ' + u'\u2714')

    print(SLACK_LOG)
    slackpost_status = slackpost(SLACK_LOG)

if __name__ == "__main__":
    main()
