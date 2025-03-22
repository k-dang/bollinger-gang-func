import json
import requests
from time import sleep
import os
from concurrent.futures import ThreadPoolExecutor

# internal modules
import discord_helpers as dh
from bollingerchecker import BollingerChecker

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    # discord webhook url
    webhook_url = os.environ.get('webhook_url')

    # headers for discord webhook
    headers = {'Content-Type': 'application/json'}

    bollinger_checker = BollingerChecker()
    tickers = open("tickers_list.txt", "r").read().split('\n')

    # Use ThreadPoolExecutor with max 5 threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(bollinger_checker.check_ticker, tickers)

    for item in bollinger_checker.list_of_potentials:
        # construct webhook body
        webhook_body = dh.get_discord_webhook_body()
        webhook_body['embeds'][0]['fields'] = item
        requests.post(url=webhook_url, data=json.dumps(webhook_body), headers=headers)
        sleep(0.5)

    if not bollinger_checker.list_of_potentials:
        webhook_body = dh.get_empty_discord_webhook_body("Nothing passed today")
        requests.post(url=webhook_url, data=json.dumps(webhook_body), headers=headers)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }
