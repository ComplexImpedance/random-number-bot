#!/usr/bin/env python3.6

# =============================================================================
# IMPORTS
# =============================================================================
import praw
import re
import time
import logging
import os
import smtplib
import json
import requests
import uuid
# =============================================================================
# GLOBALS
# =============================================================================

VERSION = '1.1.3'

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('RandomNumberBot')
logger.setLevel(logging.INFO)

random_number_reply = """#{command_message} {random_numbers}

Paste the following values into their respective fields on the [random.org verify page](https://api.random.org/verify) to verify the winner.

**Random:**

{verification_random}

**Signature:**

{verification_signature}

**This bot is maintained and hosted by {dev_name}. View the {version} source code on [github](https://github.com/ComplexImpedance/random-number-bot)**"""


def send_dev_pm(reddit, user_name, subject, body):
    """
    Sends Reddit PM to DEV_USER_NAME
    :param subject: subject of PM
    :param body: body of PM
    """
    reddit.redditor(user_name).message(subject, body)

def check_mentions(reddit, bot_username, dev_name, api_key, api_url):
    for mention in reddit.inbox.unread(limit=None):
        #Mark Read first in case there is an error we dont want to keep trying to process it
        mention.mark_read()
        process_mention(mention, bot_username, dev_name, api_key, api_url)
        #break after first item so we don't go over timeout
        break

def getRdoRequest(num_randoms, num_slots, api_key):
    return {'jsonrpc': '2.0', 'method': 'generateSignedIntegers',
    'params': {'apiKey': api_key, 'n': num_randoms, 'min': 1, 'max': num_slots, 'replacement': False},
    'id': uuid.uuid4().hex}


def process_mention(mention, bot_username, dev_name, api_key, api_url):
    command_regex = r'^([ ]+)?/?u/{bot_username}[ ]+(?P<param_1>[\d]+)([ ]+(?P<param_2>[\d]+))?([ ]+)?$'.format(bot_username=bot_username)
    match = re.search(command_regex, mention.body, re.IGNORECASE)

    command_message = ''
    num_randoms = 0
    num_slots = 0

    if match and match.group("param_1") and match.group("param_2"):
        command_message = 'Your escrow spots:'
        num_randoms = int(match.group("param_1"))
        num_slots = int(match.group("param_2"))
        if(num_randoms > num_slots):
            num_randoms, num_slots = num_slots, num_randoms
    elif match and match.group("param_1"):
        command_message = 'The winner is:'
        num_randoms = 1
        num_slots = int(match.group("param_1"))
    else:
        #could be a normal mention not a command so just return
        return

    #response = random_org_client.generate_signed_integers(num_randoms, 1, num_slots, replacement=False)
    request = getRdoRequest(num_randoms, num_slots, api_key)

    responseData = {}
    try:
        HTTP_TIMEOUT = 3.0
        response = requests.post(api_url,
                data=json.dumps(request),
                headers={'content-type': 'application/json'},
                timeout=HTTP_TIMEOUT)
        responseData = response.json()


    except Exception as err:
        logger.exception('Error calling RandomOrg API')

    if(responseData and 'result' in responseData):
        responseResult = responseData['result']
        mention.reply(random_number_reply.format(command_message = command_message,
                                    random_numbers = str(responseResult['random']['data']),
                                    verification_random = get_verification_random(responseResult['random']),
                                    verification_signature = str(responseResult['signature']),
                                    version = VERSION,
                                    dev_name = dev_name))
    else:
        logger.error('Error getting random nums {num_randoms} {num_slots}'.format(num_randoms=num_randoms, num_slots=num_slots))
        logger.error(str(response))
        try:
            mention.reply('There was an error getting your random numbers from random.org. Please try again.')
            send_dev_pm(reddit, dev_name, "Error getting random nums", 'Error getting random nums {num_randoms} {num_slots}'.format(num_randoms=num_randoms, num_slots=num_slots))
        except Exception as err:
            logger.exception("Unknown error sending dev pm")

def get_verification_random(random_dict):
    return '{{"method": "generateSignedIntegers",'\
    '"hashedApiKey": "{hashedApiKey}",'\
    '"n": {n},'\
    '"min": {min},'\
    '"max": {max},'\
    '"replacement": {replacement},'\
    '"base": {base},'\
    '"data": {data},'\
    '"completionTime": "{completionTime}",'\
    '"serialNumber": {serialNumber}}}'.format(
        hashedApiKey = random_dict['hashedApiKey'],
        n = random_dict['n'],
        min = random_dict['min'],
        max = random_dict['max'],
        replacement = str(random_dict['replacement']).lower(),
        base = random_dict['base'],
        data = random_dict['data'],
        completionTime = random_dict['completionTime'],
        serialNumber = random_dict['serialNumber']
    )

# =============================================================================
# MAIN
# =============================================================================

def call_the_bot(event, context):
    #get env variables
    try:
        bot_username = os.environ["username"]
        bot_password = os.environ["password"]
        client_id = os.environ["client_id"]
        client_secret = os.environ["client_secret"]

        DEV_USER_NAME = os.environ["dev_user"]
        RANDOM_ORG_API_KEY = os.environ["random_org_api_key"]
        RANDOM_ORG_API_URL = 'https://api.random.org/json-rpc/1/invoke'

    except KeyError:
        return "Please set the environment variables"


    #Reddit info
    reddit = praw.Reddit(client_id=client_id,
                        client_secret=client_secret,
                        password=bot_password,
                        user_agent='random_number_bot by /u/BoyAndHisBlob',
                        username=bot_username)
    #random_org_client = RandomOrgClient(RANDOM_ORG_API_KEY, blocking_timeout=3.0, http_timeout=3.0)

    try:
        check_mentions(reddit, bot_username, DEV_USER_NAME, RANDOM_ORG_API_KEY, RANDOM_ORG_API_URL)
    except Exception as err:
        logger.exception("Unknown Exception in check_mentions")
        try:
            send_dev_pm(reddit, "Unknown Exception in Main Loop", "Error: {exception}".format(exception = str(err)))
        except Exception as err:
            logger.exception("Unknown error sending dev pm")
    return "fin"
