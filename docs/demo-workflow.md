# Demo API Workflow

Esta guia muestra el flujo minimo para evaluar el backend localmente sin frontend y sin datos sensibles.

## Credenciales demo locales

Usa estas credenciales solo en desarrollo local:

- `email`: `demo@example.com`
- `password`: `DemoPass123!`

El script incluido crea ese usuario o resetea su password para que la demo sea repetible.

## Flujo rapido

### 1. Levantar servicios base

```bash
docker compose up -d
```

Servicios esperados:

- PostgreSQL + `pgvector` en `127.0.0.1:5433`
- Redis en `127.0.0.1:6379`

### 2. Aplicar migraciones

```bash
alembic upgrade head
```

### 3. Crear o resetear el usuario demo

```bash
python -m app.scripts.create_demo_user
```

Tambien puedes personalizarlo:

```bash
python -m app.scripts.create_demo_user --email demo@example.com --password DemoPass123! --full-name "Demo Local User"
```

### 4. Levantar la API

```bash
uvicorn app.main:app --reload
```

### 5. Levantar el worker de Celery

```bash
celery -A app.celery_app:celery_app worker --pool=solo --loglevel=info
```

### 6. Hacer login

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@example.com\",\"password\":\"DemoPass123!\"}"
```

Guarda el `access_token` de la respuesta para los siguientes requests.

### 7. Subir un documento demo

Archivo de ejemplo incluido:

- [docs/demo-files/demo-propuesta.txt](/c:/Proyectos%20CV/clasificador-documentos-ia/docs/demo-files/demo-propuesta.txt)

Request:

```bash
curl -X POST "http://127.0.0.1:8000/api/documents/upload/" \
  -H "Authorization: Bearer TU_TOKEN" \
  -F "file=@docs/demo-files/demo-propuesta.txt;type=text/plain"
```

La respuesta devuelve el `job_id` y el `document_id`.

### 8. Consultar el job

```bash
curl "http://127.0.0.1:8000/api/jobs/JOB_ID/status" \
  -H "Authorization: Bearer TU_TOKEN"
```

Cuando el estado sea `completed`, el documento ya deberia estar disponible para lectura, busqueda y preguntas.

### 9. Ejecutar busqueda semantica

```bash
curl "http://127.0.0.1:8000/api/search/semantic/?q=garantia%20de%20servicio&limit=3" \
  -H "Authorization: Bearer TU_TOKEN"
```

### 10. Hacer una pregunta

```bash
curl -X POST "http://127.0.0.1:8000/api/ask/" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Cual es el monto referencial?\",\"document_id\":1,\"top_k\":3}"
```

## Coleccion de requests

Quedo una coleccion lista para probar el flujo desde clientes compatibles con archivos `.http`:

- [docs/requests/demo-api.http](/c:/Proyectos%20CV/clasificador-documentos-ia/docs/requests/demo-api.http)

Incluye:

- health check
- login
- `me`
- upload
- job status
- listado de documentos
- busqueda semantica
- pregunta sobre documento
- logs de preguntas

## Limites de esta demo

- La indexacion semantica depende de que el worker de Celery procese el documento.
- Las credenciales demo son solo para desarrollo local; no deben reutilizarse en entornos compartidos.
- El archivo incluido es un ejemplo controlado para mostrar el flujo, no un dataset real.
