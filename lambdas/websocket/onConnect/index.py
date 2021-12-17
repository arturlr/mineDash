import boto3
import logging
import os
import json
import jwt
from base64 import b64encode
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddbTableName = os.getenv('connectionTableName')
dynamodb = boto3.resource('dynamodb')
ec2_client = boto3.client('ec2')
appValue = os.getenv('appValue')
ec2Filter = [{"Name":"tag:App", "Values":[ appValue ]}]

def response_proxy(statusCode, body):
        response = {}
        response["isBase64Encoded"] = False
        response["statusCode"] = statusCode
        response["headers"] = {
            'Content-Type': 'application/json', 
            'Access-Control-Allow-Origin': '*' 
        }
        if not isinstance(body, str):
            response["body"] = json.dumps(body)
        else:
            response["body"] = body
        return response

def putConnection(id, user):

    exTime = datetime.now() + timedelta(days=7)
    table = dynamodb.Table(ddbTableName)
    response = table.put_item(
       Item={
            'connectionId': id,
            'user': user,
            'expirationEpoch': round(exTime.timestamp())    
        }
    )
    return response

def handler(event, context):

    instanceInfo = ec2_client.describe_instances(Filters=ec2Filter)

    if (len(instanceInfo["Reservations"])) == 0:
        return response_proxy(500, "No instances found with App tag: " + appValue)

    instanceId = instanceInfo["Reservations"][0]["Instances"][0]["InstanceId"]    

    connectionId = event["requestContext"].get("connectionId")
    token = event.get("queryStringParameters", {}).get("token")

    if event["requestContext"]["eventType"] == "CONNECT":
        logger.info("Connect requested (CID: {}, Token: {})"\
                .format(connectionId, token))

        # Ensure connectionID and token are set
        if not connectionId:
            logger.error("Failed: connectionId value not set.")
            return response_proxy(500, "connectionId value not set.")
        if not token:
            logger.debug("Failed: token query parameter not provided.")
            return response_proxy(400, "token query parameter not provided.")

        # Verify the token
        try:
            payload = jwt.decode(token, "FAKE_SECRET", algorithms="HS256")
            logger.info("Verified JWT for '{}'".format(payload.get("username")))
        except:
            logger.debug("Failed: Token verification failed.")
            return response_proxy(400, "Token verification failed.")

        # Add connectionID to the database
        putConnection(connectionId, payload.get("username"))

        return response_proxy(200,instanceId)

    else:
        logger.error("Connection manager received unrecognized eventType '{}'"\
                .format(event["requestContext"]["eventType"]))
        return response_proxy(500, "Unrecognized eventType.")