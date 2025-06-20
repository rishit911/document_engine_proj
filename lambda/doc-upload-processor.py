import json
import boto3
import urllib.parse

def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    s3 = boto3.client('s3')
    textract = boto3.client('textract')
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('DocumentTextTable')

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        try:
            # Extract text using Textract
            response = textract.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )

            # Safely extract lines
            extracted_lines = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE' and 'Text' in block:
                    extracted_lines.append(block['Text'])

            extracted_text = "\n".join(extracted_lines)
            print("Extracted text:", extracted_text)

            # Store in DynamoDB
            table.put_item(
                Item={
                    'DocumentName': key,
                    'ExtractedText': extracted_text
                }
            )

            print(f"Saved extracted text for {key} into DynamoDB.")

        except Exception as e:
            print(f"Error processing file {key} from bucket {bucket}: {e}")

    return {"statusCode": 200, "body": "Document processed and stored."}
