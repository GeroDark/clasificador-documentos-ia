# Arquitectura

## Visión general

`clasificador-documentos-ia` es un backend monolítico en Python orientado al procesamiento inteligente de documentos empresariales.

Combina:

- API HTTP con FastAPI
- persistencia con SQLAlchemy sobre PostgreSQL
- migraciones con Alembic
- colas con Celery + Redis
- búsqueda semántica con `pgvector`

La intención actual del proyecto es priorizar una base técnica clara y profesional antes de agregar complejidad extra.

## Componentes principales

### FastAPI

Expone los endpoints del sistema:

- documentos
- jobs
- búsqueda semántica
- preguntas sobre documentos
- health checks

También centraliza:

- OpenAPI/Swagger
- validación de entrada
- contrato HTTP
- manejo consistente de errores controlados
- autenticación JWT

### SQLAlchemy + PostgreSQL

Persisten:

- usuarios
- documentos y metadatos
- texto extraído
- clasificaciones
- resúmenes
- campos extraídos
- chunks indexados
- logs de preguntas
- jobs de procesamiento

### Alembic

Versiona cambios del esquema y permite reproducir la base de datos de forma consistente con `alembic upgrade head`.

### Celery + Redis

La subida de documentos no procesa el archivo en línea. En su lugar:

1. la API crea el documento y el job
2. envía una tarea a Celery
3. el worker procesa el pipeline en segundo plano

Redis se usa como broker y backend de resultados.

### pgvector

Se usa para almacenar embeddings de chunks y habilitar consultas por similitud coseno desde PostgreSQL.

### Servicios del dominio

La lógica principal vive en `app/services/`:

- `text_extractor.py`
- `classifier.py`
- `summarizer.py`
- `field_extractor.py`
- `chunker.py`
- `embeddings.py`
- `semantic_indexer.py`
- `question_answering.py`
- `document_pipeline.py`

## Flujo de procesamiento documental

### 1. Ingesta

`POST /api/documents/upload/`

- valida tipo de archivo
- guarda el archivo en `uploads/`
- crea `Document`
- crea `ProcessingJob`
- encola tarea Celery

### 2. Procesamiento asíncrono

`app/tasks.py` actualiza estados del job y del documento:

- `queued`
- `processing`
- `completed`
- `failed`

### 3. Pipeline documental

`app/services/document_pipeline.py` ejecuta:

1. extracción de texto
2. clasificación
3. resumen
4. extracción de campos
5. reindexación de chunks y embeddings

Si el documento no produce texto utilizable, el flujo no continúa hacia indexación.

### 4. Consulta

Una vez indexado el documento:

- `/api/search/semantic/` recupera chunks relevantes
- `/api/ask/` reutiliza chunks relevantes para construir una respuesta extractiva

## Estructura resumida

```text
app/
  api/
    routes/
  core/
  db/
  models/
  schemas/
  services/
  celery_app.py
  main.py
  tasks.py
```

## Decisiones de diseño

### Rutas delgadas

Los endpoints se mantienen relativamente delgados y delegan trabajo a servicios o tareas. Esto ayuda a:

- testear mejor
- aislar responsabilidades
- mantener el contrato HTTP separado de la lógica de negocio

### Lógica heurística antes que sobreingeniería

Clasificación, resumen y extracción usan reglas simples. No intentan simular un sistema enterprise ni depender de modelos costosos desde el primer día.

Esto hace que el proyecto sea:

- más fácil de entender
- más barato de ejecutar
- más estable para CI y tests

### Asincronía en el punto correcto

El procesamiento documental puede ser pesado. Por eso la subida solo encola trabajo y el pipeline ocurre fuera del request-response principal.

## Testing y validación

El proyecto ya valida varias capas:

- tests de servicios pequeños
- tests de endpoints críticos
- tests del contrato API y errores
- tests deterministas de `/api/search` y `/api/ask` sin dependencias vectoriales reales
- CI con Ruff, migraciones y pytest

## Límites actuales

- no hay OCR
- no hay autenticación
- storage local solamente
- QA extractivo, no generativo
- la calidad de clasificación y extracción depende de reglas

## Qué hace defendible este diseño

- separación por capas razonable
- contrato API consistente
- pipeline visible de extremo a extremo
- uso real de Postgres, Redis, Celery y pgvector
- estrategia de testing pragmática en puntos de mayor valor
