import boto3
import json
import logging
import os
import urllib.request
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

logger = logging.getLogger("handler_logger")
logger.setLevel(logging.INFO)

connectionTableName = os.getenv('connectionTableName')
aplicationName = os.getenv('aplicationName')
dynamodb = boto3.resource("dynamodb")
ssm = boto3.client('ssm')
botoSession = boto3.session.Session()
awsRegion = botoSession.region_name
ssm_cognito_key= "/amplify/" + aplicationName + "/cognitoPoolId"
userpool_id = ssm.get_parameter(Name=ssm_cognito_key)
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(awsRegion, userpool_id)

# download the key
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}

def _is_token_valid(token):
    # https://github.com/awslabs/aws-support-tools/tree/master/Cognito/decode-verify-jwt
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        logger.error('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        logger.error('Signature verification failed')
        return False
    logger.info('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        logger.error('Token is expired')
        return False
    # now we can use the claims
    logger.info(claims)
    return True

def handler(event, context):
    """
    Handles connecting and disconnecting for the Websocket.
    Connect verifes the passed in token, and if successful,
    adds the connectionID to the database.
    Disconnect removes the connectionID from the database.
    """
    connectionID = event["requestContext"].get("connectionId")
    token = event.get("queryStringParameters", {}).get("token")

    if event["requestContext"]["eventType"] == "CONNECT":
        logger.info("Connect requested (CID: {}, Token: {})"\
                .format(connectionID, token))

        # Ensure connectionID and token are set
        if not connectionID:
            logger.error("Failed: connectionId value not set.")
            return _get_response(500, "connectionId value not set.")
        if not token:
            logger.debug("Failed: token query parameter not provided.")
            return _get_response(400, "token query parameter not provided.")

        # Verify the token
        if not _is_token_valid(token):
            logger.debug("Failed: Token verification failed.")
            return _get_response(400, "Token verification failed.")

        # Add connectionID to the database
        table = dynamodb.Table(connectionTableName)
        expiration = int(time.time()) + 172800 # 48h expiration time
        table.put_item(
            Item={
                "ConnectionID": connectionID,
                "expiration": expiration
                }
            )
        return _get_response(200, "Connect successful.")

    elif event["requestContext"]["eventType"] == "DISCONNECT":
        logger.info("Disconnect requested (CID: {})".format(connectionID))

        # Ensure connectionID is set
        if not connectionID:
            logger.error("Failed: connectionId value not set.")
            return _get_response(500, "connectionId value not set.")

        # Remove the connectionID from the database
        table = dynamodb.Table(connectionTableName)
        table.delete_item(Key={"ConnectionID": connectionID})
        return _get_response(200, "Disconnect successful.")

    else:
        logger.error("Connection manager received unrecognized eventType '{}'"\
                .format(event["requestContext"]["eventType"]))
        return _get_response(500, "Unrecognized eventType.")