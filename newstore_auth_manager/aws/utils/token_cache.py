"""
Module containing functions to fetch and write credentials to the 
NewStore Token Cache DynamoDB Table
"""

import logging
import time
import boto3
from api_toolkit.modifiers import base64_encode

# Setup Logging
LOGGER = logging.getLogger(__name__)


def get_cached_token(client_id, role, dynamodb_table_name, dynamodb_client=None):
    """
    Taken in the client_id and Role, Encode them into the key,
    then search the DynamoDB Table for a cached token.
    dynamodb_client is used for testing purposes
    """
    key = base64_encode(f"{client_id}:{role}") if role else base64_encode(f"{client_id}:none")

    # Create a DynamoDB resource
    if not dynamodb_client:
        dynamodb = boto3.resource('dynamodb')
    else:
        dynamodb = dynamodb_client

    table = dynamodb.Table(dynamodb_table_name)

    response = table.get_item(
        Key={
            'key': key
        }
    )
    return response['Item']['access_token'] if 'Item' in response else None


def cache_token(*args, **kwargs):
    """
    Caches the token in the Token Cache Table
    Args:
     - client_id
     - role
     - access_token
     - token_ttl,
     - token_table
    """
    if args[1] is None:
        key = base64_encode(f"{args[0]}:none")
    else:
        key = base64_encode(f"{args[0]}:{args[1]}")
    LOGGER.info(f"Key Type: {type(key)}")
    access_token = args[2]
    token_table = args[4]
    token_ttl = args[3]

    cache_ttl = int(time.time()) + token_ttl - 300

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(token_table)

    table.put_item(
        Item={
            'key': key,
            'access_token': access_token,
            'cache_ttl': str(cache_ttl)
        }
    )
