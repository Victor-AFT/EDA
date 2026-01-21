import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Data_iot')


def lambda_handler(event, context):
    print("Evento recibido:", event)

    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])

        print("Evento IoT:", message)

        #Crea item para DynamoDB
        item = {
            "eventId": message['eventId'],
            "eventType": message["eventType"],
            "sensorId": message["data"]["sensorId"],
            "timestamp": message['timestamp'],
            "data": json.loads(
                json.dumps(message["data"]),
                parse_float=Decimal
            )
        }

        # Guarda en DynamoDB
        table.put_item(Item=item)
        print("Guardado en DynamoDB:", item["eventId"])

    return {
        "statusCode": 200
    }
