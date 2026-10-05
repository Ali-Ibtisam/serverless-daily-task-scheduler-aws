import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("DailyTaskScheduler")


def decimal_converter(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        user_id = params.get("userID")

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "userID is required"}),
            }

        response = table.query(
            KeyConditionExpression=Key("userID").eq(user_id)
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response["Items"], default=decimal_converter),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)}),
        }
