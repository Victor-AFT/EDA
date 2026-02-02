import random
from datetime import datetime
import uuid
import time
import boto3
import json

client_sns = boto3.client("sns", region_name="us-east-1")

EVENT_COUNTER = 0  # contador

def generate_event(is_error=False):
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


while True:
    EVENT_COUNTER += 1

    # cada 50 eventos → 1 erróneo
    is_error = (EVENT_COUNTER % 50 == 0)
    event = generate_event(is_error=is_error)
    client_sns.publish(
        Message=json.dumps(event),
        TargetArn="arn:aws:sns:us-east-1:983470701612:SNS_AIR"
    )

    if is_error:
        print("🚨 Evento ERRÓNEO enviado:", event)
    else:
        print("✅ Evento enviado:", event)

    time.sleep(0.5)
