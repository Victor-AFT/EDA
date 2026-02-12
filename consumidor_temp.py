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

QUEUE_URL="SNS"
BUCKET_NAME="s3-telemetry-bucket"

def dec_to_native(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, dict):
        return {k: dec_to_native(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [dec_to_native(x) for x in obj]

    return obj

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
    
    print("LAMBDA CONSUMIDOR TEMP:")
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

        
        # ---- TEMPERATURE ----
        
        try:
            status = get_temperature_status(item["data"]["value"])
            
            item["data"]["status"] = status
            print("Status calculada:", status)
        except (ValueError, TypeError) as e:
            print("Error categorizando Temperature:", e)
    
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
            MessageBody=json.dumps(item)
        )


    return {"statusCode": 200}
