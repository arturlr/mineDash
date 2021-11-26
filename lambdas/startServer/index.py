import urllib
import boto3
import logging
import os
import json
import time
from base64 import b64encode
from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
ssm = boto3.client('ssm')

aplicationName = os.getenv('aplicationName')

def getInstanceInfo(instanceId):
    return ec2_client.describe_instances(
            InstanceIds=[instanceId]          
        )

def getInstanceStatus(instanceId):
    return ec2_client.describe_instance_status(
            InstanceIds=[instanceId]            
        )

def IsInstanceReady(InstanceId):
    statusRsp = getInstanceStatus(InstanceId)
    
    if (len(statusRsp["InstanceStatuses"])) == 0:
        return False
    
    instanceStatus = statusRsp["InstanceStatuses"][0]["InstanceStatus"]["Status"]
    systemStatus = statusRsp["InstanceStatuses"][0]["SystemStatus"]["Status"]

    if (instanceStatus == "ok" and systemStatus == "ok"):
        return True
    else:
        return False

def handler(event, context):
    try:   

        InstanceId = event["instanceId"]

        instanceInfo = getInstanceInfo(InstanceId)

        launchTime = instanceInfo["Reservations"][0]["Instances"][0]["LaunchTime"]            
        state = instanceInfo["Reservations"][0]["Instances"][0]["State"]["Name"]

        if (state == "stopped"):
            start_rsp = ec2_client.start_instances(
                InstanceIds=[ InstanceId ]
            )
            logger.info(start_rsp)

        now = datetime.now(timezone.utc)
        elapsedTime = (now - launchTime)

        return { 'isSuccessful': True, 'instanceId': InstanceId, 'isInstanceReady': IsInstanceReady(InstanceId), 'state': state, 'elapsedTime': int(elapsedTime.total_seconds()) }
            
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return {'isSuccessful': False, 'msg': str(e)}