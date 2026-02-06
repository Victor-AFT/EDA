import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid
import time

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table_telemetry = dynamodb.Table('IoT_Telemetry')


sns = boto3.client("sns")
SNS_TEMP = ""


def get_temperature_status(value):
    if value <= -30:
        return "EXTREME_COLD"
    elif value <= -10:
        return "VERY_COLD"
    elif value <= 5:
        return "COLD"
    elif value <= 20:
        return "NORMAL"
    elif value <= 30:
        return "WARM"
    elif value <= 40:
        return "HOT"
    else:
        return "EXTREME_HEAT"


def lambda_handler(event, context):
    print("LAMBDA CONSUMIDOR:")
    print("Evento recibido:", event)
    for record in event["Records"]:
        message = json.loads(record["body"])
        if message['eventId']:
            print("Evento IoT:", message)
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

            print("data antes de categorizar:", item["data"])
            
            try:
                status = get_temperature_status(item["data"]["value"])
                
                item["data"]["status"] = status
                print("Status calculada:", status)
            except (ValueError, TypeError) as e:
                print("Error categorizando Temperature:", e)
        
       
            table_telemetry.put_item(Item=item)
            print("Guardado en DynamoDB:", item["eventId"])
        else:
            pass
        
    return {"statusCode": 200}
