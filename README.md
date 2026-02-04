# EDA
Este proyecto simula un sistema de ingestión y procesamiento de eventos IoT orientado al monitoreo de la calidad del aire. 
Sensores virtuales generan eventos de manera continua con mediciones ambientales (AQI, PM2.5 y PM10). 
Estos eventos son enviados a un canal desacoplado y procesados de forma asíncrona, donde se categorizan y almacenan para análisis posterior. 
El objetivo principal es demostrar un flujo de eventos near-real-time, desacoplado, escalable y con persistencia de estado derivado. 

<img width="364" height="611" alt="image" src="https://github.com/user-attachments/assets/50784427-7977-4f23-8a71-10b88871c142" />


Cloud (AWS)
	SNS / SQS,  
	Lambda, 
    DynamoDB 
    
### 1. Generación de eventos
La generación de eventos se realiza mediante un script productor que simula sensores IoT de calidad del aire Eventes_AirQuality 
Características del evento: 
	eventId: identificador único (UUID) 
	timestamp: fecha y hora de generación 
	atributo: 
		sensorId 
		aqi 
		pm25 
		pm10 
El script genera valores aleatorios dentro de rangos realistas y publica eventos de manera continua cada 0.5 segundos, simulando un stream de datos. 
   
### 2. Ingesta y canalización de eventos
Se utiliza AWS SNS como canal de eventos intermedio. 
Flujo: 
	Productor (script Python) → SNS Topic → SQS → Lambda Consumidora
Componentes:
	Productor: genera y publica eventos (SNS) 
	Consumidor: procesa eventos (Lambda) 
	Persistencia: DynamoDB 
 
### 3. Procesamiento asíncrono / streaming
La Lambda consumidora procesa los eventos conforme llegan desde SQS  (Consumidor_contaminacion) 
Cada mensaje: 
	Se deserializa.
	Se categoriza según severidad ambiental.
	Persiste en DynamoDB.
		
### 4. Estado y agregados
Estado derivado 
	El sistema mantiene estado derivado del evento: 
	Categoría de calidad del aire (BUENA, MODERADA, INSALUBRE, etc.) 
	Último valor conocido por sensor 
	La categorización se calcula una sola vez en el consumidor y se almacena. 	
### 5. Persistencia
Cada evento procesado se almacena como un ítem en DynamoDB. 
Campos principales: 
	eventId (PK) 
	sensorId 
	timestamp 
	eventType 
	data (mediciones + categoría) 
Justificacion:
	Se utiliza NoSQL (DynamoDB) porque: 
		Alta velocidad de escritura 
		Escalado automático 
		Estructura flexible (ideal para eventos) 
		Compatible con Free Tier 
	
### 6. Manejo de errores
Flujo ante fallos 
Si la Lambda falla: 
	SQS reintenta automáticamente 
Si falla repetidamente: 
	El mensaje puede enviarse a una DLQ (Dead Letter Queue) 
		
## Requisitos no funcionales
Arquitectura desacoplada
	Productores y consumidores no se conocen 
	Cambios en un componente no afectan a otros
	
Escalado razonable 
	SNS y SQS escalan automáticamente 
	Lambda escala por concurrencia 
	DynamoDB maneja alto throughput 

Uso responsable de recursos 
	Servicios serverless 
	Sin servidores activos 
	Compatible con AWS Free Tier 
	Costos mínimos 
