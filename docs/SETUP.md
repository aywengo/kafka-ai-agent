# Kafka AI Agent - Setup Guide

## Prerequisites

### System Requirements
- Python 3.9 or higher
- Node.js 16 or higher
- Docker (optional, for containerized deployment)
- At least 4GB RAM
- 10GB free disk space

### Required Access
- Kafka Schema Registry instances (dev/staging/prod)
- API keys for at least one LLM provider:
  - Anthropic Claude API
  - OpenAI API
  - Google Gemini API
  - Local Ollama instance

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/aywengo/kafka-ai-agent.git
cd kafka-ai-agent
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Install MCP Server

The Kafka Schema Registry MCP Server is required for schema operations:

```bash
# Install globally
npm install -g @aywengo/kafka-schema-reg-mcp

# Or use npx (no installation needed)
npx @aywengo/kafka-schema-reg-mcp
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# At least one LLM provider key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Schema Registry URLs
SCHEMA_REGISTRY_DEV_URL=http://localhost:8081
SCHEMA_REGISTRY_STAGING_URL=http://staging-registry:8081
SCHEMA_REGISTRY_PROD_URL=http://prod-registry:8081
```

### 5. Configure Application Settings

Edit `config.yaml` to match your environment:

```yaml
environments:
  dev:
    registry_url: "http://localhost:8081"
    context: "development"
    compatibility: "BACKWARD"
  staging:
    registry_url: "http://staging-registry:8081"
    context: "staging"
    compatibility: "BACKWARD"
  production:
    registry_url: "http://prod-registry:8081"
    context: "production"
    compatibility: "FULL"

llm_providers:
  primary: "anthropic"  # Choose your primary provider
  fallback: "openai"    # Fallback if primary fails
```

## Running the Application

### CLI Mode

```bash
# Analyze a schema
python kafka_ai_agent.py analyze --subject user-events --environment dev

# Check compatibility
python kafka_ai_agent.py check --subject user-events --schema-file new-schema.json

# Generate documentation
python kafka_ai_agent.py document --subject user-events

# Natural language query
python kafka_ai_agent.py query --query "What schemas have changed today?"

# Start monitoring
python kafka_ai_agent.py monitor --environment prod
```

### API Server

```bash
# Start the API server
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Access the API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t kafka-ai-agent .
docker run -p 8000:8000 --env-file .env kafka-ai-agent
```

## Verification

### 1. Test MCP Server Connection

```bash
# Test MCP server is accessible
npx @aywengo/kafka-schema-reg-mcp --test
```

### 2. Test Schema Registry Connection

```bash
# Test Schema Registry connectivity
curl http://localhost:8081/subjects
```

### 3. Test API Server

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "timestamp": "..."}
```

### 4. Test LLM Provider

```python
# test_llm.py
from kafka_ai_agent import KafkaAIAgent

agent = KafkaAIAgent()
response = await agent._query_llm("Test prompt")
print(response)
```

## Troubleshooting

### Common Issues

#### MCP Server Connection Failed
```
Error: Cannot connect to MCP server
```
**Solution:**
- Ensure Node.js is installed: `node --version`
- Check MCP server is installed: `npm list -g @aywengo/kafka-schema-reg-mcp`
- Verify network connectivity

#### Schema Registry Unreachable
```
Error: Connection to Schema Registry failed
```
**Solution:**
- Check Schema Registry URL in config.yaml
- Verify Schema Registry is running: `curl http://localhost:8081/subjects`
- Check firewall/network rules

#### LLM API Errors
```
Error: Invalid API key
```
**Solution:**
- Verify API keys in .env file
- Check API key permissions and quotas
- Ensure fallback provider is configured

#### Memory Issues
```
Error: Out of memory
```
**Solution:**
- Increase Python heap size: `export PYTHONMAXHEAP=4g`
- Use Docker with memory limits: `docker run -m 4g ...`
- Enable pagination for large result sets

## Next Steps

1. **Configure Monitoring**: Set up Prometheus and Grafana for metrics
2. **Set Up Authentication**: Configure JWT tokens for API security
3. **Create Documentation**: Generate initial schema documentation
4. **Configure Alerts**: Set up Slack/email notifications
5. **Integrate CI/CD**: Add pre-commit hooks for schema validation

## Support

For issues or questions:
- GitHub Issues: https://github.com/aywengo/kafka-ai-agent/issues
- Documentation: https://github.com/aywengo/kafka-ai-agent/docs