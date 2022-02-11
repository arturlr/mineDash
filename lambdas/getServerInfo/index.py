import urllib
import boto3
import logging
import os
import json
import time
from base64 import b64encode
from datetime import date, datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
cw_client = boto3.client('cloudwatch')
ct_client = boto3.client('cloudtrail')
sfn = boto3.client('stepfunctions')
ce_client = boto3.client('ce')
ENCODING = 'utf-8'

sftArn = os.getenv('StepFunctionsArn')
aplicationName = os.getenv('aplicationName')
appValue = os.getenv('appValue')

filters = [{"Name":"tag:App", "Values":[ appValue ]}]

def _response_proxy(status_code, body, headers={}):
    if bool(headers): # Return True if dictionary is not empty
        return {"statusCode": status_code, "body": json.dumps(body), "headers": headers}
    else:
        return {"statusCode": status_code, "body": json.dumps(body)}

def getUsageCost(instanceId):
    first_day_of_the_month=date.today().replace(day=1)
    ending = date.today()
    usageQuantity = None
    unblendedCost = None
    request = {
            "TimePeriod": {
                "Start": first_day_of_the_month.strftime("%Y-%m-%d"),
                "End": ending.strftime("%Y-%m-%d")
            },
            "Filter": {
                "And": [
                    {
                        "Dimensions": {
                            "Key": "USAGE_TYPE_GROUP",
                            "Values": [
                                "EC2: Running Hours"
                            ]
                        }
                    },
                    {
                        "Tags": {
                            "Key": "App",
                            "Values": [ appValue
                            ]
                        }
                    }
                ]
            },
            "Granularity": "MONTHLY",
            "Metrics": [
                "UnblendedCost",
                "UsageQuantity"
            ]
        }
    response = ce_client.get_cost_and_usage(**request)
    for results in response['ResultsByTime']:  
        unblendedCost = float(results['Total']['UnblendedCost']['Amount'])
        usageQuantity = float(results['Total']['UsageQuantity']['Amount'])

    return { "unblendedCost": round(unblendedCost,1), "usageQuantity": round(usageQuantity,1) }

def getMetricData(instanceId,metricName,unit,statType):
    cdata = []
    four_hours_before=datetime.utcnow() - timedelta(hours=4)

    rsp = cw_client.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName=metricName,
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceId
            }
        ],
        StartTime=four_hours_before,
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=[statType],
        Unit=unit
    )

    if len(rsp["Datapoints"]) == 0:
        return None
    else:
        for rec in rsp["Datapoints"]:
            cdata.append({'x': round(rec["Average"], 2), 'y': rec["Timestamp"].strftime("%Y/%m/%dT%H:%M:%S")})
            
        return sorted(cdata, key=lambda k: k['y'])

def getInstanceInfo():
    return ec2_client.describe_instances(
            Filters=filters            
        )

def getInstanceStatus(instanceId):
    return ec2_client.describe_instance_status(
            InstanceIds=[instanceId]            
        )

def getCloudTailEvents(instanceId, eventValue):
    eventList = []

    paginator = ct_client.get_paginator('lookup_events')
    
    StartingToken = None
    
    page_iterator = paginator.paginate(
    	LookupAttributes=[{'AttributeKey':'EventName','AttributeValue': eventValue}],
    	PaginationConfig={'PageSize':50, 'StartingToken':StartingToken })
    for page in page_iterator:
        for event in page['Events']:
            if event['Resources'][0]["ResourceName"] == instanceId:
                eventList.append(event['EventTime'].strftime("%m/%d/%Y - %H:%M:%S") + '#' + event['Username'] + '#' + eventValue)
                
    return eventList


def getInstanceDetails(InstanceId):
    statusRsp = getInstanceStatus(InstanceId)
        
    if (len(statusRsp["InstanceStatuses"])) == 0:
        return { 'instanceStatus': "Fail", 'systemStatus': "Fail" }
    
    instanceStatus = statusRsp["InstanceStatuses"][0]["InstanceStatus"]["Status"]
    systemStatus = statusRsp["InstanceStatuses"][0]["SystemStatus"]["Status"]
    
    logger.info('instanceStatus: ' + instanceStatus)
    logger.info('systemStatus:' + systemStatus)
        
    return { 'instanceStatus': instanceStatus, 'systemStatus': systemStatus }


def handler(event, context):
    headers = {
           'Content-Type': 'application/json', 
           'Access-Control-Allow-Origin': '*' }
    try:   
        instanceInfo = getInstanceInfo()
        
        if (len(instanceInfo["Reservations"])) == 0:
            resp = { 'result': False, 'msg': "No Instances Found" }
            return _response_proxy(500, resp, headers)
            
        instanceName = instanceInfo["Reservations"][0]["Instances"][0]["InstanceId"]
        instanceType = instanceInfo["Reservations"][0]["Instances"][0]["InstanceType"]
        launchTime = instanceInfo["Reservations"][0]["Instances"][0]["LaunchTime"]
        if "Association" in instanceInfo["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]:
            publicIp = instanceInfo["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["Association"]["PublicIp"]
        else:
            publicIp = "none"
            
        state = instanceInfo["Reservations"][0]["Instances"][0]["State"]["Name"]

        instanceDetails = getInstanceDetails(instanceName)

        payload = {}
        payload["instanceName"] = instanceName
        payload["instanceType"] = instanceType
        payload["state"] = state
        payload["launchTime"] = launchTime.strftime("%m/%d/%Y - %H:%M:%S")
        payload["publicIp"] = publicIp
        payload["instanceStatus"] = instanceDetails["instanceStatus"].lower()
        payload["systemStatus"] = instanceDetails["systemStatus"].lower()
        payload["cost"] = getUsageCost(instanceName)
        payload["metrics"] = { 
            'networkOut' : getMetricData(instanceName,'NetworkOut','Bytes','Average'),
            'cpuUtilization' : getMetricData(instanceName,'CPUUtilization','Percent','Average')
            }
        startEvents = getCloudTailEvents(instanceName, "StartInstances")
        stopEvents = getCloudTailEvents(instanceName, "StopInstances")
        payload["timeLine"] = sorted(startEvents + stopEvents, reverse = True)

        return _response_proxy(200,payload)
            
    except Exception as e:
        resp = {'result': False, 'msg': str(e)}
        logger.error('Something went wrong: ' + str(e))
        return _response_proxy(500,resp)