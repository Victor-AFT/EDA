
# 📊 EDA – Sistema de Ingestión y Procesamiento de Eventos IoT 


### Flujo arquitectónico
```
Sensores → SQS (x2) → Lambda → DynamoDB (telemetría)
                          └→ DynamoDB (alertas)
                          └→ SNS (notificaciones)

```



### Uso responsable de recursos
- Servicios serverless
- Sin servidores activos
- Operación dentro del Free Tier de AWS

<img width="721" height="431" alt="Arquitectura Lambda" src="https://github.com/user-attachments/assets/726ee4dc-b277-4abf-a0ad-fa560b39a05b" />
