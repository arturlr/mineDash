import urllib
import boto3
import logging
import os
import json
import time
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
ssm = boto3.client('ssm')

minecraftDocumentName = os.getenv('minecraftDocument')

def handler(event, context):
    try:   
        
        ssm_rsp = ssm.send_command(
            InstanceIds=[event["instanceId"]],
            DocumentName=minecraftDocumentName
        )
        
        logger.info(ssm_rsp)

        # Save CommandID in a DDb table to submit the result via websocket

        return { 'result': 'Succeed', 'id': ssm_rsp["Command"]["CommandId"] }

    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return {'result': 'Fail', 'msg': str(e)}