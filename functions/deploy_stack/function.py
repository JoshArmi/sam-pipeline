import os

import boto3
from botocore.exceptions import ClientError, ValidationError

BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PREFIX = os.environ['BUCKET_PREFIX']
REGION = os.environ['REGION']
ROLE_NAME = os.environ['ROLE_NAME']
STACK_NAME = os.environ['STACK_NAME']

session = boto3.Session()


def get_session(account_id):
    credentials = session.client('sts').assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/{ROLE_NAME}',
        RoleSessionName=f'{ROLE_NAME}',
    )['Credentials']
    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )


def handler(event, context):
    print(event)
    cross_session = get_session(event)
    cloudformation = cross_session.client('cloudformation')
    stacks = []
    paginator = cloudformation.get_paginator('list_stacks')
    for page in paginator.paginate():
        stacks.extend(page['StackSummaries'])
    stack_names = [stack['StackName'] for stack in stacks]
    if STACK_NAME in stack_names:
        try:
            cloudformation.update_stack(
                StackName=STACK_NAME,
                TemplateURL=f'https://{BUCKET_NAME}.s3-{REGION}.amazonaws.com/{BUCKET_PREFIX}'
            )
        except ClientError as err:
            print(err)
            if 'No updates are to be performed' not in str(err):
                raise err
            raise Exception({"Error": err, "Account": event})
    else:
        cloudformation.create_stack(
            StackName=STACK_NAME,
            TemplateURL=f'https://{BUCKET_NAME}.s3-{REGION}.amazonaws.com/{BUCKET_PREFIX}'
        )
