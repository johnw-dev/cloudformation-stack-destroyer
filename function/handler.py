import boto3
import logging
import sys
import os

import sys


from function.destroyer import Destroyer

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EXPIRY_TAG = os.environ["STACK_EXPIRY_TAG"]
RETENTION_TAG = os.environ["STACK_RETENTION_TAG"]
cloudformation = boto3.client("cloudformation")
destroyer = Destroyer(
    cloudformation, expiry_tag=EXPIRY_TAG, retention_tag=RETENTION_TAG
)


def handler(event, context):
    print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
    ### entrypoint ###
    logger.info("started")
    response = destroyer.delete_all_stacks()
    logger.info(response)
    return response
