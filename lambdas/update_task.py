import json
import boto3
from decimal import Decimal

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
        if "body" in event and event["body"]:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event

        user_id = body["userID"]
        task_id = body["taskID"]

        update_fields = {
            "taskName": body.get("taskName"),
            "taskDate": body.get("taskDate"),
            "startTime": body.get("startTime"),
            "endTime": body.get("endTime"),
            "durationMinutes": body.get("durationMinutes"),
            "priority": body.get("priority"),
            "status": body.get("status"),
            "fixedEvent": body.get("fixedEvent"),
            "reminderTime": body.get("reminderTime"),
        }

        update_expression = []
        expression_values = {}
        expression_names = {}

        for key, value in update_fields.items():
            if value is not None:
                update_expression.append(f"#{key} = :{key}")
                expression_names[f"#{key}"] = key
                expression_values[f":{key}"] = value

        if not update_expression:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No fields provided to update"}),
            }

        response = table.update_item(
            Key={"userID": user_id, "taskID": task_id},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW",
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "Task updated successfully",
                    "task": response["Attributes"],
                },
                default=decimal_converter,
            ),
        }

    except KeyError as error:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Missing required field: {str(error)}"}),
        }

    except Exception as error:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)}),
        }
