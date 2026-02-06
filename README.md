# 📡 Arquitectura Serverless de Telemetría y Alertas (AWS Lambda)

<img width="699" height="858" alt="DA SENSOR drawio" src="https://github.com/user-attachments/assets/12c5f048-ee23-45a0-aedf-e0e3cd922f56" />

Este repositorio documenta una **arquitectura serverless en AWS** diseñada para procesar eventos de telemetría (aire y temperatura), almacenarlos, categorizarlos y generar **alertas críticas** de forma desacoplada, escalable y resiliente.

---

## 🧠 Visión General

Arquitectura basada en eventos (**event-driven**):

- Un script genera eventos de sensores.
- SNS desacopla la publicación.
- SQS garantiza procesamiento confiable.
- Lambdas procesan, almacenan y categorizan datos.
- Se generan alertas críticas con notificación por email.

---

## 🗺️ Flujo de Arquitectura

```
Script Eventos
   ├── SNS_AIR  → SQS_AIR  → Lambda Process Air
   └── SNS_TEMP → SQS_TEMP → Lambda Process Temp
                          ↓
                    DB Telemetry
                          ↓
                   SQS_CATEGORIZADO
                          ↓
                    Lambda Alertas
                          ├── DB Alertas
                          └── SNS Alertas Críticas → Email
```

---

## 🔧 Componentes

### Productor
- Script Eventos: genera y publica datos de sensores.

### Ingesta
- SNS_AIR / SNS_TEMP
- SQS_AIR / SQS_TEMP

### Procesamiento
- Lambda Process Air
- Lambda Process Temp

### Almacenamiento
- DB Telemetry
- DB Alertas

### Alertas
- Lambda Alertas
- SNS Alertas Críticas
- Email Alertas Críticas

---

## 🚀 Beneficios

- Serverless
- Escalable
- Alta disponibilidad
- Procesamiento asíncrono
- Fácil extensión

---

## 🔒 Consideraciones

- Dead Letter Queues
- CloudWatch Logs & Metrics
- IAM con menor privilegio
- Infraestructura como Código recomendada

---

## 📄 Licencia

Definir licencia del proyecto.
