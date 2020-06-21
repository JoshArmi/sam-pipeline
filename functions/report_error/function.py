import os

import boto3

TOPIC_ARN = os.environ['TOPIC_ARN']


def handler(event, context):
    sns = boto3.Session().client('sns')
    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject='Error Deploying Stack',
        Message=str(event),
    )
