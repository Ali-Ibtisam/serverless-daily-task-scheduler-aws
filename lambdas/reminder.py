import json
import boto3
import os

sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):
    try:
        user_id = event.get("userID", "Unknown User")
        task_name = event.get("taskName", "Unknown Task")
        start_time = event.get("startTime", "Unknown Time")

        message = (
            "Daily Task Reminder\n\n"
            f"Task: {task_name}\n"
            f"Start Time: {start_time}\n\n"
            "Your task is starting soon."
        )

        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Daily Task Reminder",
            Message=message,
        )

        print("===== TASK REMINDER =====")
        print(f"User: {user_id}")
        print(f"Task: {task_name}")
        print(f"Start Time: {start_time}")
        print(f"SNS Message ID: {response['MessageId']}")
        print("=========================")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Reminder email sent successfully",
                "taskName": task_name,
                "messageId": response["MessageId"],
            }),
        }

    except Exception as error:
        print(f"ERROR: {str(error)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(error)}),
        }
