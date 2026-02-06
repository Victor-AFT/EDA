import json

import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid
import time

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table_alerts=dynamodb.Table('IoT_Critical_Alerts')

sns = boto3.client("sns")
SNS_IOT_ALERT = ""

def save_critical_alert(
    sensor_id,
    event_type,
    category_or_status,
    timestamp
):
    alert_item = {
        "severity": "CRITICAL",
        "timestamp": timestamp,
        "alertId": str(uuid.uuid4()),
        "sensorId": sensor_id,
        "eventType": event_type,
        "category": category_or_status,
        # TTL: 7 días
        "ttl": int(time.time()) + (7 * 24 * 60 * 60)
    }

    table_alerts.put_item(Item=alert_item)
    print("Alerta crítica guardada:", alert_item["alertId"])


def lambda_handler(event, context):
    print("LAMBDA_CREADOR_ALERTAS:")
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

           
            # ---- AIR QUALITY ----
            if item["eventType"] == 'AirQuality-sensor':
                try:
                  
                    if item["data"]['category'] in ["INSALUBRE", "MUY_INSALUBRE", "PELIGROSA"]:
                        # Guardado alerta crítica
                        save_critical_alert(
                            sensor_id=item["sensorId"],
                            event_type=item["eventType"],
                            category_or_status=item["data"]['category'],
                            timestamp=item["timestamp"]
                        )

                        # Envio de notificacion a SNS
                        sns.publish(
                            TopicArn=SNS_IOT_ALERT,
                            Subject="ALERTA CALIDAD DEL AIRE",
                            Message=(
                                f"Sensor: {item['sensorId']}\n"
                                f"Categoría: {message["data"]["category"]}\n"
                                f"Hora: {item['timestamp']}"
                            )
                        )
                    
                except (ValueError, TypeError) as e:
                    print("Error categorizando AirQuality:", e)
                
            # ---- TEMPERATURE ----
            if item["eventType"] == "temperature-sensor":
                try:
                    
                    if item["data"]['status'] in ["EXTREME_HEAT", "EXTREME_COLD"]:
                        # Guardado alerta crítica
                        save_critical_alert(
                            sensor_id=item["sensorId"],
                            event_type=item["eventType"],
                            value=float(item["data"]["value"]),
                            category_or_status=item["data"]['status'],
                            timestamp=item["timestamp"]
                        )

                        # Envio de notificacion a SNS
                        sns.publish(
                            TopicArn=SNS_IOT_ALERT,
                            Subject="ALERTA TEMPERATURA",
                            Message=(
                                f"Sensor: {item['sensorId']}\n"
                                f"Estado: {item["data"]['status']}\n"
                                f"Hora: {item['timestamp']}"
                            )
                        )
                    
                except (ValueError, TypeError) as e:
                    print("Error categorizando Temperature:", e)

        else:
            pass
        
    return {"statusCode": 200}
