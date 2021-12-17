import urllib
import boto3
import logging
import os
import json
import time
from base64 import b64encode
from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddbTableName = os.getenv('connectionTableName')
dynamodb = boto3.resource('dynamodb')


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

def deleteConnection(id):

    exTime = datetime.now() + timedelta(days=7)
    table = dynamodb.Table(ddbTableName)
    response = table.delete(
       Item={
            'connectionId': id  
        }
    )
    return response

def handler(event, context):
    
    connectionId = event["requestContext"].get("connectionId")
    deleteConnection(connectionId)

    return response_proxy(200,"Disconnect successful.")