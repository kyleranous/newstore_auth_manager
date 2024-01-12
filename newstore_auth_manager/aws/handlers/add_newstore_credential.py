"""
Module for creating or udating a New Store credential
"""
import os
import logging
import json
import boto3


#Setup Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_LEVEL = logging.getLevelName(LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)

# Get Authentication URL SETTINGS
TENANT = os.environ.get('TENANT')

# Get Auth Lambda Name
AUTH_LAMBDA = os.environ.get('AUTH_LAMBDA')

def handler(event, _context):
    """
    Event Handler for Adding NewStore Credentials
    Expected Payload:
    {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "role": "role"
    }
    """
    LOGGER.info("New Credentials Recieved")
    LOGGER.info(f"Event: {event}")
    event_dict = json.loads(event['body-json']) if isinstance(event, str) else event['body-json']
    try:
        validation = validate_credentials(event_dict['client_id'],
                                          event_dict['client_secret'],
                                          event_dict['role'])
    except Exception as error:
        LOGGER.error(f"Error: {error}")
        return {'statusCode': 500,
                'body': json.dumps(str(error))}
    
    LOGGER.info(f"Validation Response: {validation}")

    return {'statusCode': 200 }

def validate_credentials(client_id, client_secret, role):
    """
    Validate that the credentials are valid with NewStore
    using the NewStore Credential Manager
    """

    lambda_client = boto3.client('lambda')
    request_payload = {
        'client_id': client_id,
        'role': role,
        'client_secret': client_secret,
        'request_from': 'add_newstore_credential'
    }
    response = lambda_client.invoke(
        FunctionName=AUTH_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps(request_payload)
    )
    response_token = json.loads(response['Payload'].read().decode("utf-8"))
    if 'error' in response_token:
        error_msg = json.loads(response_token)['error']
        raise Exception(f"Error: {json.loads(error_msg)}")
    LOGGER.info(f"Response: {response_token}")
    return response
