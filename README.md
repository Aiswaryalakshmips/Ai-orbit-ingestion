## Deployed API

The FastAPI service is deployed and publicly accessible on Render.

**Base URL**

https://ai-orbit-ingestion-ucgh.onrender.com

**Interactive API Documentation**

https://ai-orbit-ingestion-ucgh.onrender.com/docs

**OpenAPI Specification**

https://ai-orbit-ingestion-ucgh.onrender.com/openapi.json

### Available Endpoints

| Method | Endpoint            | Description                                   |
| ------ | ------------------- | --------------------------------------------- |
| GET    | `/`                 | API root                                      |
| GET    | `/health`           | Returns service health and dataset statistics |
| GET    | `/entities`         | Returns the processed entity dataset          |
| GET    | `/relationships`    | Returns extracted entity relationships        |
| GET    | `/entities/sampled` | Returns the representative sampled dataset    |

### Deployment Verification

The deployed API was successfully tested through the interactive Swagger documentation.

Current health response:

```json
{
  "status": "healthy",
  "entities": 349,
  "relationships": 140,
  "sampled_entities": 271
}
```

All documented API endpoints return successful responses from the deployed service.

The API is implemented using FastAPI and served with Uvicorn.
