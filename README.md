# Kafka AI Agent - Enhanced Edition

🚀 **Now with Multi-MCP Support!** Intelligent Kafka ecosystem management powered by AI, integrating both **Schema Registry** and **Kafka Brokers** MCP servers for comprehensive control.

## 🎯 New Enhanced Features

### Multi-MCP Integration
- **Dual MCP Servers**: Seamlessly integrates [Kafka Schema Registry MCP](https://github.com/aywengo/kafka-schema-reg-mcp) and [Kafka Brokers MCP](https://github.com/aywengo/kafka-brokers-mcp)
- **Unified Management**: Single interface for schemas, topics, brokers, and consumer groups
- **Cross-Domain Analysis**: Correlate schemas with topics, analyze data pipelines, and validate message compliance

### Comprehensive Ecosystem Management
- 🔍 **Ecosystem Health Analysis** - Complete health scoring across schemas, topics, and consumer groups
- 🔄 **Data Pipeline Analysis** - Track data flow across multiple topics with compatibility checking
- 📊 **Topic-Schema Alignment** - Ensure every topic has proper schema coverage
- 🎯 **Consumer Group Intelligence** - Analyze consumer patterns with schema awareness
- 📈 **Performance Optimization** - AI-driven bottleneck detection and recommendations

## Features

### Core Capabilities (Original)
- 🔍 **Schema Evolution Monitoring** - Track changes and suggest improvements
- 🛡️ **Breaking Change Prevention** - Detect compatibility issues before production
- 📚 **Auto-Documentation** - Generate comprehensive docs using AI
- 💬 **Natural Language Queries** - Query your Kafka ecosystem in plain English
- 🤖 **Multi-LLM Support** - Anthropic, OpenAI, Google, or self-hosted models

### Enhanced Capabilities (New)
- 🌐 **Complete Topology Mapping** - Visualize entire Kafka ecosystem
- 🔗 **Data Lineage Tracking** - Understand data flow from source to sink
- ⚡ **Real-time Health Monitoring** - WebSocket-based live updates
- 🔧 **Auto-fix Compatibility** - AI-powered schema compatibility resolution
- 📖 **Data Catalog Generation** - Comprehensive documentation with business context

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Access to Kafka infrastructure
- LLM API keys (Anthropic/OpenAI/Google)

### Installation

```bash
# Clone repository
git clone https://github.com/aywengo/kafka-ai-agent.git
cd kafka-ai-agent

# Install Python dependencies
pip install -r requirements.txt

# Install BOTH MCP servers
npm install -g @aywengo/kafka-schema-reg-mcp
npm install -g @aywengo/kafka-brokers-mcp

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Enhanced CLI Usage

```bash
# Analyze entire ecosystem
python cli_enhanced.py ecosystem --environment prod

# Analyze data pipeline
python cli_enhanced.py pipeline \
  --name "user-journey" \
  --topics "user-events,user-profiles,user-analytics"

# Manage schema evolution with auto-fix
python cli_enhanced.py evolve \
  --subject user-events \
  --changes-file changes.json \
  --auto-fix

# Check topic health
python cli_enhanced.py health --topic user-events

# Generate data catalog
python cli_enhanced.py catalog \
  --environment prod \
  --output catalog.md \
  --format markdown

# Start comprehensive monitoring
python cli_enhanced.py monitor --interval 30
```

### Enhanced API Usage

Start the enhanced API server:
```bash
uvicorn api_enhanced:app --reload --port 8000
```

#### New API Endpoints

```bash
# Comprehensive ecosystem analysis
curl -X POST http://localhost:8000/api/v2/ecosystem/analysis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environment": "prod"}'

# Analyze data pipeline
curl -X POST http://localhost:8000/api/v2/pipeline/analysis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_name": "user-journey",
    "topic_chain": ["user-events", "user-profiles", "user-analytics"],
    "environment": "prod"
  }'

# Topic health check with schema validation
curl -X POST http://localhost:8000/api/v2/topic/health-check \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "user-events", "validate_messages": true}'

# Generate data catalog
curl -X POST http://localhost:8000/api/v2/catalog/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environment": "prod", "include_documentation": true}'
```

### WebSocket Monitoring

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitoring');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Ecosystem Update:', data);
  // data.health_score, data.issues, etc.
};
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Enhanced AI Agent                         │
├───────────────────────────────────────────────────────────────┤
│  • Natural Language Processing                               │
│  • Cross-MCP Orchestration                                   │
│  • Intelligent Analysis & Recommendations                    │
└─────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│   Schema Registry MCP    │   │    Kafka Brokers MCP     │
├─────────────────────────┤   ├─────────────────────────┤
│ • Schema CRUD           │   │ • Topic Management      │
│ • Compatibility Check   │   │ • Consumer Groups       │
│ • Evolution Workflows   │   │ • Broker Operations     │
│ • Migration Tools       │   │ • Performance Metrics   │
└─────────────────────────┘   └─────────────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Kafka Infrastructure                       │
├────────────────┬──────────────────┬──────────────────────────┤
│    Brokers     │  Schema Registry  │    Consumer Groups       │
└────────────────┴──────────────────┴──────────────────────────┘
```

## Docker Deployment

```yaml
# docker-compose.yml includes all services
docker-compose up -d

# Access services
# API: http://localhost:8000
# Prometheus: http://localhost:9091
# Grafana: http://localhost:3000
```

## Configuration

Update `config.yaml` for multi-MCP setup:

```yaml
mcp_servers:
  schema_registry:
    enabled: true
    command: npx
    args: ["-y", "@aywengo/kafka-schema-reg-mcp"]
  kafka_brokers:
    enabled: true
    command: npx
    args: ["-y", "@aywengo/kafka-brokers-mcp"]

environments:
  dev:
    registry_url: "http://localhost:8081"
    broker_urls: ["localhost:9092"]
  prod:
    registry_url: "http://prod-registry:8081"
    broker_urls: ["prod-broker1:9092", "prod-broker2:9092"]
```

## Use Cases

### 1. Complete Ecosystem Health Check
```python
# Analyze entire Kafka ecosystem
analysis = await agent.comprehensive_ecosystem_analysis("prod")
print(f"Health Score: {analysis.health_score}%")
print(f"Risks: {analysis.risk_assessment}")
```

### 2. Data Pipeline Validation
```python
# Validate data pipeline compatibility
pipeline = await agent.analyze_data_pipeline(
    "user-journey",
    ["user-events", "user-enriched", "user-analytics"],
    "prod"
)
```

### 3. Intelligent Schema Evolution
```python
# Evolve schema with impact analysis
evolution = await agent.intelligent_schema_evolution(
    "user-events",
    {"add_fields": [{"name": "session_id", "type": "string"}]},
    "prod"
)
```

### 4. Topic-Schema Health Monitoring
```python
# Check topic health with schema validation
health = await agent.topic_schema_health_check("user-events", "prod")
```

## Monitoring & Observability

- **Prometheus Metrics**: Comprehensive metrics for both schemas and brokers
- **Grafana Dashboards**: Pre-built dashboards for ecosystem visualization
- **Real-time Alerts**: Configurable alerts for health degradation
- **WebSocket Streaming**: Live updates for monitoring dashboards

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **WebSocket**: ws://localhost:8000/ws/monitoring

## Testing

```bash
# Run all tests
pytest tests/

# Test MCP connections
pytest tests/test_mcp_manager.py

# Test enhanced features
pytest tests/test_enhanced_agent.py

# Integration tests
pytest tests/integration/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- [ ] Support for additional MCP servers (ksqlDB, Kafka Connect)
- [ ] Schema registry federation support
- [ ] Advanced data lineage visualization
- [ ] ML-based anomaly detection
- [ ] Cost optimization recommendations
- [ ] Automated disaster recovery
- [ ] Schema versioning strategies
- [ ] Compliance and governance features

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- Built on [Kafka Schema Registry MCP Server](https://github.com/aywengo/kafka-schema-reg-mcp)
- Powered by [Kafka Brokers MCP Server](https://github.com/aywengo/kafka-brokers-mcp)
- AI capabilities by Anthropic/OpenAI/Google
- Model Context Protocol (MCP) by Anthropic

## Support

- **Issues**: [GitHub Issues](https://github.com/aywengo/kafka-ai-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aywengo/kafka-ai-agent/discussions)
- **Documentation**: [Full Docs](docs/)

---

**⭐ Star this repo if you find it helpful!**