import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Students')

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:your-region:your-account-id:student-registration-topic'  # <-- Replace with real ARN

def lambda_handler(event, context):
    print("🔍 Received event:", json.dumps(event))  # Log the full incoming event

    method = event.get('httpMethod')
    print("🔍 HTTP Method:", method)

    if method == "POST":
        try:
            body = json.loads(event['body'])
            print("📝 Parsed body:", body)

            # Store in DynamoDB
            table.put_item(Item=body)
            print("✅ Item inserted into DynamoDB")

            # Compose and send SNS message
            message = f"📘 New student registered:\nName: {body.get('name')}\nEmail: {body.get('email')}\nID: {body.get('studentID')}"
            response = sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="New Student Registered",
                Message=message
            )
            print("📤 SNS publish response:", response)

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps("Student registered successfully")
            }

        except Exception as e:
            print("❌ Error during POST:", str(e))
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps("Internal Server Error")
            }

    elif method == "GET":
        try:
            student_id = event['pathParameters']['studentID']
            print("🔍 GET studentID:", student_id)

            response = table.get_item(Key={'studentID': student_id})
            item = response.get('Item')
            print("📦 GET item response:", item)

            if item:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps(item)
                }
            else:
                print("⚠️ Student not found.")
                return {
                    "statusCode": 404,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps("Student not found")
                }

        except Exception as e:
            print("❌ Error during GET:", str(e))
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps("Internal Server Error")
            }

    print("⚠️ Unsupported method:", method)
    return {
        "statusCode": 400,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps("Unsupported method")
    }
