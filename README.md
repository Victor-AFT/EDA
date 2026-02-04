
# 📊 EDA – Sistema de Ingestión y Procesamiento de Eventos IoT (Calidad del Aire)

Este proyecto simula un sistema de ingestión y procesamiento de eventos IoT orientado al **monitoreo de la calidad del aire**.
Sensores virtuales generan eventos continuamente con mediciones ambientales como:

- AQI
- PM2.5
- PM10

Los eventos se envían a un canal desacoplado y luego son procesados de forma asíncrona, categorizados y almacenados para análisis posterior.

El objetivo principal es demostrar un **flujo de eventos near‑real‑time**, desacoplado, escalable y con persistencia de estado derivado.

---

## 🧩 Servicios Utilizados en AWS
- SNS
- SQS
- Lambda
- DynamoDB
- CloudWatch

---

## 1️⃣ Generación de eventos
La generación se realiza mediante un script productor que simula sensores IoT de calidad del aire (**Eventos_AirQuality**).

### Características del evento
Cada evento contiene:

| Campo       | Descripción                          |
|-------------|--------------------------------------|
| eventId     | Identificador único (UUID)           |
| timestamp   | Fecha y hora de generación           |
| sensorId    | Identificador del sensor             |
| aqi         | Índice de calidad del aire           |
| pm25        | Partículas finas                     |
| pm10        | Partículas gruesas                   |

El script genera valores aleatorios dentro de rangos realistas y publica un evento **cada 0.5 segundos**, simulando un stream real.

---

## 2️⃣ Ingesta y canalización de eventos

El sistema utiliza **AWS SNS** como canal de eventos intermedio.

### Flujo arquitectónico
```
Productor (Python) → SNS Topic → SQS → Lambda Consumidora → DynamoDB
```

### Componentes
- Productor: genera y publica eventos en SNS
- Consumidor (Lambda): procesa cada evento
- Persistencia (DynamoDB): almacena los datos procesados

---

## 3️⃣ Procesamiento asíncrono / streaming

La Lambda consumidora procesa los mensajes provenientes de SQS:

1. Deserializa el evento
2. Calcula la categoría de calidad del aire
3. Persiste el resultado en DynamoDB

Nombre del consumidor: **Consumidor_contaminacion**

---

## 4️⃣ Estado y agregados

El sistema mantiene **estado derivado**:

- Categoría de calidad del aire
  - BUENA, MODERADA, INSALUBRE, etc.
- Último valor conocido por sensor

La categorización se calcula **una sola vez** en el consumidor y se almacena de forma persistente.

---

## 5️⃣ Persistencia en DynamoDB

Cada evento procesado se almacena como un ítem en DynamoDB con:

- PK: eventId
- sensorId
- timestamp
- eventType
- data (mediciones + categoría)

### Justificación de DynamoDB
- Alta velocidad de escritura
- Escalado automático
- Estructura flexible (ideal para eventos)
- Compatible con Free Tier
- Costos mínimos

---

## 6️⃣ Manejo de errores

Si la Lambda falla:

1. SQS reintenta automáticamente
2. Si persisten los fallos → el mensaje pasa a una **DLQ (Dead Letter Queue)**

---

## 🛠 Requisitos no funcionales

### Arquitectura desacoplada
- Productores y consumidores no se conocen
- Cambios en un componente no afectan a otro

### Escalabilidad
- SNS y SQS escalan automáticamente
- Lambda escala por concurrencia
- DynamoDB soporta alto throughput

### Uso responsable de recursos
- Servicios serverless
- Sin servidores activos
- Operación dentro del Free Tier de AWS

