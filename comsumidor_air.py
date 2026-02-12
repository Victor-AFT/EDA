import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid
import time


# Conexión a SQS CATEGORIZADO
sqs = boto3.client("sqs")
# Conexión a S3 BUCKET
s3 = boto3.client("s3")

QUEUE_URL="SQS"
BUCKET_NAME="s3-telemetry-bucket"



def dec_to_native(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, dict):
        return {k: dec_to_native(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [dec_to_native(x) for x in obj]

    return obj


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
    print("LAMBDA PROCESS_AIR:")
    print("Evento recibido:", event)
    for record in event["Records"]:
        sns_envelope = json.loads(record["body"])
        message = json.loads(sns_envelope["Message"])
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
                aqi_value = int(item["data"]["aqi"])
                pm25_value = float(item["data"]["pm25"])
                pm10_value = int(item["data"]["pm10"])

                category = get_air_quality_category(
                    aqi_value,
                    pm25_value,
                    pm10_value
                )
                
                item["data"]["category"] = category
                print("Categoría calculada:", category)
                
        except (ValueError, TypeError) as e:
            print("Error categorizando AirQuality:", e)
            
        # StorageClass: "GLACIER_IR" | "GLACIER" | "DEEP_ARCHIVE"
        safe_item = dec_to_native(item)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"sensores/date={datetime.utcnow().date()}/{item['sensorId']}_{item['timestamp']}.json",
            Body=json.dumps(safe_item).encode("utf-8"),
            ContentType="application/json",
            StorageClass="DEEP_ARCHIVE"
        )

        print("Guardado en S3:", item["eventId"])
        #SQS_CAT
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(safe_item)
        )
        print(f"Enviado evento {message['eventId']} a {QUEUE_URL}")



    return {"statusCode": 200}
