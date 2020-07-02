'''
Network InvSync Python Script - Verify ISE and YAML Inventories are Synchronized.
'''
#!/usr/bin/env python3

__author__ = 'Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'


import json # Required to process *.json ISE config file and Slack Posting
import slack # Required for Slack Post. NOTE: 'pip install slackclient'
import ssl # Required for Slack Post.
import urllib3 # Required to disable SSL Warnings
import time # Require for requests delay function
import ipdb # Optional Debug. ipdb.set_trace()

from argparse import ArgumentParser # Required for Command Line Argument parsing

# Import custom modules
from modules.diffgen import diffgen
from modules.ise_api import ise_api
from modules.nornir_inv import nornir_inv
from modules.netdisco_api import netdisco_api

SESSION_TK = {}

# Custom Confiuration Files
slack_cfg_f = '../network_config/slack_network_auto.json' # Slack Post Config File.

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
        with open(slack_cfg_f) as slack_f:
            slack_settings = json.load(slack_f)

        OAUTH_TOKEN = slack_settings["OAUTH_TOKEN"]
        SLACKCHANNEL = slack_settings["CHANNEL"]

        # Establish Slack Web Client
        client = slack.WebClient(token=OAUTH_TOKEN, ssl=ssl_context)

        # Post slack_msg to Slack Channel
        client.chat_postMessage(
            channel=SLACKCHANNEL,
            blocks=message_data)

        slackpost_status = True

    except:
        slackpost_status = False

    return slackpost_status

def invsync():
    ''' MAIN FUNCTION '''

    print('\nQuerying ISE & YAML. Please Wait...')

    # Process Command Line Argument
    parser = ArgumentParser(description='Usage:')
    parser.add_argument('-i', '--ise', type=str, required=True,
                        help='ISE Admin Node FQDN')
    parser.add_argument('-s', '--slack', action='store_true',
                        help='Post to Slack [OPTIONAL]')
    parser.add_argument('-d', '--basicdebug', action='store_true',
                        help='Basic Debug')
    parser.add_argument('-v', '--verbosedebug', action='store_true',
                        help='Verbose Debug')

    arg = parser.parse_args()

    SESSION_TK['ISENODE'] = arg.ise
    SESSION_TK['SLACKPOST'] = arg.slack
    SESSION_TK['bDEBUG'] = arg.basicdebug
    SESSION_TK['vDEBUG'] = arg.verbosedebug

    # Read INVSYNC Config File
    invsync_cfg_f = 'invsync_cfg.json' # Script Config File.

    with open(invsync_cfg_f) as cfg_f:
        cfg = json.load(cfg_f)

    SESSION_TK['iPATTERN'] = cfg["iPATTERN"] # ISE Include Pattern
    SESSION_TK['xPATTERN'] = cfg["xPATTERN"] # ISE Exclude Pattern
    SESSION_TK['dSTRIP'] = cfg["dSTRIP"] # Domain Strip Patter
    SESSION_TK['mPAGES'] = cfg["mPAGES"] # ISE Maximum Number of Pages Supported. See line 129'ish
    SESSION_TK['yFILTER'] = cfg["yFILTER"] # YAML Group
    SESSION_TK['SLACKPOST'] = cfg['SLACKPOST']

    ilist = ise_api(SESSION_TK) # Query ISE API
    ylist = nornir_inv(SESSION_TK) # Query Nornir YAML Inventory
    nlist = netdisco_api(SESSION_TK) # Query NetDisco API

    xdict = {} # Use a dict to de-duplicate

    for i in ilist:
        xdict[i] = ''

    for y in ylist:
        xdict[y] = ''

    for n in nlist:
        xdict[n] = ''

    idiff = diffgen(ilist, xdict)
    ydiff = diffgen(ylist, xdict)
    ndiff = diffgen(nlist, xdict)

    # WRITE SLACK_LOG to slackpost() function for processing
    SLACK_LOG.append('Network InvSync Script Results...')
    if idiff:
        SLACK_LOG.append('\n** Missing from ISE Inventory:')
        for i in idiff:
            SLACK_LOG.append(i)

    if ydiff:
        SLACK_LOG.append('\n** Configured from YAML Inventory:')
        for y in ydiff:
            SLACK_LOG.append(y)

    if ndiff:
        SLACK_LOG.append('\n** Missing from NetMiko Inventory:')
        for n in ndiff:
            SLACK_LOG.append(n)

    if not idiff and not ydiff and not ndiff:
        SLACK_LOG.append('\n** No Difference Found Between YAML, ISE and NetMiko Inventory ' + u'\u2714')

    print(SLACK_LOG)

    if SESSION_TK['SLACKPOST'] == 1: # True
        slackpost_status = slackpost(SLACK_LOG)

if __name__ == "__main__":
    invsync()
