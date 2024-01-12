"""
Tests for the Token Cache Modules
"""
import boto3
from botocore.stub import Stubber
from api_toolkit.modifiers import base64_encode

from newstore_auth_manager.aws.utils import token_cache


def test_get_cached_token_found():
    """
    Test that get_cached_token will return a token when a valid token is found in the cache
    """
    client_id = "mock"
    role = "client"
    mock_response = {
        'Item': {
            'key': {'S': base64_encode(f'{client_id}:{role}')},
            'access_token': {'S': '0123456789'},
        }
    }
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('mock-table')
    stubber = Stubber(table.meta.client)
    stubber.add_response('get_item', mock_response)
    stubber.activate()
    
    with stubber:
        result = token_cache.get_cached_token(client_id, role, "mock-table", dynamodb_client=dynamodb)
    assert result == '0123456789'

def test_get_cached_token_not_found():
    """
    Test that get_cached_token will return None when a valid token is not found in the cache
    """
    mock_response = {}
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('mock-table')
    stubber = Stubber(table.meta.client)
    stubber.add_response('get_item', mock_response)
    stubber.activate()
    
    with stubber:
        result = token_cache.get_cached_token('invalid', 'invalid', "mock-table", dynamodb_client=dynamodb)
    assert result is None
