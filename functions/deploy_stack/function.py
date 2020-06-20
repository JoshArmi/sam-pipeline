import os

import boto3

BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_PREFIX = os.environ['BUCKET_PREFIX']
REGION = os.environ['REGION']
ROLE_NAME = os.environ['ROLE_NAME']
STACK_NAME = os.environ['STACK_NAME']

session = boto3.Session()


def get_session(account_id):
    credentials = session.client('sts').assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/CrossAccountDeploy',
        RoleSessionName='CrossAccountDeploy',
    )['Credentials']
    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )


def handler(event, context):
    cross_session = get_session(event)
    cloudformation = cross_session.client('cloudformation')
    stacks = []
    paginator = cloudformation.get_paginator('list_stacks')
    for page in paginator.paginate():
        stacks.extend(page['StackSummaries'])
    stack_names = [stack['StackName'] for stack in stacks]
    if STACK_NAME in stack_names:
        cloudformation.update_stack(
            StackName=STACK_NAME,
            TemplateURL=f'https://{BUCKET_NAME}.s3-{REGION}.amazonaws.com/{BUCKET_PREFIX}'
        )
    else:
        cloudformation.create_stack(
            StackName=STACK_NAME,
            TemplateURL=f'https://{BUCKET_NAME}.s3-{REGION}.amazonaws.com/{BUCKET_PREFIX}'
        )
