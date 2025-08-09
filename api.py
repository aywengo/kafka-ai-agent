# api.py
"""
REST API Server for Kafka AI Agent
Provides HTTP endpoints for schema management operations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

from kafka_ai_agent import KafkaAIAgent, SchemaMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Kafka AI Agent API",
    description="Intelligent Schema Registry Management with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Prometheus metrics
request_counter = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])
schema_operations = Counter('schema_operations_total', 'Schema operations', ['operation', 'status'])

# Global agent instance
agent: Optional[KafkaAIAgent] = None
monitor: Optional[SchemaMonitor] = None


# Pydantic models for request/response
class SchemaAnalysisRequest(BaseModel):
    subject: str = Field(..., description="Schema subject name")
    environment: str = Field("dev", description="Environment (dev/staging/prod)")


class CompatibilityCheckRequest(BaseModel):
    subject: str = Field(..., description="Schema subject name")
    schema: Dict[str, Any] = Field(..., description="New schema definition")
    environment: str = Field("dev", description="Environment")


class DocumentationRequest(BaseModel):
    subject: str = Field(..., description="Schema subject name")
    environment: str = Field("dev", description="Environment")
    format: str = Field("markdown", description="Documentation format")


class NaturalLanguageQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    environment: str = Field("dev", description="Environment")
    context: Optional[Dict] = Field(None, description="Additional context")


# Dependency injection
async def get_agent() -> KafkaAIAgent:
    """Get or create agent instance"""
    global agent
    if agent is None:
        agent = KafkaAIAgent("config.yaml")
        await agent.connect_mcp_server()
    return agent


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify JWT token (simplified - implement proper JWT validation)"""
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


# Schema analysis endpoints
@app.post("/api/v1/analyze")
async def analyze_schema(
    request: SchemaAnalysisRequest,
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Analyze schema evolution and provide AI-powered recommendations"""
    try:
        request_counter.labels(endpoint="/analyze", method="POST").inc()
        
        result = await agent.analyze_schema_evolution(
            request.subject,
            request.environment
        )
        
        schema_operations.labels(operation="analyze", status="success").inc()
        
        return {
            "subject": result.schema_name,
            "version": result.version,
            "compatibility_issues": result.compatibility_issues,
            "suggestions": result.suggestions,
            "breaking_changes": result.breaking_changes,
            "documentation": result.documentation,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        schema_operations.labels(operation="analyze", status="error").inc()
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/check-compatibility")
async def check_compatibility(
    request: CompatibilityCheckRequest,
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Check schema compatibility and detect breaking changes"""
    try:
        request_counter.labels(endpoint="/check-compatibility", method="POST").inc()
        
        result = await agent.detect_breaking_changes(
            request.subject,
            request.schema,
            request.environment
        )
        
        schema_operations.labels(operation="compatibility_check", status="success").inc()
        
        return result
    except Exception as e:
        schema_operations.labels(operation="compatibility_check", status="error").inc()
        logger.error(f"Compatibility check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate-documentation")
async def generate_documentation(
    request: DocumentationRequest,
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Generate AI-powered documentation for schemas"""
    try:
        request_counter.labels(endpoint="/generate-documentation", method="POST").inc()
        
        documentation = await agent.generate_documentation(
            request.subject,
            request.environment
        )
        
        schema_operations.labels(operation="document", status="success").inc()
        
        return {
            "subject": request.subject,
            "documentation": documentation,
            "format": request.format,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        schema_operations.labels(operation="document", status="error").inc()
        logger.error(f"Documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query")
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Process natural language queries about schemas"""
    try:
        request_counter.labels(endpoint="/query", method="POST").inc()
        
        response = await agent.natural_language_query(
            request.query,
            request.environment
        )
        
        return {
            "query": request.query,
            "response": response,
            "environment": request.environment,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Schema information endpoints
@app.get("/api/v1/schemas")
async def list_schemas(
    environment: str = "dev",
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """List all schemas in an environment"""
    try:
        if agent.mcp_client:
            result = await agent.mcp_client.call_tool(
                "list_subjects",
                {"registry": environment}
            )
            
            subjects = json.loads(result.content[0].text)
            
            return {
                "environment": environment,
                "schemas": subjects,
                "count": len(subjects)
            }
    except Exception as e:
        logger.error(f"Failed to list schemas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/schemas/{subject}/versions")
async def get_schema_versions(
    subject: str,
    environment: str = "dev",
    agent: KafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Get all versions of a schema"""
    try:
        if agent.mcp_client:
            result = await agent.mcp_client.call_tool(
                "get_schema_versions",
                {"subject": subject, "registry": environment}
            )
            
            versions = json.loads(result.content[0].text)
            
            return {
                "subject": subject,
                "environment": environment,
                "versions": versions
            }
    except Exception as e:
        logger.error(f"Failed to get schema versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    logger.info("Starting Kafka AI Agent API...")
    global agent
    agent = await get_agent()
    logger.info("Kafka AI Agent API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Kafka AI Agent API...")
    global monitor
    if monitor:
        monitor.stop_monitoring()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)