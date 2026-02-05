import random
from datetime import datetime
import uuid
import time
import boto3
import json

sqs = boto3.client("sqs", region_name="us-east-1")

SQS_TEMP_URL = "SQS_TEMP"
SQS_AIR_URL  = "SQS_AIR"
EVENT_COUNTER = 0  # contador


def generate_event_airquality(is_error=False):
    if not is_error:
        # EVENTO NORMAL
        return {
            "eventId": str(uuid.uuid4()),
            "eventType": "AirQuality-sensor",
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
            "data": {
                "sensorId": f"air-{random.randint(1, 10000)}",
                "aqi": random.randint(0, 350),
                "pm25": round(random.uniform(0, 300), 1),
                "pm10": random.randint(0, 500),
                "category": {}
            }
        }
    else:
        # EVENTO ERRÓNEO
        return {
            "eventId": str(uuid.uuid4()),
            "eventType": "AirQuality-sensor",
            "timestamp": "INVALID_TIMESTAMP",
            "data": {
                "sensorId": None,
                "aqi": "ERROR",          
                "pm25": -999,           
                "pm10": "NaN",           
            }
        }


def generate_event_temp(is_error=False):
    if not is_error:
        # EVENTO NORMAL
        return{
                "eventId": str(uuid.uuid4()),
                "eventType": "temperature-sensor",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                "data":{
                    "sensorId": "temp"+str(random.randint(1, 10000)),
                    "value": round(random.uniform(-70, 50), 2),
                    "unit": "Cº",
                    "status": {}
                }
        }
    else:
        # EVENTO ERRÓNEO
        return {
            "eventId": str(uuid.uuid4()),
            "eventType": "temperature-sensor",
            "timestamp": "INVALID_TIMESTAMP",
            "data": {
                "sensorId": None,
                    "value": -1111,
                    "unit": "Cº",
                    "status": {}
            }
        }


def generate_event(is_error=False):
    return random.choice([
        generate_event_airquality(is_error),
        generate_event_temp(is_error)
    ])

while True:
    EVENT_COUNTER += 1

    # cada 25 eventos → 1 erróneo
    #is_error = (EVENT_COUNTER % 25 == 0)
    is_error=False
    event = generate_event(is_error=is_error)

    #SQS SEGÚN TIPO
    if event["eventType"] == "temperature-sensor":
        queue_url = SQS_TEMP_URL
    else:
        queue_url = SQS_AIR_URL

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(event)
    )

    if is_error:
        print("🚨 Evento ERRÓNEO enviado:", event)
    else:
        print("✅ Evento enviado:", event)

    time.sleep(0.5)
