# NewStore Authentication Manager
This integration is for the centralized management of NewStore API Credentials to help reduce the number of API Calls being made to NewStore and reduce the overall number of calls being made to the AWS Parameter Store.


## Requires
 - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
 - [newstore_connector](https://github.com/kyleranous/newstore_connector/blob/main/docs/newstore_connector.md)
 - [api_toolkit](https://github.com/kyleranous/api_toolkit/blob/main/docs/api_toolkit.md)


## QuickStart Guide

### Adding Credentials to the Parameter Store
**Headers**
```json
{
    "x-api-key": "[API KEY]"
}
```

**Body**
```json
{
    "client_id": "string",
    "client_secret": "string",
    "role": "string"
}
```
*Valid Roles as of 19DEC2023:*
 - `iam:providers:read`
 - `iam:providers:write`
 - `iam:roles:read`
 - `iam:roles:write`
 - `iam:users:read`
 - `iam:users:write`
 - `customer:profile:read`
 - `customer:profile:write`
 - `newstore:configuration:read`
 - `newstore:configuration:write`

 See the NewStore Documentation for Current Valid [Scopes](https://docs.p.newstore.partners/#/http/getting-started/newstore-rest-api/getting-started/client-credentials-grant/scopes) list.

### Getting a token from the Auth Manager

```python
import boto3


```

## Workflow
```mermaid

```

## Contributors
 - Kyle Ranous - kyle.ranous@changecx.com



## Notes
 - Tokens are valid for the duration of the TTL period (Currently 3600s from Creation), even if another token is generated with the same Client ID and Secret. Because of this, this integration does not handle potential race conditions if 2 or more integrations request tokens that need to be generated at the same time. The last token generated will be set as the cached token for subsequent calls
 - Tokens are expired in the cache ~5 minutes before the token expires in NewStore, this is to ensure lambdas have enough time to run through operations with a cached token. If writing an integration that has a potential run time greater then the cache overlap, consider authenticating with NewStore directly in the integration instead of using this authentication manager.
 - When using this auth manager do not pull tokens in a global scope. They will be pulled from the cache only on a Cold Start and Lambda's could potentially stay warm longer then the live time of the token.