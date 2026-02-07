import random
from datetime import datetime
import uuid
import time
import boto3
import json


sns = boto3.client("sns", region_name="us-east-1")


SNS_TEMP_TOPIC_ARN = ""
SNS_AIR_TOPIC_ARN  = ""

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

    # cada 50 eventos → 1 erróneo
    is_error = (EVENT_COUNTER % 50 == 0)
    event = generate_event(is_error=is_error)
    message = json.dumps(event)
    #SQS SEGÚN TIPO
    
    if event["eventType"] == "temperature-sensor":
        topic_arn = SNS_TEMP_TOPIC_ARN
    else:
        topic_arn = SNS_AIR_TOPIC_ARN

    sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=event["eventType"]
    )
    if is_error:
        print("🚨 Evento ERRÓNEO enviado:", event)
    else:
        print("✅ Evento enviado:", event)

    time.sleep(0.5)
