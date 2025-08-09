# api_enhanced.py
"""
Enhanced REST API Server for Kafka AI Agent
Provides endpoints for complete Kafka ecosystem management
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

from kafka_ai_agent_enhanced import EnhancedKafkaAIAgent, EnhancedSchemaMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Kafka AI Agent API",
    description="Complete Kafka Ecosystem Management with AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Prometheus metrics
request_counter = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])
ecosystem_operations = Counter('ecosystem_operations_total', 'Ecosystem operations', ['operation', 'status'])

# Global agent instance
agent: Optional[EnhancedKafkaAIAgent] = None
monitor: Optional[EnhancedSchemaMonitor] = None


# Request/Response Models
class EcosystemAnalysisRequest(BaseModel):
    environment: str = Field("dev", description="Environment to analyze")
    include_recommendations: bool = Field(True, description="Include AI recommendations")


class DataPipelineRequest(BaseModel):
    pipeline_name: str = Field(..., description="Name of the pipeline")
    topic_chain: List[str] = Field(..., description="Ordered list of topics in pipeline")
    environment: str = Field("dev", description="Environment")


class SchemaEvolutionRequest(BaseModel):
    subject: str = Field(..., description="Schema subject")
    proposed_changes: Dict[str, Any] = Field(..., description="Proposed schema changes")
    environment: str = Field("dev", description="Environment")
    auto_fix: bool = Field(False, description="Automatically fix compatibility issues")


class TopicHealthCheckRequest(BaseModel):
    topic: str = Field(..., description="Topic name")
    environment: str = Field("dev", description="Environment")
    validate_messages: bool = Field(True, description="Validate messages against schema")
    sample_size: int = Field(10, description="Number of messages to validate")


class DataCatalogRequest(BaseModel):
    environment: str = Field("dev", description="Environment")
    include_documentation: bool = Field(True, description="Generate AI documentation")
    format: str = Field("json", description="Output format (json/markdown)")


class TopicCreationRequest(BaseModel):
    topic_name: str = Field(..., description="Topic name")
    partitions: int = Field(3, description="Number of partitions")
    replication_factor: int = Field(2, description="Replication factor")
    schema: Optional[Dict[str, Any]] = Field(None, description="Optional schema to register")
    environment: str = Field("dev", description="Environment")


class ConsumerGroupAnalysisRequest(BaseModel):
    consumer_group: str = Field(..., description="Consumer group ID")
    environment: str = Field("dev", description="Environment")
    include_schemas: bool = Field(True, description="Include schemas for consumed topics")


# Dependency injection
async def get_agent() -> EnhancedKafkaAIAgent:
    """Get or create enhanced agent instance"""
    global agent
    if agent is None:
        agent = EnhancedKafkaAIAgent("config.yaml")
        await agent.initialize()
    return agent


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify JWT token"""
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return credentials.credentials


# Health and metrics endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow(),
        "mcp_servers": {
            "schema_registry": "connected",
            "kafka_brokers": "connected"
        }
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


# Ecosystem analysis endpoints
@app.post("/api/v2/ecosystem/analysis")
async def analyze_ecosystem(
    request: EcosystemAnalysisRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Perform comprehensive ecosystem analysis"""
    try:
        request_counter.labels(endpoint="/ecosystem/analysis", method="POST").inc()
        
        analysis = await agent.comprehensive_ecosystem_analysis(request.environment)
        
        ecosystem_operations.labels(operation="ecosystem_analysis", status="success").inc()
        
        return {
            "timestamp": analysis.timestamp,
            "environment": analysis.environment,
            "health_score": analysis.health_score,
            "schemas_count": len(analysis.schemas),
            "topics_count": len(analysis.topics),
            "consumer_groups_count": len(analysis.consumer_groups),
            "alignment_issues": analysis.alignment_issues,
            "recommendations": analysis.recommendations if request.include_recommendations else [],
            "risk_assessment": analysis.risk_assessment
        }
    except Exception as e:
        ecosystem_operations.labels(operation="ecosystem_analysis", status="error").inc()
        logger.error(f"Ecosystem analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/pipeline/analysis")
async def analyze_pipeline(
    request: DataPipelineRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Analyze a data pipeline across topics"""
    try:
        request_counter.labels(endpoint="/pipeline/analysis", method="POST").inc()
        
        analysis = await agent.analyze_data_pipeline(
            request.pipeline_name,
            request.topic_chain,
            request.environment
        )
        
        ecosystem_operations.labels(operation="pipeline_analysis", status="success").inc()
        
        return {
            "pipeline_name": analysis.pipeline_name,
            "topics": analysis.topics,
            "schemas_count": len(analysis.schemas),
            "compatibility_matrix": analysis.compatibility_matrix,
            "bottlenecks": analysis.bottlenecks,
            "optimization_suggestions": analysis.optimization_suggestions
        }
    except Exception as e:
        ecosystem_operations.labels(operation="pipeline_analysis", status="error").inc()
        logger.error(f"Pipeline analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Schema evolution endpoints
@app.post("/api/v2/schema/evolution")
async def manage_schema_evolution(
    request: SchemaEvolutionRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Intelligently manage schema evolution"""
    try:
        request_counter.labels(endpoint="/schema/evolution", method="POST").inc()
        
        result = await agent.intelligent_schema_evolution(
            request.subject,
            request.proposed_changes,
            request.environment
        )
        
        # Auto-fix if requested and needed
        if request.auto_fix and not result["compatibility"].get("is_compatible", True):
            fix_result = await agent.auto_fix_compatibility_issues(
                request.subject,
                result["proposed_version"],
                request.environment
            )
            result["auto_fix"] = fix_result
        
        ecosystem_operations.labels(operation="schema_evolution", status="success").inc()
        
        return result
    except Exception as e:
        ecosystem_operations.labels(operation="schema_evolution", status="error").inc()
        logger.error(f"Schema evolution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Topic management endpoints
@app.post("/api/v2/topic/health-check")
async def check_topic_health(
    request: TopicHealthCheckRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Perform health check on topic-schema alignment"""
    try:
        request_counter.labels(endpoint="/topic/health-check", method="POST").inc()
        
        health_report = await agent.topic_schema_health_check(
            request.topic,
            request.environment
        )
        
        ecosystem_operations.labels(operation="topic_health_check", status="success").inc()
        
        return health_report
    except Exception as e:
        ecosystem_operations.labels(operation="topic_health_check", status="error").inc()
        logger.error(f"Topic health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/topic/create")
async def create_topic_with_schema(
    request: TopicCreationRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Create a topic and optionally register its schema"""
    try:
        request_counter.labels(endpoint="/topic/create", method="POST").inc()
        
        # Create topic using broker MCP
        topic_result = await agent.unified_client.call_tool(
            "create_topic",
            {
                "topic": request.topic_name,
                "partitions": request.partitions,
                "replication_factor": request.replication_factor,
                "cluster": request.environment
            }
        )
        
        result = {
            "topic_created": True,
            "topic_name": request.topic_name,
            "partitions": request.partitions,
            "replication_factor": request.replication_factor
        }
        
        # Register schema if provided
        if request.schema:
            schema_result = await agent.unified_client.call_tool(
                "register_schema",
                {
                    "subject": f"{request.topic_name}-value",
                    "schema_definition": request.schema,
                    "registry": request.environment
                }
            )
            result["schema_registered"] = True
            result["schema_id"] = schema_result.get("id")
        
        ecosystem_operations.labels(operation="topic_create", status="success").inc()
        
        return result
    except Exception as e:
        ecosystem_operations.labels(operation="topic_create", status="error").inc()
        logger.error(f"Topic creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Consumer group endpoints
@app.post("/api/v2/consumer-group/analysis")
async def analyze_consumer_group(
    request: ConsumerGroupAnalysisRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Analyze consumer group with schema information"""
    try:
        request_counter.labels(endpoint="/consumer-group/analysis", method="POST").inc()
        
        # Get consumer group details
        group_info = await agent.unified_client.call_tool(
            "get_consumer_group",
            {"group_id": request.consumer_group, "cluster": request.environment}
        )
        
        result = {
            "consumer_group": request.consumer_group,
            "state": group_info.get("state"),
            "members": group_info.get("members", []),
            "topics": group_info.get("topics", []),
            "total_lag": group_info.get("total_lag", 0)
        }
        
        # Get schemas if requested
        if request.include_schemas:
            schemas = await agent.unified_client.get_consumer_group_schemas(
                request.consumer_group,
                request.environment
            )
            result["schemas"] = schemas["schemas"]
        
        ecosystem_operations.labels(operation="consumer_group_analysis", status="success").inc()
        
        return result
    except Exception as e:
        ecosystem_operations.labels(operation="consumer_group_analysis", status="error").inc()
        logger.error(f"Consumer group analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data catalog endpoints
@app.post("/api/v2/catalog/generate")
async def generate_data_catalog(
    request: DataCatalogRequest,
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Generate comprehensive data catalog"""
    try:
        request_counter.labels(endpoint="/catalog/generate", method="POST").inc()
        
        catalog = await agent.generate_data_catalog(request.environment)
        
        ecosystem_operations.labels(operation="catalog_generate", status="success").inc()
        
        if request.format == "markdown":
            # Convert to markdown format
            markdown = "# Kafka Data Catalog\n\n"
            markdown += f"**Generated:** {catalog['generated_at']}\n"
            markdown += f"**Environment:** {catalog['environment']}\n\n"
            
            for topic, doc in catalog['documentation'].items():
                markdown += f"## {topic}\n\n{doc}\n\n"
            
            return PlainTextResponse(content=markdown, media_type="text/markdown")
        
        return catalog
    except Exception as e:
        ecosystem_operations.labels(operation="catalog_generate", status="error").inc()
        logger.error(f"Catalog generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Monitoring endpoints
@app.post("/api/v2/monitoring/start")
async def start_enhanced_monitoring(
    interval: int = 60,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """Start enhanced ecosystem monitoring"""
    global monitor
    
    try:
        if monitor is None:
            monitor = EnhancedSchemaMonitor(agent)
        
        background_tasks.add_task(monitor.start_monitoring, interval)
        
        return {
            "status": "monitoring_started",
            "interval": interval,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/monitoring/alerts")
async def get_monitoring_alerts(
    token: str = Depends(verify_token)
):
    """Get current monitoring alerts"""
    global monitor
    
    if monitor is None:
        return {"alerts": [], "monitoring_active": False}
    
    return {
        "alerts": monitor.get_alerts(),
        "monitoring_active": monitor.monitoring,
        "timestamp": datetime.utcnow()
    }


# Utility endpoints
@app.get("/api/v2/tools/available")
async def list_available_tools(
    agent: EnhancedKafkaAIAgent = Depends(get_agent),
    token: str = Depends(verify_token)
):
    """List all available tools from MCP servers"""
    try:
        tools = {
            "schema_registry": [],
            "kafka_brokers": []
        }
        
        if agent.mcp_manager.is_connected():
            # Get tools from each server
            from mcp_manager import MCPServerType
            
            for server_type in MCPServerType:
                if agent.mcp_manager.is_connected(server_type):
                    server_tools = await agent.mcp_manager.get_available_tools(server_type)
                    tools[server_type.value] = server_tools
        
        return {
            "tools": tools,
            "total_tools": sum(len(t) for t in tools.values())
        }
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time monitoring
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/monitoring")
async def websocket_monitoring(
    websocket: WebSocket,
    token: str = Depends(verify_token)
):
    """WebSocket endpoint for real-time monitoring updates"""
    await websocket.accept()
    
    try:
        agent = await get_agent()
        
        while True:
            # Send ecosystem status every 10 seconds
            analysis = await agent.comprehensive_ecosystem_analysis("dev")
            
            await websocket.send_json({
                "type": "ecosystem_update",
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": analysis.health_score,
                "issues": analysis.alignment_issues
            })
            
            await asyncio.sleep(10)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize enhanced agent on startup"""
    logger.info("Starting Enhanced Kafka AI Agent API...")
    global agent
    agent = await get_agent()
    logger.info("Enhanced Kafka AI Agent API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Enhanced Kafka AI Agent API...")
    global monitor
    if monitor:
        monitor.stop_monitoring()
    if agent:
        await agent.mcp_manager.disconnect_all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)