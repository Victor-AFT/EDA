# EDA
Simulacion de una Arquitectura Basada en eventos

Cloud (AWS)
	- SNS / SQS
	- EventBridge
	- Lambda
  - DynamoDB / DynamoDB Streams
    
### 1. Generación de eventos
	- Simular una fuente de eventos continua (script, API, productor, etc.)
	- Los eventos deben contener:
	 - identificador
	 - timestamp
	 - algún atributo de negocio (usuario, sensor, pedido, etc.)
   
### 2. Ingesta y canalización de eventos
	- Usar un canal de eventos (topic, stream, queue, bus)
	- Separar claramente:
	 - productores
	 - consumidores
	- Justificar el tipo de comunicación:
	 - pub/sub
	 - colas
	 - streaming
### 3. Procesamiento asíncrono / streaming
	- Procesar eventos en near-real-time
	- Demostrar comprensión de:
	 - orden
	 - concurrencia
	 - retries
	 - idempotencia (aunque sea parcial)
### 4. Estado y agregados
	El sistema debe mantener estado derivado a partir de eventos, por ejemplo:
	- contadores
	- sumas
	- último valor conocido
	- agregados por ventana temporal (opcional)
	Este estado:
	- no debe recalcularse desde cero
	- debe actualizarse incrementalmente
### 5. Persistencia
	- Almacenar eventos individuales (opcional pero recomendado)
	- Almacenar estado agregado
	- Justificar el modelo de datos elegido
### 6. Manejo de errores
Demostrar qué ocurre cuando un evento falla:
	- retries
	- DLQ
	- reintentos
	Explicar las implicaciones.
## Requisitos no funcionales
	- Arquitectura desacoplada
	- Escalado razonable
