import json
import requests
import threading
from time import sleep
import os

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
    threads = []
    text_file = open("tickers_list.txt", "r")
    tickers = text_file.read().split('\n')
    for ticker in tickers:
        t = threading.Thread(target=bollinger_checker.check_ticker, args=(ticker,))
        threads.append(t)
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

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
