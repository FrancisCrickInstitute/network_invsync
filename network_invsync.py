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
import os # Required for Log File Writing
import datetime # Required for Start/ End time
import pprint # Optional to Pretty Print Responses
import ipdb # Optional Debug. ipdb.set_trace()

from argparse import ArgumentParser # Required for Command Line Argument parsing

# Import custom modules
from modules.diffgen import diffgen
from modules.ise_api import ise_api
from modules.nornir_yml import nornir_yml
from modules.netdisco_api import netdisco_api

pp = pprint.PrettyPrinter()
SESSION_TK = {}

# Custom Confiuration Files
slack_cfg_f = '../network_config/slack_network_auto.json' # Slack Post Config File.

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MASTER_LOG = [] # MASTER_LOG as list of tuples. Logs flagged with 1 to be sent to
                # slackpost.

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

def main():
    ''' MAIN FUNCTION '''

    status = False

    print('\nQuerying ISE, YAML and NetMiko Inventory. Please Wait...')

    start_time = datetime.datetime.now()

    # Process Command Line Argument
    parser = ArgumentParser(description='Usage:')
    parser.add_argument('-d', '--basicdebug', action='store_true',
                        help='Basic Debug')
    parser.add_argument('-v', '--verbosedebug', action='store_true',
                        help='Verbose Debug')
    arg = parser.parse_args()

    SESSION_TK['bDEBUG'] = arg.basicdebug
    SESSION_TK['vDEBUG'] = arg.verbosedebug

    MASTER_LOG.append(('Network InvSync Script Results...', 1))
    
    # File Method
    try:
        # Read INVSYNC Config File
        invsync_cfg_f = 'config/invsync_cfg.json' # Script Config File.

        with open(invsync_cfg_f) as cfg_f:
            cfg = json.load(cfg_f)

        SESSION_TK['iPATTERN'] = cfg["iPATTERN"] # ISE Include Pattern
        SESSION_TK['xPATTERN'] = cfg["xPATTERN"] # ISE Exclude Pattern
        SESSION_TK['dSTRIP'] = cfg["dSTRIP"] # Domain Strip Patter
        SESSION_TK['yFILTER'] = cfg["yFILTER"] # YAML Group
        SESSION_TK['SLACKPOST'] = cfg['SLACKPOST']

    except Exception as error:
        MASTER_LOG.append(('File Error: ' + str(error) + '. ' + str(invsync_cfg_f) \
            + ' missing or invalid', 1))

    # GET Query Methods
    try:
        while True:
            # ISE API Query
            ise_status, ise_log, ise_list = ise_api(SESSION_TK)

            for line in ise_log:
                MASTER_LOG.append(line)

            if not ise_status: # False
                status = False
                break

            # Nornir YAML Query
            nornir_status, nornir_log, nornir_list = nornir_yml(SESSION_TK)

            for line in nornir_log:
                MASTER_LOG.append(line)

            if not nornir_status: # False
                status = False
                break

            # NetDisco API Query
            netdisco_status, netdisco_log, netdisco_list = netdisco_api(SESSION_TK)

            for line in netdisco_log:
                MASTER_LOG.append(line)

            if not netdisco_status: # False
                status = False
                break

            status = True

            break

    except Exception as error:
        MASTER_LOG.append(('Query Error: ' + str(error), 1))

    # DIFF Method
    if status: # True

        xdict = {} # Use a dict to de-duplicate

        for i in ise_list:
            xdict[i] = ''

        for y in nornir_list:
            xdict[y] = ''

        for n in netdisco_list:
            xdict[n] = ''

        # xdict {} should now contain all nodes across all methods

        # Call diffgen Module
        idiff = diffgen(ise_list, xdict)
        ydiff = diffgen(nornir_list, xdict)
        ndiff = diffgen(netdisco_list, xdict)

        # WRITE SLACK_LOG to slackpost() function for processing
        if idiff:
            MASTER_LOG.append(('\n** Missing from ISE Inventory:', 1))
            for i in idiff:
                MASTER.append((i, 1))

        if ydiff:
            MASTER_LOG.append(('\n** Missing from YAML Inventory:', 1))
            for y in ydiff:
                MASTER_LOG.append((y, 1))

        if ndiff:
            MASTER_LOG.append(('\n** Missing from NetDisco Inventory:', 1))
            for n in ndiff:
                MASTER_LOG.append((n, 1))

        if not idiff and not ydiff and not ndiff:
            MASTER_LOG.append(('\n** No Difference Found Between YAML, ISE and NetDisco Inventory ' + u'\u2714', 1))

    # WRITE MASTER_LOG to file
    # Make a folder in script working directory to store results
    logdir = '../LOGS/network_invsync_log/'
    # Modify the time stamp to not contain special characters (: & /)
    log_time = start_time.strftime('%Y_%m_%d_%H_%M_%S')

    try:
        os.makedirs(logdir)
    except FileExistsError:
        pass # Folder exisits so nothing to do

    logfile = open(logdir + str(log_time) + '.log', 'w')

    for line in MASTER_LOG:
        logfile.write(str(line[0]) + '\n')

    logfile.close()

    for line in MASTER_LOG:
        print(line)

    print('MASTER_LOG saved to ' + str(logfile))

    # POST to Slack
    if SESSION_TK['SLACKPOST'] == 1: # True
        SLACK_LOG = []
        for line in MASTER_LOG:
            if line[1] == 1:
                SLACK_LOG.append(line[0])

        slackpost_status = slackpost(SLACK_LOG)

if __name__ == "__main__":
    main()
