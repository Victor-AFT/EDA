import json
import boto3
from datetime import datetime
from decimal import Decimal
import uuid
import time

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table_telemetry = dynamodb.Table('IoT_Telemetry')
table_alerts=dynamodb.Table('IoT_Critical_Alerts')

sns = boto3.client("sns")
SNS_IOT_ALERT = "arn:aws:sns:us-east-1:983470701612:SNS_IOT_ALERT"

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

def save_critical_alert(
    sensor_id,
    event_type,
    metric,
    value,
    category_or_status,
    timestamp
):
    alert_item = {
        "severity": "CRITICAL",
        "timestamp": timestamp,
        "alertId": str(uuid.uuid4()),
        "sensorId": sensor_id,
        "eventType": event_type,
        "metric": metric,
        "value": Decimal(str(value)),
        "category": category_or_status,
        # TTL: 7 días
        "ttl": int(time.time()) + (7 * 24 * 60 * 60)
    }

    table_alerts.put_item(Item=alert_item)
    print("Alerta crítica guardada:", alert_item["alertId"])


def lambda_handler(event, context):
    print("Evento recibido:", event)

    for record in event["Records"]:

        message = json.loads(record["body"])

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

        print("eventType recibido:", item["eventType"])
        print("data antes de categorizar:", item["data"])

        # ---- AIR QUALITY ----
        if item["eventType"] == 'AirQuality-sensor':
            try:
                aqi_value = int(item["data"]["aqi"])
                pm25_value = float(item["data"]["pm25"])
                pm10_value = int(item["data"]["pm10"])

                category = get_air_quality_category(
                    aqi_value,
                    pm25_value,
                    pm10_value
                )
                
                if category in ["INSALUBRE", "MUY_INSALUBRE", "PELIGROSA"]:
                    # Guardado alerta crítica
                    save_critical_alert(
                        sensor_id=item["sensorId"],
                        event_type=item["eventType"],
                        metric="air_quality",
                        value="N/A",
                        category_or_status=category,
                        timestamp=item["timestamp"]
                    )

                    # Envio de notificacion a SNS
                    sns.publish(
                        TopicArn=SNS_IOT_ALERT,
                        Subject="ALERTA CALIDAD DEL AIRE",
                        Message=(
                            f"Sensor: {item['sensorId']}\n"
                            f"AQI: {aqi_value}\n"
                            f"PM2.5: {pm25_value}\n"
                            f"PM10: {pm10_value}\n"
                            f"Categoría: {category}\n"
                            f"Hora: {item['timestamp']}"
                        )
                    )
                item["data"]["category"] = category
                print("Categoría calculada:", category)

            except (ValueError, TypeError) as e:
                print("Error categorizando AirQuality:", e)

        # ---- TEMPERATURE ----
        if item["eventType"] == "temperature-sensor":
            try:
                status = get_temperature_status(item["data"]["value"])
                
                if status in ["EXTREME_HEAT", "EXTREME_COLD"]:
                    # Guardado alerta crítica
                    save_critical_alert(
                        sensor_id=item["sensorId"],
                        event_type=item["eventType"],
                        metric="temperature",
                        value=item["data"]["value"],
                        category_or_status=status,
                        timestamp=item["timestamp"]
                    )

                    # Envio de notificacion a SNS
                    sns.publish(
                        TopicArn=SNS_IOT_ALERT,
                        Subject="🚨 ALERTA TEMPERATURA",
                        Message=(
                            f"Sensor: {item['sensorId']}\n"
                            f"Temperatura: {item['data']['value']} °C\n"
                            f"Estado: {status}\n"
                            f"Hora: {item['timestamp']}"
                        )
                    )
                item["data"]["status"] = status
            except (ValueError, TypeError) as e:
                print("Error categorizando Temperature:", e)

        table_telemetry.put_item(Item=item)
        print("Guardado en DynamoDB:", item["eventId"])
        print("DATA después de categorizar:", item["data"])

    return {"statusCode": 200}
