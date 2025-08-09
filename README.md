# Kafka AI Agent

Intelligent Kafka Schema Registry Management with AI - Monitors schema evolution, prevents breaking changes, auto-generates documentation, and provides natural language queries.

## Features

- 🔍 **Schema Evolution Monitoring** - Track schema changes and suggest improvements
- 🛡️ **Breaking Change Prevention** - Detect and prevent compatibility issues before they reach production
- 📚 **Auto-Documentation** - Generate comprehensive documentation from schemas using AI
- 💬 **Natural Language Queries** - Query your schemas using plain English
- 🔄 **Multi-Environment Support** - Manage dev/staging/prod environments seamlessly
- 🤖 **Multi-LLM Support** - Works with Anthropic, OpenAI, Google, or self-hosted models

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+ (for MCP server)
- Access to Kafka Schema Registry
- API key for LLM provider (Anthropic/OpenAI/Google)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aywengo/kafka-ai-agent.git
cd kafka-ai-agent
```

2. **Install dependencies**
```bash
# Python dependencies
pip install -r requirements.txt

# MCP Server
npm install -g @aywengo/kafka-schema-reg-mcp
```

3. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Add your LLM API keys and Schema Registry URLs
```

4. **Run the agent**
```bash
# CLI mode
python kafka_ai_agent.py analyze --subject user-events --environment dev

# Start API server
uvicorn api:app --reload --port 8000
```

## Documentation

See [docs/](docs/) for full documentation including:
- [Setup Guide](docs/SETUP.md)
- [API Reference](docs/API.md)
- [Configuration Guide](docs/CONFIG.md)
- [Deployment Options](docs/DEPLOYMENT.md)

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/aywengo/kafka-ai-agent/issues)
- Based on [Kafka Schema Registry MCP Server](https://github.com/aywengo/kafka-schema-reg-mcp)

## License

MIT License - see [LICENSE](LICENSE) file for details.