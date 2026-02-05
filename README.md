
# 📊 EDA – Sistema de Ingestión y Procesamiento de Eventos IoT 


### Flujo arquitectónico
```
Sensores → SQS (x2) → Lambda → DynamoDB (telemetría)
                          └→ DynamoDB (alertas)
                          └→ SNS (notificaciones)

```
<img width="721" height="431" alt="Arquitectura Lambda" src="https://github.com/user-attachments/assets/1677cd41-2534-44ef-82c0-297b54c523b7" />


### Uso responsable de recursos
- Servicios serverless
- Sin servidores activos
- Operación dentro del Free Tier de AWS

