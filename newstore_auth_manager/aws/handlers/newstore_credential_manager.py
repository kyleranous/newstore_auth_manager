"""
Module for the New Store Credential Manager
"""

import os
import logging
import json
import boto3
from newstore_connector import NewStoreConnector


from newstore_auth_manager.aws.utils import token_cache


# Load cached Settings
#Setup Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_LEVEL = logging.getLevelName(LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)

# Get Authentication URL SETTINGS
TENANT = os.environ.get('TENANT')

# Check for an overridden DynamoDB Table Name
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')


def handler(event, _context):
    """
    Event Handler for newstore_credential_manager
    Expected Event Payload:
    {
        "client_id": "client_id",
        "role": "role",
        "request_from": "Lambda Name Requesting the data"
    }
    """
    event_dict = json.loads(event) if isinstance(event, str) else event
    LOGGER.info(f"Authentication request recieved from {event_dict['request_from']}")

    # Checking for client_secret so this can be used to validate new credentials
    response = get_access_token(event_dict['client_id'],
                                event_dict.get('role'),
                                client_secret=event_dict.get('client_secret', None))

    return response


def get_access_token(client_id, role, client_secret):
    """
    Workflow for finding or initiating an access token for a client_id
    """
    token_table = DYNAMODB_TABLE_NAME or "newstore-token-cache"
    # If client_secret is not passed, check for a cached token then stored secret
    # This is added to allow this lambda to be used to validate credentials for the add_newstore_credential lambda
    if client_secret is None:
        # Check if the client_id and role have a cached access token
        cached_token = token_cache.get_cached_token(client_id, role, token_table)

        # If not, Retrieve client_secret from the Secrets Manager
        if cached_token:
            LOGGER.info("Found a cached token")
            return cached_token
    
        ## Get a New Access Token from NewStore
        # Check for a stored client_secret
        try:
            ssm = boto3.client('ssm')
            param_path = f"/newstore/creds/{client_id}"
            client_secret = ssm.get_parameter(Name=param_path, WithDecryption=True)['Parameter']['Value']
        except Exception as err:
            LOGGER.info(f'Error retrieving secret from ssm for {client_id}: {err}')
            return json.dumps({"error": f"Error retrieving secret from ssm for {client_id}: {err}"})

    try:
        newstore_connector = get_newstore_token(client_id, client_secret, role)
    
    except:
        LOGGER.info(f'Error getting Token from NewStore for {client_id}')
        return json.dumps({"error": f"Error getting Token from NewStore for {client_id}"})
    
    ## Cache the new access token in the DynamoDB Database
    token_cache.cache_token(client_id,
                            role,
                            newstore_connector.token,
                            newstore_connector.token_ttl,
                            token_table) 

    return newstore_connector.token


def get_newstore_token(client_id, client_secret, role):
    """
    Get a New Access Token from NewStore
    """
    connector_params = {
        'tenant': TENANT,
        'client_id': client_id,
        'client_secret': client_secret,
        'role': role
    }
    newstore_connector = NewStoreConnector(**connector_params)

    return newstore_connector