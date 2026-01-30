import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Data_iot')


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
        #Categorizacion de evento
        if item["eventType"] == "temperature-sensor" and item["eventType"]['data']==float:

            status = get_temperature_status(item["data"]["value"])
            item["data"]["status"] = status 
            print(f"Update item {item} to table {table}")

        # Guardar UNA sola vez en DynamoDB
        table.put_item(Item=item)
        print("Guardado en DynamoDB:", item["eventId"])

       
    return {
        "statusCode": 200
    }
