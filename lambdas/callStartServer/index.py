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
minecraftAlarmName = os.getenv('minecraftAlarmName')
botoSession = boto3.session.Session()
awsRegion = botoSession.region_name

def _response_proxy(status_code, body, headers={}):
    if bool(headers): # Return True if dictionary is not empty
        return {"statusCode": status_code, "body": json.dumps(body), "headers": headers}
    else:
        return {"statusCode": status_code, "body": json.dumps(body)}

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

def updateAlarm(instanceId):
    logger.info("updateAlarm: " + instanceId )
    cw_client.put_metric_alarm(
        AlarmName=minecraftAlarmName,
        ActionsEnabled=True,
        AlarmActions=["arn:aws:automate:" + awsRegion + ":ec2:stop"],
        InsufficientDataActions=[],
        MetricName="NetworkOut",
        Namespace="AWS/EC2",
        Statistic="Average",
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceId
            },
        ],
        Period=300,
        EvaluationPeriods=10,
        DatapointsToAlarm=10,
        Threshold=20000,
        TreatMissingData="missing",
        ComparisonOperator="LessThanOrEqualToThreshold"   
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
    proxyRsp={}
    proxyRsp["headers"] = {
           'Content-Type': 'application/json', 
           'Access-Control-Allow-Origin': '*' 
       }

    cognitoGroups = event["requestContext"]["authorizer"]["claims"]["cognito:groups"]
    if not belongsToGroup(cognitoGroups):
        logger.warning("Not Authorized" )
        resp = {'msg': 'User not authorized to start server'}
        return _response_proxy(401,resp)

    try:                 
        if not 'body' in event:
            resp = {'result': False, 'msg': 'Invalid parameters'}
            return _response_proxy(500,resp)
        else:
            bodyJson = json.loads(event["body"])

        if 'instanceId' not in bodyJson:
            resp = { 'msg': 'Missing parameters' }
            return _response_proxy(500,resp)

        bodyJson = json.loads(event["body"])

        instanceId = bodyJson["instanceId"]

        infoRsp = getInstanceInfo(instanceId)        
        state = infoRsp["Reservations"][0]["Instances"][0]["State"]["Name"]
        launchTime = infoRsp["Reservations"][0]["Instances"][0]["LaunchTime"]

        now = datetime.now(timezone.utc)
        elapsedTime = (now - launchTime)

        updateAlarm(instanceId)

        # Invoking Step-Functions

        sfn_rsp = sfn.start_execution(
                 stateMachineArn=sftArn,
                 input='{\"instanceId\" : \"' + instanceId + '\"}' 
          )

        resp ={'isInstanceReady': isInstanceReady(instanceId), 'state': state, 'elapsedTime': int(elapsedTime.total_seconds()) }

        return _response_proxy(200,resp)
            
    except Exception as e:
        resp = {'result': False, 'msg': str(e)}
        logger.error('Something went wrong: ' + str(e))
        return _response_proxy(500,resp)
            