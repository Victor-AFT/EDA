import random
from datetime import datetime
import uuid
import time
import boto3
import json

client_sns = boto3.client("sns", region_name="us-east-1")
temperature_value = round(random.uniform(-70, 50), 2)
temperature_value_error = "na"


#Evento erroneo
sensor_temp_error={
  "eventId": str(uuid.uuid4()),
  "eventType": "temperature-sensor",
  "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
  "data":{
      "sensorId": "temp"+str(random.randint(1, 10000)),
      "value": temperature_value_error,
      "unit": "Cº",
      "status": {}
  }
  
}


#lambda_temperature
sensor_temp={
  "eventId": str(uuid.uuid4()),
  "eventType": "temperature-sensor",
  "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
  "data":{
      "sensorId": "temp"+str(random.randint(1, 10000)),
      "value": temperature_value,
      "unit": "Cº",
      "status": {}
  }
  
}



def generate_event():
    return random.choice([
        sensor_temp
    ])

while True:
    event = generate_event()
    client_sns.publish(Message=json.dumps(event),TargetArn="arn:aws:sns:us-east-1:983470701612:IOT_SNS")
    print("Evento enviado:", event)
    time.sleep(0.5)  # streaming continuo


