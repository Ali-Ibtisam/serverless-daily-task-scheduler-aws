import json
import boto3
import uuid
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("DailyTaskScheduler")
scheduler = boto3.client("scheduler")

REMINDER_FUNCTION_ARN = os.environ["REMINDER_FUNCTION_ARN"]
SCHEDULER_ROLE_ARN = os.environ["SCHEDULER_ROLE_ARN"]


def lambda_handler(event, context):
    try:
        if "body" in event and event["body"]:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event

        task_id = str(uuid.uuid4())

        item = {
            "userID": body["userID"],
            "taskID": task_id,
            "taskName": body["taskName"],
            "taskDate": body["taskDate"],
            "startTime": body["startTime"],
            "endTime": body["endTime"],
            "durationMinutes": body["durationMinutes"],
            "priority": body["priority"],
            "status": "PENDING",
            "fixedEvent": body["fixedEvent"],
            "reminderTime": body["reminderTime"],
        }

        table.put_item(Item=item)

        schedule_name = f"reminder-{task_id}"
        schedule_expression = f"at({body['taskDate']}T{body['reminderTime']}:00)"

        reminder_payload = {
            "userID": body["userID"],
            "taskID": task_id,
            "taskName": body["taskName"],
            "startTime": body["startTime"],
        }

        scheduler.create_schedule(
            Name=schedule_name,
            ScheduleExpression=schedule_expression,
            ScheduleExpressionTimezone="Asia/Karachi",
            FlexibleTimeWindow={"Mode": "OFF"},
            ActionAfterCompletion="DELETE",
            Target={
                "Arn": REMINDER_FUNCTION_ARN,
                "RoleArn": SCHEDULER_ROLE_ARN,
                "Input": json.dumps(reminder_payload),
            },
        )

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Task and reminder created successfully",
                "taskID": task_id,
                "scheduleName": schedule_name,
            }),
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
