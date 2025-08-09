# Kafka AI Agent - API Reference

## Overview

The Kafka AI Agent provides a RESTful API for managing Kafka schemas with AI-powered capabilities.

Base URL: `http://localhost:8000`

## Authentication

All API endpoints require Bearer token authentication:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

## Endpoints

### Health Check

#### GET /health

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Schema Analysis

#### POST /api/v1/analyze

Analyze a schema and get AI-powered recommendations.

**Request Body:**
```json
{
  "subject": "user-events",
  "environment": "dev"
}
```

**Response:**
```json
{
  "subject": "user-events",
  "version": 3,
  "compatibility_issues": [],
  "suggestions": [
    "Consider adding field documentation",
    "Field 'timestamp' should use logical type 'timestamp-millis'"
  ],
  "breaking_changes": [],
  "documentation": "Generated documentation...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Compatibility Check

#### POST /api/v1/check-compatibility

Check if a new schema version is compatible.

**Request Body:**
```json
{
  "subject": "user-events",
  "schema": {
    "type": "record",
    "name": "UserEvent",
    "fields": [...]
  },
  "environment": "dev"
}
```

**Response:**
```json
{
  "compatible": true,
  "issues": [],
  "suggested_fixes": null,
  "safe_evolution_path": null
}
```

### Documentation Generation

#### POST /api/v1/generate-documentation

Generate documentation for a schema.

**Request Body:**
```json
{
  "subject": "user-events",
  "environment": "dev",
  "format": "markdown"
}
```

**Response:**
```json
{
  "subject": "user-events",
  "documentation": "# User Events Schema\n\n...",
  "format": "markdown",
  "generated_at": "2024-01-01T00:00:00Z"
}
```

### Natural Language Query

#### POST /api/v1/query

Query schemas using natural language.

**Request Body:**
```json
{
  "query": "What schemas depend on user-events?",
  "environment": "dev"
}
```

**Response:**
```json
{
  "query": "What schemas depend on user-events?",
  "response": "The following schemas depend on user-events: order-events, payment-events",
  "environment": "dev",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### List Schemas

#### GET /api/v1/schemas

List all schemas in an environment.

**Query Parameters:**
- `environment` (string, default: "dev"): Environment to query

**Response:**
```json
{
  "environment": "dev",
  "schemas": ["user-events", "order-events", "payment-events"],
  "count": 3
}
```

### Get Schema Versions

#### GET /api/v1/schemas/{subject}/versions

Get all versions of a schema.

**Path Parameters:**
- `subject` (string): Schema subject name

**Query Parameters:**
- `environment` (string, default: "dev"): Environment to query

**Response:**
```json
{
  "subject": "user-events",
  "environment": "dev",
  "versions": [1, 2, 3]
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### Common Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per API key

## Metrics

#### GET /metrics

Prometheus metrics endpoint.

**Response:** Prometheus text format

## WebSocket Support

For real-time schema monitoring:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Schema change:', data);
};
```

## SDK Examples

### Python

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/api/v1/analyze',
    json={'subject': 'user-events', 'environment': 'dev'},
    headers=headers
)

print(response.json())
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    subject: 'user-events',
    environment: 'dev'
  })
});

const data = await response.json();
console.log(data);
```

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subject": "user-events", "environment": "dev"}'
```