import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:021280546444:bruno-topic-sns'

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # 🔍 Log full event

    method = event['httpMethod']
    print("HTTP method:", method)  # 🔍 Log HTTP method

    if method == "POST":
        body = json.loads(event['body'])
        print("POST body parsed:", body)  # 🔍 Log parsed POST body

        # Save to DynamoDB
        table.put_item(Item=body)
        print("Item saved to DynamoDB")  # 🔍 Confirm save

        # Prepare SNS message
        message = f"New student registered:\n\n{json.dumps(body, indent=2)}"
        try:
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="New Student Registration",
                Message=message
            )
            print("SNS publish success:", response)  # ✅ Log success
        except Exception as e:
            print("SNS publish error:", str(e))  # ❌ Log error

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps("Student registered successfully and notification sent.")
        }

    elif method == "GET":
        student_id = event['pathParameters']['studentID']
        print("GET request for studentID:", student_id)

        response = table.get_item(Key={'studentID': student_id})
        item = response.get('Item')

        if item:
            print("Student found:", item)
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(item)
            }
        else:
            print("Student not found.")
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps("Student not found")
            }

    print("Unsupported method:", method)
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps("Unsupported method")
    }
