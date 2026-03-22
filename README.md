# Plataforma Inteligente para Clasificación y Consulta de Documentos

API backend construida con **FastAPI** para procesar documentos empresariales con un flujo inteligente que permite:

- subir archivos PDF, DOCX y TXT
- extraer texto automáticamente
- clasificar documentos por tipo
- generar resúmenes automáticos
- extraer campos clave de negocio
- indexar contenido con embeddings
- realizar búsqueda semántica
- responder preguntas sobre los documentos
- procesar archivos en segundo plano con Celery + Redis

Este proyecto está orientado a un caso de uso empresarial real, no a una demo genérica de IA.

---

## Objetivo del proyecto

Construir una plataforma que permita a una empresa centralizar y consultar documentos de manera más eficiente usando procesamiento automático de lenguaje y búsqueda por significado.

Ejemplos de uso:

- clasificar contratos, propuestas, cartas, facturas e informes
- encontrar documentos relacionados con garantías o vencimientos
- extraer montos, fechas, remitentes, asuntos y vigencias
- responder preguntas como:
  - ¿Cuál es el monto referencial?
  - ¿Cuál es la vigencia del documento?
  - ¿Quién figura como remitente?
  - ¿De qué trata este documento?

---

## Características principales

### 1. Carga de documentos
Permite subir archivos en formato:

- PDF
- DOCX
- TXT

Cada archivo queda registrado con sus metadatos básicos y almacenado localmente en la carpeta `uploads/`.

### 2. Procesamiento automático
Una vez subido el archivo, el sistema ejecuta un pipeline asíncrono que:

- extrae texto
- clasifica el documento
- genera resumen
- extrae campos clave
- divide el contenido en fragmentos
- genera embeddings
- indexa el documento para búsqueda semántica

### 3. Clasificación documental
Clasifica el documento en categorías como:

- `contract`
- `proposal`
- `invoice`
- `letter`
- `report`
- `other`

Actualmente utiliza un clasificador basado en reglas y palabras clave, pensado como MVP profesional y extensible a modelos de IA más avanzados.

### 4. Resumen automático
Genera:

- resumen corto
- puntos clave
- palabras clave

### 5. Extracción de campos clave
Extrae automáticamente información útil como:

- empresa
- monto
- fecha
- asunto
- vigencia
- remitente

### 6. Búsqueda semántica
Permite consultar documentos por significado utilizando embeddings y `pgvector` en PostgreSQL.

Ejemplos:

- documentos que hablen de garantías
- propuestas con monto alto
- contratos con fecha de vencimiento
- documentos relacionados con carta fianza

### 7. Preguntas sobre documentos
Permite hacer preguntas en lenguaje natural y responder usando los fragmentos más relevantes del documento.

### 8. Procesamiento asíncrono
El procesamiento pesado se ejecuta con:

- Celery
- Redis

Esto permite que la subida de documentos responda rápido y el análisis ocurra en segundo plano.

### 9. Observabilidad básica
Incluye:

- health checks
- logging por request con `X-Request-ID`
- seguimiento de jobs de procesamiento

---

## Stack tecnológico

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic Settings

### Base de datos y búsqueda
- PostgreSQL
- pgvector

### Procesamiento y colas
- Celery
- Redis

### NLP / embeddings
- sentence-transformers
- all-MiniLM-L6-v2

### Infraestructura local
- Docker Compose

### Testing
- pytest

---

## Arquitectura general

```text
Cliente / Swagger
        |
        v
     FastAPI
        |
        +------------------------------+
        |                              |
        v                              v
 PostgreSQL + pgvector             Redis
        |                              |
        v                              v
 Metadatos / texto / chunks        Celery Worker
        |
        v
 Embeddings + búsqueda semántica
```

---

## Flujo del sistema

```text
1. El usuario sube un documento
2. La API registra el archivo y crea un job
3. Celery procesa el documento en segundo plano
4. Se extrae el texto
5. Se clasifica el documento
6. Se genera el resumen
7. Se extraen campos clave
8. Se generan chunks y embeddings
9. El documento queda disponible para búsqueda y preguntas
```

---

## Estructura del proyecto

```text
clasificador-documentos-ia/
│
├── alembic/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── ask.py
│   │   │   ├── documents.py
│   │   │   ├── jobs.py
│   │   │   └── search.py
│   │   └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── base_class.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   ├── document_text.py
│   │   ├── document_classification.py
│   │   ├── document_summary.py
│   │   ├── extracted_field.py
│   │   ├── document_chunk.py
│   │   ├── query_log.py
│   │   └── processing_job.py
│   │
│   ├── schemas/
│   ├── services/
│   │   ├── chunker.py
│   │   ├── classifier.py
│   │   ├── document_pipeline.py
│   │   ├── embeddings.py
│   │   ├── field_extractor.py
│   │   ├── health.py
│   │   ├── question_answering.py
│   │   ├── semantic_indexer.py
│   │   ├── storage.py
│   │   ├── summarizer.py
│   │   └── text_extractor.py
│   │
│   ├── celery_app.py
│   ├── main.py
│   └── tasks.py
│
├── tests/
├── uploads/
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

---

## Modelo de datos principal

Entidades implementadas:

- `Document`
- `DocumentText`
- `DocumentClassification`
- `DocumentSummary`
- `ExtractedField`
- `DocumentChunk`
- `QueryLog`
- `ProcessingJob`

---

## Variables de entorno

Crea un archivo `.env` a partir de `.env.example`.

Ejemplo:

```env
APP_NAME=Clasificador Inteligente de Documentos con IA
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/clasificador_documentos_ia
UPLOADS_DIR=uploads

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS=384
SEMANTIC_SEARCH_TOP_K=5

REDIS_URL=redis://127.0.0.1:6379/0
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

---

## Instalación local

### 1. Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd clasificador-documentos-ia
```

### 2. Crear entorno virtual

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements-dev.txt
```

### 4. Levantar servicios con Docker

```bash
docker compose up -d
```

### 5. Aplicar migraciones

```bash
alembic upgrade head
```

### 6. Levantar la API

```bash
uvicorn app.main:app --reload
```

### 7. Levantar el worker de Celery

En otra terminal:

```bash
celery -A app.celery_app:celery_app worker --pool=solo --loglevel=info
```

> En Windows se usa `--pool=solo` para evitar problemas con el pool por defecto.

---

## Documentación interactiva

Una vez levantada la API, la documentación Swagger está disponible en:

```text
http://127.0.0.1:8000/docs
```

---

## Endpoints principales

### Salud del sistema
- `GET /health/live`
- `GET /health/ready`

### Documentos
- `POST /api/documents/upload/`
- `GET /api/documents/`
- `GET /api/documents/{id}`
- `GET /api/documents/{id}/text`
- `GET /api/documents/{id}/classification`
- `GET /api/documents/{id}/summary`
- `GET /api/documents/{id}/fields`
- `GET /api/documents/{id}/chunks`

### Jobs
- `GET /api/jobs/`
- `GET /api/jobs/{job_id}/status`

### Búsqueda
- `GET /api/search/semantic/`

### Preguntas
- `POST /api/ask/`
- `GET /api/ask/logs/`

---

## Ejemplo de flujo de uso

### 1. Subir un documento
`POST /api/documents/upload/`

Respuesta esperada:

```json
{
  "id": 1,
  "document_id": 3,
  "task_id": "celery-task-id",
  "status": "queued",
  "error_message": null,
  "created_at": "2026-03-22T18:00:00",
  "started_at": null,
  "finished_at": null
}
```

### 2. Consultar el estado del job
`GET /api/jobs/{job_id}/status`

Estados posibles:

- `queued`
- `processing`
- `completed`
- `failed`

### 3. Consultar resultados del documento
Cuando el job termine:

- `GET /api/documents/{id}/text`
- `GET /api/documents/{id}/classification`
- `GET /api/documents/{id}/summary`
- `GET /api/documents/{id}/fields`
- `GET /api/documents/{id}/chunks`

### 4. Hacer preguntas sobre el documento

`POST /api/ask/`

```json
{
  "question": "¿Cuál es el monto referencial?",
  "document_id": 3,
  "top_k": 5
}
```

Ejemplo de respuesta:

```json
{
  "question": "¿Cuál es el monto referencial?",
  "answer": "Monto referencial: S/ 53,200.00.",
  "confidence": 0.96,
  "document_id": 3,
  "sources": [
    {
      "chunk_id": 10,
      "document_id": 3,
      "document_filename": "propuesta.txt",
      "chunk_index": 0,
      "chunk_text": "Carta de presentación de propuesta comercial. Monto referencial: S/ 53,200.00. Vigencia: 30 días calendario.",
      "score": 0.91
    }
  ]
}
```

---

## Ejemplo de búsqueda semántica

Consulta:

```text
documentos que hablen de garantías
```

Endpoint:

```text
GET /api/search/semantic/?q=documentos que hablen de garantías
```

Resultado esperado:

- lista de chunks relevantes
- score de similitud
- documento relacionado
- fragmento exacto recuperado

---

## Cómo funciona internamente

### Extracción de texto
- TXT: lectura directa
- DOCX: extracción de párrafos con `python-docx`
- PDF: extracción de texto con `pypdf`

### Clasificación
Clasificador basado en reglas y palabras clave.

### Resumen
Resumen extractivo basado en frecuencia de términos y selección de oraciones relevantes.

### Extracción de campos
Extracción por patrones regex para identificar campos de negocio.

### Búsqueda semántica
- división del documento en chunks
- generación de embeddings
- almacenamiento en PostgreSQL con `pgvector`
- búsqueda por similitud coseno

### Preguntas y respuestas
- recuperación de chunks relevantes
- selección de oraciones más útiles según la pregunta
- respuesta extractiva con fuentes

---

## Testing

Ejecutar tests:

```bash
pytest
```

Cobertura funcional actual de tests:

- health checks
- chunking
- clasificación
- extracción de texto
- resumen
- extracción de campos
- question answering
- estados del pipeline

---

## Limitaciones actuales

- la clasificación usa reglas, no un modelo entrenado
- el resumen es extractivo, no generativo
- la extracción de campos depende de patrones relativamente estructurados
- PDFs escaneados podrían requerir OCR
- el almacenamiento de archivos es local
- no hay autenticación ni control de usuarios
- la corrección manual de resultados aún no está implementada

---

## Mejoras futuras

- OCR para PDFs escaneados
- autenticación y gestión de usuarios
- almacenamiento en S3 o similar
- panel administrativo
- corrección manual de clasificación y campos
- búsqueda híbrida léxica + semántica
- re-ranking de resultados
- uso de LLM para resúmenes y respuestas más avanzadas
- evaluación automática de precisión
- métricas y observabilidad avanzada
- despliegue productivo con workers separados

---

## Valor profesional del proyecto

Este proyecto demuestra experiencia práctica en:

- diseño de APIs backend con FastAPI
- modelado de datos con SQLAlchemy
- migraciones con Alembic
- integración de PostgreSQL, pgvector y Redis
- procesamiento documental
- NLP aplicado a un caso empresarial
- búsqueda semántica
- embeddings y recuperación de información
- procesamiento asíncrono con Celery
- testing y diseño modular

---

## Estado actual

Proyecto funcional en evolución, orientado a portafolio profesional para posiciones de desarrollo backend Python / IA aplicada / automatización documental.

---

## Autor

Desarrollado por **Walter Gerald Arzapalo Janampa** **GeroDark** como proyecto de portafolio enfocado en backend, procesamiento documental e integración de IA aplicada a documentos empresariales.