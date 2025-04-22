import os
import logging
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional
import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel("INFO")
dynamodb = boto3.resource("dynamodb")
purchases_table = dynamodb.Table(os.environ.get("PURCHASES_TABLE_NAME"))

class EventModel(BaseModel):
    action: str
    customer_email: Optional[EmailStr] = None

def get_purchase_details(event):
    logger.info(event)
    email = event.get("customer_email", None)
    logger.info(email)
    if not email:
        logger.info("Missing customer email")
        return None
    
    try:
        response = purchases_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('customer_email').eq(email)
        )
        return response.get('Items', [])
    except Exception as e:
        logger.exception("Failed to query purchases")
        return str(e)

def get_all_purchases(event):
    logger.info(event)
    try:
        response = purchases_table.scan()
        purchases = response.get('Items', [])
        return purchases
    except Exception as e:
        logger.exception("Failed to scan purchases table")
        return str(e)

available_actions = {
    'get_purchase_details': get_purchase_details,
    'get_all_purchases': get_all_purchases,
}

def lambda_handler(event, _):
    logger.info(event)
    try:
        validated_event = EventModel(**event)
    except ValidationError as e:
        logger.error(f"Event validation failed: {e}")
        return {"error": "Invalid event format", "details": e.errors()}
    
    action = event.get('action')
    if not action:
        logger.info("Action is unknown")
        return None
    result = available_actions[event['action']](event)
    return result
 