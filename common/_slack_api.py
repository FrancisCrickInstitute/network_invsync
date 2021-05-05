'''
Slack API Module
'''
#!/usr/bin/env python3

__author__ = 'Guy Morrell & Paul Mahan, Francis Crick Institute, London UK'
__copyright__ = 'None. Enjoy :-)'
__credits__ = "Kees C. Bakker @ https://keestalkstech.com/2019/10/simple-python-code-to-send-message-to-slack-channel-without-packages/"

import slack # Required for Slack Post. NOTE: 'pip install slackclient'
import ssl # Required for Slack Post.
import json # Required to read Slack config file
import requests # Required for Slack Post
import pprint # Required to Pretty Print results
import ipdb # Debug. ipdb.set_trace()

from common._session_tk import Session_tk # Import Session Token Class
SESSION_TK = Session_tk() # Define object from Class

pp = pprint.PrettyPrinter(indent=4)

def slack_api(SLACK_LOG, end_time):
    '''
    Slack Post Module
    REQ: SLACK_LOG, end_time
    RTN: slack_api_status, slack_api_log
    '''
    slack_api_status = False
    slack_api_log = []

    try:
        slack_api_log.append(('%common/_slack_api', 'Slack Post Module Initialised...', 6))

        # Build our message_string to post to Slack
        message_string = ""

        for line in SLACK_LOG:
            message_string += str(line)
            message_string += '\n'

        #overflow = []
        #for k, v in git_cmd_dict.items():
        #    overflow.append({ "type": "section", "text":
        #                        {
        #                            "type": "mrkdwn",
        #                            "text": str(k)
        #                        },
        #                        "accessory": {
        #                            "type": "overflow",
        #                            "options": [
        #                                {
        #                                    "text": {
        #                                        "type": "plain_text",
        #                                        "text": str(v),
        #                                        "emoji": True
        #                                    }
        #                                }
        #                            ]
        #                        }
        #                    })

        # Build our JSON Blocks to post to Slack
        message_data = []
        message_data.append({   "type": "header",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Network InvSync Script",
                                    "emoji": True
                                    }
                            })

        message_data.append({   "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "_" + str(end_time) + "_"
                                    }
                            })

        message_data.append({   "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": message_string
                                    }
                            })

        # Call Slack Post function
        slack_post(SESSION_TK.slack_oauth_token, SESSION_TK.slack_channel, message_data)

        slack_api_log.append(('%common/_slack_api', 'Slack Post Successful.', 6))
        slack_api_status = True

    except Exception as error:
        slack_api_log.append(('%common/_slack_api', 'Slack Post Error: ' + str(error), 3))

    return slack_api_status, slack_api_log

def slack_post(slack_token, slack_channel, message_data = None):
    return requests.post(
        'https://slack.com/api/chat.postMessage',
        {
        'token': slack_token,
        'channel': slack_channel,
        'blocks': json.dumps(message_data) if message_data else None
        }).json()
