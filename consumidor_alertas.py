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

# Fecha de expiración en 3h en DYNAMODB
expire_at = int(time.time()) + 3 * 3600

sns = boto3.client("sns")
SNS_IOT_ALERT = "arn:aws:sns"

def save_critical_alert(sensor_id, event_type, category_or_status, timestamp):
    alert_item = {
        "severity": "CRITICAL",
        "timestamp": timestamp,
        "alertId": str(uuid.uuid4()),
        "sensorId": sensor_id,
        "eventType": event_type,
        "category": category_or_status,
        # TTL: 3 horas
        "ttl": expire_at
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
                print("category: ",message['data']['category'])
                try:
                  
                    if message['data']['category'] in ["INSALUBRE", "MUY_INSALUBRE", "PELIGROSA"] and item['timestamp'] not in ['INVALID_TIMESTAMP']:
                        # Guardado alerta crítica
                        save_critical_alert(
                            sensor_id=item["sensorId"],
                            event_type=item["eventType"],
                            category_or_status=item['data']['category'],
                            timestamp=item["timestamp"]
                        )

                        # Envio de notificacion a SNS
                        sns.publish(
                            TopicArn=SNS_IOT_ALERT,
                            Subject="ALERTA CALIDAD DEL AIRE",
                            Message=(
                                f"Sensor: {item['sensorId']}\n"
                                f"Categoría: {item['data']['category']}\n"
                                f"Hora: {item['timestamp']}"
                            )
                        )
                    
                except (ValueError, TypeError) as e:
                    print("Error:", e)
                
            # ---- TEMPERATURE ----
            if item["eventType"] == "temperature-sensor":
                try:
                    
                    if message['data']['status'] in ["EXTREME_HEAT", "EXTREME_COLD"] and item['timestamp'] not in ['INVALID_TIMESTAMP'] :
                        # Guardado alerta crítica
                        save_critical_alert(
                            sensor_id=item["sensorId"],
                            event_type=item["eventType"],
                            category_or_status=message['data']['status'],
                            timestamp=item["timestamp"]
                        )

                        # Envio de notificacion a SNS
                        sns.publish(
                            TopicArn=SNS_IOT_ALERT,
                            Subject="ALERTA TEMPERATURA",
                            Message=(
                                f"Sensor: {item['sensorId']}\n"
                                f"Estado: {message['data']['status']}\n"
                                f"Hora: {item['timestamp']}"
                            )
                        )
                    
                except (ValueError, TypeError) as e:
                    print("Error :", e)
        else:
            pass
        
    return {"statusCode": 200}
