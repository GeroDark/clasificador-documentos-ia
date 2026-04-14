# Clasificador de Documentos con IA

Backend en Python para procesamiento documental empresarial con clasificación, extracción de información, búsqueda semántica y preguntas sobre documentos.

La propuesta de valor del proyecto es convertir documentos como contratos, propuestas, cartas, facturas o reportes en datos consultables desde API, con un pipeline asíncrono y una base técnica defendible para portafolio profesional de backend.

## Qué problema resuelve

En muchos equipos los documentos viven como archivos sueltos y la consulta depende de lectura manual. Eso vuelve costoso:

- encontrar información puntual
- clasificar documentos operativamente
- detectar montos, fechas o vigencias
- buscar por significado, no solo por nombre de archivo
- responder preguntas sobre el contenido ya cargado

Este proyecto aborda ese problema desde backend:

- recibe archivos `PDF`, `DOCX` y `TXT`
- extrae texto
- clasifica y resume
- extrae campos de negocio
- indexa chunks con embeddings
- habilita búsqueda semántica
- responde preguntas con fragmentos fuente

## Capacidades actuales

- carga de documentos y almacenamiento local en `uploads/`
- creación y seguimiento de jobs de procesamiento
- procesamiento asíncrono con Celery + Redis
- extracción de texto para `TXT`, `DOCX` y `PDF`
- clasificación documental basada en reglas
- resumen extractivo
- extracción de campos clave
- indexación semántica con PostgreSQL + `pgvector`
- endpoint de búsqueda semántica
- endpoint de preguntas sobre documentos
- autenticación JWT básica
- health checks, contrato API consistente, tests y CI

## Documentación técnica

- [Arquitectura](docs/architecture.md)
- [API Overview](docs/api-overview.md)
- [Demo Workflow](docs/demo-workflow.md)

## Enfoque del proyecto

No busca simular una plataforma enterprise completa ni prometer funcionalidades inexistentes. El foco actual es una base profesional para backend Python + IA documental aplicada:

- arquitectura por capas
- API clara y documentada
- pipeline asíncrono explícito
- persistencia relacional
- recuperación semántica
- testing pragmático

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
AUTH_SECRET_KEY=change-me-in-development-32-bytes
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Instalación local

### 1. Clonar el proyecto

```bash
git clone https://github.com/GeroDark/clasificador-documentos-ia.git
cd clasificador-documentos-ia
```

### 2. Crear entorno virtual

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements-dev.txt
```

### 4. Levantar servicios con Docker

```bash
docker compose up -d
```

Esto levanta:

- PostgreSQL con `pgvector` en `127.0.0.1:5433`
- Redis en `127.0.0.1:6379`

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

## Demo local rápida

Hay un flujo demo pensado para que cualquier persona pruebe el backend sin frontend y con un usuario local reproducible.

### Crear usuario demo

```bash
python -m app.scripts.create_demo_user
```

Credenciales demo locales:

- `demo@example.com`
- `DemoPass123!`

### Requests listas para probar

- [Guía demo paso a paso](docs/demo-workflow.md)
- [Colección HTTP](docs/requests/demo-api.http)
- [Documento de ejemplo](docs/demo-files/demo-propuesta.txt)

El flujo recomendado es:

1. levantar Docker
2. correr migraciones
3. crear usuario demo
4. hacer login
5. subir el archivo de ejemplo
6. consultar el job
7. ejecutar búsqueda
8. hacer una pregunta

---

## Documentación interactiva

Una vez levantada la API, la documentación Swagger está disponible en:

```text
http://127.0.0.1:8000/docs
```

La especificación OpenAPI se expone en:

```text
http://127.0.0.1:8000/openapi.json
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

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

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

## Autenticación

La versión actual incluye autenticación JWT básica con:

- registro de usuarios
- login con email y contraseña
- endpoint `GET /api/auth/me`
- protección de endpoints de negocio (`documents`, `jobs`, `search` y `ask`)

Los passwords se almacenan hasheados con `scrypt`; no se guardan en texto plano.

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
pytest -q
```

Ejecutar lint:

```bash
ruff check .
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
- endpoints críticos de documentos y jobs
- contrato API y errores
- cobertura determinista de `/api/search` y `/api/ask`

---

## CI

GitHub Actions valida el proyecto en cada `push` y `pull_request`.

El workflow actual:

- instala dependencias con Python 3.11
- levanta PostgreSQL con `pgvector`
- levanta Redis
- crea `uploads/`
- ejecuta `alembic upgrade head`
- corre `ruff check .`
- corre `pytest -q`

---

## Limitaciones actuales

- la clasificación usa reglas, no un modelo entrenado
- el resumen es extractivo, no generativo
- la extracción de campos depende de patrones relativamente estructurados
- PDFs escaneados podrían requerir OCR
- el almacenamiento de archivos es local
- la autenticación actual es JWT básica: no hay roles, refresh tokens ni recuperación de contraseña
- la corrección manual de resultados aún no está implementada

---

## Mejoras futuras

Roadmap corto y realista para siguientes fases:

- reforzar evaluación y calidad de clasificación/extracción
- mejorar ranking y estrategia de búsqueda semántica
- ampliar tests de integración sobre pipeline completo
- documentar despliegue local y productivo con más detalle

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
