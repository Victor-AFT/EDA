import random
from datetime import datetime
import uuid
import time
import boto3
import json


client_sns = boto3.client("sns", region_name="us-east-1")

aqi_value = random.randint(0, 350)
pm25_value = round(random.uniform(0, 300), 2)
pm10_value = round(random.uniform(0, 500), 2)




#lambda2
sensor_air={
  "eventId": str(uuid.uuid4()),
  "eventType": "AirQualit-sensor",
  "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
  "data":{
    "sensorId": "air-"+str(random.randint(1, 10000)),
    #Índice de Calidad del Aire
    "aqi": aqi_value,
    #Material Particulado finas
    "pm25": pm25_value,
    #Material Particulado grandes
    "pm10":pm10_value ,
    "category":  {}
  }
  
}




def generate_event():
    return random.choice([sensor_air])

while True:
    event = generate_event()
    client_sns.publish(Message=json.dumps(event),TargetArn="arn:aws:sns:us-east-1:983470701612:IOT_SNS")
    print("Evento enviado:", event)
    time.sleep(0.5)  # streaming continuo


