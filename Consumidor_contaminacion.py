import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Data_iot')



def get_aqi(aqi):
    if aqi <= 50:
        return "BUENA"
    elif aqi <= 100:
        return "MODERADA"
    elif aqi <= 150:
        return "INSALUBRE_PARA_SENSIBLES"
    elif aqi <= 200:
        return "INSALUBRE"
    elif aqi <= 300:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"

def get_pm25(pm25):
    if pm25 <= 12.0:
        return "BUENA"
    elif pm25 <= 35.4:
        return "MODERADA"
    elif pm25 <= 55.4:
        return "INSALUBRE_PARA_SENSIBLES"
    elif pm25 <= 150.4:
        return "INSALUBRE"
    elif pm25 <= 250.4:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"

def get_pm10(pm10):
    if pm10 <= 54:
        return "BUENA"
    elif pm10 <= 154:
        return "MODERADA"
    elif pm10 <= 254:
        return "INSALUBRE_PARA_SENSIBLES"
    elif pm10 <= 354:
        return "INSALUBRE"
    elif pm10 <= 424:
        return "MUY_INSALUBRE"
    else:
        return "PELIGROSA"


def get_air_quality_category(aqi, pm25, pm10):
    categories = [
        get_aqi(aqi),
        get_pm25(pm25),
        get_pm10(pm10)
    ]

    severity_order = [
    "BUENA",
    "MODERADA",
    "INSALUBRE_PARA_SENSIBLES",
    "INSALUBRE",
    "MUY_INSALUBRE",
    "PELIGROSA"
    ]

    return max(categories, key=lambda c: severity_order.index(c))



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
        if item["eventType"] == "AirQualit-sensor":
            aqi=get_aqi(item["data"]["aqi"])
            pm25=get_pm25(item["data"]["pm25"])
            pm10=get_pm10(item["data"]["pm10"])
           
            category =  get_air_quality_category(aqi, pm25, pm10)
            item['data']["category"] = category  # opcional, pero útil
            print(f"Update item {item} to table {table}")

        # Guardar UNA sola vez en DynamoDB
        table.put_item(Item=item)
        print("Guardado en DynamoDB:", item["eventId"])

       
    return {
        "statusCode": 200
    }
