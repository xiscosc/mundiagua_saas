import json

from core.aws.aws_client import create_amazon_client


def send_sns_message(topic: str, body: object):
    create_amazon_client('sns').publish(TopicArn=topic, Message=json.dumps(body))
