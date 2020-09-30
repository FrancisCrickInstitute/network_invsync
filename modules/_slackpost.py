'''
Slack Post Module
'''
#!/usr/bin/env python3

__author__ = 'Guy Morrell, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'

import slack # Required for Slack Post. NOTE: 'pip install slackclient'
import ssl # Required for Slack Post.
import json # Required to read Slack config file
import ipdb # Optional Debug. ipdb.set_trace()

def slackpost(SLACK_LOG):
    ''' Post to Slack Function '''

    try:
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

        # Custom Confiuration Files
        slack_cfg_f = '../network_config/network_slack.json' # Slack Post Config File.

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
