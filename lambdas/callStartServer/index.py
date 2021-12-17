import urllib
import boto3
import logging
import os
import json
import time
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
sfn = boto3.client('stepfunctions')
cw_client = boto3.client('cloudwatch')

sftArn = os.getenv('StepFunctionsArn')
cognitoAdminGroupName = os.getenv('cognitoAdminGroupName')

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

def getInstanceStatus(instanceId):
    logger.info("getInstanceStatus: " + instanceId )
    return ec2_client.describe_instance_status(
            InstanceIds=[instanceId]            
        )

def getInstanceInfo(instanceId):
    logger.info("getInstanceInfo: " + instanceId )
    return ec2_client.describe_instances(
            InstanceIds=[instanceId]            
        )

def belongsToGroup(groups):
    split_groups = groups.split(",")

    for group in split_groups:
        if (group == cognitoAdminGroupName):    
            return True
            
    return False


def isInstanceReady(instanceId):
    logger.info("isInstanceReady: " + instanceId )
    statusRsp = getInstanceStatus(instanceId)
    
    if (len(statusRsp["InstanceStatuses"])) == 0:
        return False
    
    instanceStatus = statusRsp["InstanceStatuses"][0]["InstanceStatus"]["Status"]
    systemStatus = statusRsp["InstanceStatuses"][0]["SystemStatus"]["Status"]

    if (instanceStatus == "ok" and systemStatus == "ok"):
        return True
    else:
        return False

def handler(event, context):

    cognitoGroups = event["requestContext"]["authorizer"]["claims"]["cognito:groups"]
    if not belongsToGroup(cognitoGroups):
        logger.warning("Not Authorized" )        
        return response_proxy(400,'User not authorized to start server')

    try:                 
        if not 'body' in event:            
            return response_proxy(500,"Invalid parameters")
        else:
            bodyJson = json.loads(event["body"])

        if 'instanceId' not in bodyJson:
            return response_proxy(500,'Missing parameters')

        bodyJson = json.loads(event["body"])

        instanceId = bodyJson["instanceId"]

        infoRsp = getInstanceInfo(instanceId)        
        state = infoRsp["Reservations"][0]["Instances"][0]["State"]["Name"]
        launchTime = infoRsp["Reservations"][0]["Instances"][0]["LaunchTime"]

        now = datetime.now(timezone.utc)
        elapsedTime = (now - launchTime)

        # Invoking Step-Functions

        sfn_rsp = sfn.start_execution(
                 stateMachineArn=sftArn,
                 input='{\"instanceId\" : \"' + instanceId + '\"}' 
          )

        bodyMsg = {'isInstanceReady': isInstanceReady(instanceId), 'state': state, 'elapsedTime': int(elapsedTime.total_seconds()) }
        return response_proxy(200,bodyMsg)
            
    except Exception as e:        
        logger.error('Something went wrong: ' + str(e))
        return response_proxy(500,str(e))
            