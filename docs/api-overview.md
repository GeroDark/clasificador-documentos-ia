# API Overview

## Objetivo

La API expone un flujo completo para:

- cargar documentos
- consultar estado de procesamiento
- recuperar resultados estructurados
- buscar por significado
- hacer preguntas sobre el contenido

## Módulos principales

### Health

- `GET /health/live`
- `GET /health/ready`

Sirven para verificar que la API está levantada y que las dependencias principales responden.

### Documents

- `POST /api/documents/`
- `POST /api/documents/upload/`
- `GET /api/documents/`
- `GET /api/documents/{document_id}`
- `GET /api/documents/{document_id}/text`
- `GET /api/documents/{document_id}/classification`
- `GET /api/documents/{document_id}/summary`
- `GET /api/documents/{document_id}/fields`
- `GET /api/documents/{document_id}/chunks`

Este módulo concentra el ciclo de vida documental y la lectura de resultados persistidos.

### Jobs

- `GET /api/jobs/`
- `GET /api/jobs/{job_id}/status`

Permite consultar el procesamiento asíncrono.

### Search

- `GET /api/search/semantic/`

Recupera chunks relevantes según similitud semántica.

### Ask

- `POST /api/ask/`
- `GET /api/ask/logs/`

Permite responder preguntas sobre documentos y consultar el historial de queries registradas.

## Contrato HTTP

### Respuestas exitosas

Los endpoints principales usan `response_model` explícitos para:

- documentos
- jobs
- resultados de búsqueda
- respuestas de QA
- health checks estructurados

### Errores controlados

La API usa un formato consistente para errores controlados:

```json
{
  "code": "not_found",
  "message": "Job no encontrado.",
  "details": null
}
```

Para errores de validación:

```json
{
  "code": "validation_error",
  "message": "La solicitud no cumple el contrato esperado.",
  "details": [
    {
      "loc": ["query", "q"],
      "message": "String should have at least 2 characters",
      "type": "string_too_short"
    }
  ]
}
```

## Flujo recomendado de uso

### 1. Subir documento

`POST /api/documents/upload/`

Devuelve un `ProcessingJobResponse` con estado `queued`.

### 2. Consultar estado del job

`GET /api/jobs/{job_id}/status`

Cuando el job termina, el documento ya debería tener resultados persistidos o un fallo explícito.

### 3. Consultar resultados

- texto
- clasificación
- resumen
- campos
- chunks

### 4. Buscar o preguntar

- `GET /api/search/semantic/`
- `POST /api/ask/`

## Qué está validado por tests

- endpoints críticos de documentos y jobs
- contrato de errores
- cobertura determinista de `/api/search` y `/api/ask`

Esto permite mantener la API más estable sin depender de modelos externos o búsquedas vectoriales reales en cada test.
