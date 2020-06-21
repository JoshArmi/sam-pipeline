import os

import boto3

BILLING_ACCOUNT_ID = os.environ['BILLING_ACCOUNT_ID']

ROLE_NAME = os.environ['ROLE_NAME']

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
    organizations = get_session(BILLING_ACCOUNT_ID).client('organizations')
    paginator = organizations.get_paginator('list_accounts')
    accounts = []
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])
    account_ids = [account['Id'] for account in accounts]
    return {
        "accounts": {
            "list": account_ids
        }
    }
