# info de la materia: ST0263 Tópicos Especiales en Telemática
#
# Estudiante(s): Samuel Valencia Loaiza, Lorena Goez Ruiz
#
# Profesor: Edwin Nelson Montoya Múnera, emontoya@eafit.brightspace.com
#
Link al video
https://www.youtube.com/watch?v=6EEorCzhlBg

--(Los archivos del repositorio son datos generales usados durante el desarrollo, no son los específicos para replicar la aplicación ya que se modificaron a medida que se trabajó directamente en aws)

# Proyecto 3 Telemática - Pipeline de Datos COVID Colombia
#
# 1. breve descripción de la actividad
#
Pipeline automatizado end-to-end para la captura, procesamiento y exposición de datos COVID del Ministerio de Salud de Colombia. El sistema implementa una arquitectura serverless en AWS que incluye ingesta automática, procesamiento ETL y exposición via API REST.

## 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

**Objetivo Principal:** Automatización del proceso de Captura, Ingesta, Procesamiento y Salida de datos accionables para gestión de datos de Covid en Colombia

**Requisitos Cumplidos:**

✅ **Fuentes de Datos Múltiples:**
- Datos COVID del Ministerio de Salud via API Socrata (gt2j-8ykr)
- Datos complementarios demográficos simulados (CSV en S3 como alternativa a RDS)

✅ **Ingesta Automática:**
- Lambda programada con EventBridge para descarga automática cada hora
- Almacenamiento en S3 Raw Zone (JSON)
- Proceso 100% automático sin intervención manual

✅ **Procesamiento ETL:**
- Lambda ETL que procesa y une datos COVID con datos demográficos
- Transformación de JSON a CSV en S3 Trusted Zone
- Consultas SQL via Athena para unión y transformación de datos

✅ **Análisis y Exposición:**
- API REST funcional via API Gateway
- Endpoint `/covid-stats` que devuelve estadísticas por departamento
- Consultas Athena sobre datos procesados
- Resultados disponibles via API y Athena

✅ **Automatización Completa:**
- Pipeline end-to-end sin intervención manual
- EventBridge orquestando ejecución horaria
- Procesamiento serverless sin clusters manuales

## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

**Adaptaciones por Restricciones Técnicas:**

🔄 **EMR Spark:** No se utilizó EMR debido a restricciones de la cuenta AWS. Se implementó alternativa con:
- Lambda + Athena para procesamiento ETL
- Consultas SQL en lugar de Spark jobs
- Manteniendo arquitectura serverless y automática

🔄 **RDS MySQL/PostgreSQL:** No se pudo configurar RDS. Se implementó alternativa con:
- Datos complementarios en CSV almacenados en S3
- Tablas Athena simulando base de datos relacional
- JOINs realizados via consultas SQL en Athena

# 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

## Arquitectura Implementada

EventBridge (cron cada hora)
↓
Lambda Ingesta → S3 Raw (JSON)
↓
Lambda ETL → Athena Query → S3 Trusted (CSV)
↓
API Gateway ← Lambda API ← Athena Queries
↓
Usuarios/Apps


## Patrones y Mejores Prácticas Aplicadas

🔹 **Arquitectura Serverless:** Zero administración de infraestructura
🔹 **Data Lake Architecture:** Zonas de datos (Raw, Trusted, Refined)
🔹 **Event-Driven Architecture:** Orquestación basada en eventos
🔹 **Separation of Concerns:** Lambdas especializadas por función
🔹 **Infrastructure as Code:** Scripts CLI para despliegue reproducible

## Servicios AWS Utilizados
- **Compute:** AWS Lambda (Python 3.9)
- **Storage:** Amazon S3 (Raw, Trusted, Results)
- **Orchestration:** Amazon EventBridge
- **Query:** Amazon Athena (SQL sobre S3)
- **API:** Amazon API Gateway (REST API)
- **Monitoring:** Amazon CloudWatch Logs

# 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

## Stack Tecnológico
- **Lenguaje:** Python 3.9
- **AWS SDK:** Boto3 (última versión)
- **Infraestructura:** AWS CLI v2
- **Almacenamiento:** JSON, CSV, Parquet
- **API:** REST JSON

# 4. Configuración de API Gateway
Tipo: REST API

Recurso: /covid-stats

Método: GET

Integración: Lambda covid-api

CORS: Habilitado

detalles del desarrollo.
Flujo de Datos
EventBridge dispara Lambda de ingesta cada hora

Lambda Ingesta descarga datos de Socrata API y guarda en S3 Raw

Lambda ETL ejecuta consulta Athena para unir datos y guarda en S3 Trusted

API Gateway recibe peticiones y las dirige a Lambda API

Lambda API ejecuta consultas Athena y devuelve resultados JSON

# Via API REST
curl -X GET "https://bj35dohnbi.execute-api.us-west-1.amazonaws.com/prod/covid-stats"

# Respuesta JSON ejemplo:
{
  "status": "success",
  "data": [
    {
      "department": "Antioquia",
      "total_cases": "15000",
      "avg_poverty": "15.5",
      "total_health_centers": "45"
    }
  ]
}

# Logros Destacados
🎯 Pipeline 100% automático sin intervención manual
🎯 Arquitectura serverless zero administración
🎯 Procesamiento de datos reales del Ministerio de Salud
🎯 API REST funcional con estadísticas actualizadas
🎯 Adaptación creativa a restricciones técnicas

Lecciones Aprendidas
Arquitectura de data lakes en AWS

Procesamiento ETL con servicios serverless

Automatización con EventBridge

Consultas SQL sobre datos en S3 con Athena

Diseño de APIs con API Gateway + Lambda

referencias:
Sitios de Referencia
AWS Documentation: https://docs.aws.amazon.com/

Socrata API Documentation: https://dev.socrata.com/

Dataset COVID Colombia: https://www.datos.gov.co/resource/gt2j-8ykr.json

AWS Athena SQL Reference: https://docs.aws.amazon.com/athena/latest/ug/ddl-sql-reference.html
    
