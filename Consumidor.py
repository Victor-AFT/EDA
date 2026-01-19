import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Data_iot')


def save_to_dynamodb(event_type, data):
    item = {
        "eventId": str(uuid.uuid4()),
        "eventType": event_type,
        "sensorId": data["sensorId"],
        "timestamp": datetime.utcnow().isoformat(),
        "data": json.loads(json.dumps(data), parse_float=Decimal)
    }

    table.put_item(Item=item)
    print("Guardado en DynamoDB:", item["eventId"])


def handle_temperature(event):
    save_to_dynamodb("temperature-sensor", event["data"])


def handle_air_quality(event):
    save_to_dynamodb("AirQualit-sensor", event["data"])


def handle_visibility(event):
    save_to_dynamodb("visibility-sensor", event["data"])


def handle_wind(event):
    save_to_dynamodb("wind-sensor", event["data"])


def lambda_handler(event, context):
    print("Evento recibido:", event)

    for record in event["Records"]:
        body = json.loads(record["body"])
        message = json.loads(body["Message"])

        print("Evento IoT:", message)

        event_type = message.get("eventType")

        handlers = {
            "temperature-sensor": handle_temperature,
            "AirQualit-sensor": handle_air_quality,
            "visibility-sensor": handle_visibility,
            "wind-sensor": handle_wind
        }

        handler = handlers.get(event_type)

        if handler:
            handler(message)
        else:
            print("Evento no soportado:", event_type)

    return {
        "statusCode": 200
    }
