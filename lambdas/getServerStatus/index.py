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
minecraftAlarmName = os.getenv('minecraftAlarmName')
botoSession = boto3.session.Session()
awsRegion = botoSession.region_name

def response_proxy(data):
        response = {}
        response["isBase64Encoded"] = False
        response["statusCode"] = data["statusCode"]
        response["headers"] = {}
        if "headers" in data:
            response["headers"] = data["headers"]
        response["body"] = json.dumps(data["body"])
        #logger.info(response)
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

def IsInstanceReady(instanceId):
    logger.info("IsInstanceReady: " + instanceId )
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
    print(event)
    proxyRsp={}
    proxyRsp["headers"] = {
           'Content-Type': 'application/json', 
           'Access-Control-Allow-Origin': '*' 
       }
    try:                 
        if not 'body' in event:
            proxyRsp["statusCode"]=500
            proxyRsp["body"]= {'result': False, 'msg': 'Invalid parameters'}
            return response_proxy(proxyRsp)
        else:
            bodyJson = json.loads(event["body"])

        if 'instanceId' not in bodyJson:
            proxyRsp["statusCode"]=500
            proxyRsp["body"] = { 'msg': 'Missing parameters' }
            return response_proxy(proxyRsp)

        bodyJson = json.loads(event["body"])

        instanceId = bodyJson["instanceId"]

        infoRsp = getInstanceInfo(instanceId)        
        state = infoRsp["Reservations"][0]["Instances"][0]["State"]["Name"]
        launchTime = infoRsp["Reservations"][0]["Instances"][0]["LaunchTime"]

        now = datetime.now(timezone.utc)
        elapsedTime = (now - launchTime)

        updateAlarm(instanceId)

        ## Invoking Step-Functions

        sfn_rsp = sfn.start_execution(
                stateMachineArn=sftArn,
                input='{\"instanceId\" : \"' + instanceId + '\"}' 
            )

        proxyRsp["statusCode"]=200
        proxyRsp["body"]={'isInstanceReady': IsInstanceReady(instanceId), 'state': state, 'elapsedTime': int(elapsedTime.total_seconds()) }

        return response_proxy(proxyRsp)
            
    except Exception as e:
        proxyRsp={}
        proxyRsp["statusCode"]=500
        proxyRsp["body"] = {'result': False, 'msg': str(e)}
        logger.error('Something went wrong: ' + str(e))
        return response_proxy(proxyRsp)
            