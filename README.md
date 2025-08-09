# Kafka AI Agent - Enhanced Edition with Configurable Prompts

🚀 **Now with Multi-MCP Support & Configurable System Prompts!** 

Intelligent Kafka ecosystem management powered by AI, integrating both **Schema Registry** and **Kafka Brokers** MCP servers with fully customizable AI behavior through configuration files.

## 🎯 Key Features

### **NEW: Configurable System Prompts** ✨
- **YAML-based Configuration**: Customize AI behavior without code changes
- **Environment-Specific Prompts**: Different AI personalities for dev/staging/prod
- **Organization Customization**: Adapt to your company's terminology and policies
- **Dynamic Reloading**: Update prompts at runtime
- **Prompt Templates**: Reusable templates for common operations
- **Risk Tolerance Settings**: Configurable safety levels per environment

### Multi-MCP Integration
- **Dual MCP Servers**: Seamlessly integrates [Kafka Schema Registry MCP](https://github.com/aywengo/kafka-schema-reg-mcp) and [Kafka Brokers MCP](https://github.com/aywengo/kafka-brokers-mcp)
- **Unified Management**: Single interface for schemas, topics, brokers, and consumer groups
- **Cross-Domain Analysis**: Correlate schemas with topics, analyze data pipelines

### Core Capabilities
- 🔍 **Schema Evolution Monitoring** - Track changes with customizable analysis criteria
- 🛡️ **Breaking Change Prevention** - Configurable compatibility checking
- 📚 **Auto-Documentation** - Generate docs with organization-specific templates
- 💬 **Natural Language Queries** - Customizable intent recognition and responses
- 🤖 **Multi-LLM Support** - Anthropic, OpenAI, Google, or self-hosted models

## 📝 Configurable Prompts System

### Quick Example

Configure AI behavior in `prompts.yaml`:

```yaml
# Customize the AI's role and expertise
global:
  role: |
    You are an expert Kafka architect for ACME Corp specializing in:
    - E-commerce event streaming
    - Real-time fraud detection
    - PCI and GDPR compliance

# Environment-specific behavior
environments:
  production:
    tone_adjustment: |
      Be extremely cautious. Always provide rollback procedures.
    risk_tolerance: "low"
  
  development:
    tone_adjustment: |
      Be educational and detailed. Explain the reasoning.
    risk_tolerance: "high"

# Operation-specific prompts
operations:
  schema_analysis:
    evaluation_criteria: |
      Evaluate based on:
      1. PCI compliance for payment fields
      2. GDPR requirements for PII
      3. Company naming standards (ACME-SCHEMA-XXX)
      4. Performance SLA requirements
```

### Prompt Customization Features

- **Global Settings**: Define AI role, tone, and constraints
- **Operation Prompts**: Customize prompts for each operation type
- **Environment Overrides**: Different behavior for dev/staging/prod
- **Custom Templates**: Create reusable prompt templates
- **Dynamic Variables**: Template substitution with context variables
- **Chain-of-Thought**: Configurable reasoning strategies

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/aywengo/kafka-ai-agent.git
cd kafka-ai-agent

# Install dependencies
pip install -r requirements.txt

# Install BOTH MCP servers
npm install -g @aywengo/kafka-schema-reg-mcp
npm install -g @aywengo/kafka-brokers-mcp

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Run the Prompt Customization Demo

```bash
# See how configurable prompts work
python examples/prompt_customization_demo.py
```

This interactive demo shows:
- Environment-specific prompt behavior
- Organization customization
- Dynamic prompt building
- Interactive configuration
- Prompt testing and validation

### Use Configurable Agent

```python
from kafka_ai_agent_configurable import ConfigurableKafkaAIAgent

# Initialize with custom prompts
agent = ConfigurableKafkaAIAgent(
    config_path="config.yaml",
    prompts_path="prompts.yaml"  # Your custom prompts
)
await agent.initialize()

# Customize for your organization
org_config = {
    "global": {
        "role": "You are a Kafka expert for FinTech Corp..."
    },
    "operations": {
        "schema_analysis": {
            "evaluation_criteria": "Focus on financial compliance..."
        }
    }
}
await agent.customize_prompts(org_config)

# Use with customized behavior
result = await agent.analyze_schema_with_prompts(
    "payment-events",
    "production"
)
```

### Enhanced CLI with Configurable Prompts

```bash
# Analyze with environment-specific prompts
python cli_enhanced.py ecosystem --environment prod

# The AI will automatically adjust its behavior based on:
# - Environment (cautious in prod, educational in dev)
# - Risk tolerance settings
# - Organization-specific requirements
```

### REST API with Configurable Prompts

```bash
# Start API server
uvicorn api_enhanced:app --reload

# The API automatically uses configured prompts for all operations
```

## 📋 Prompt Configuration Guide

### Structure of prompts.yaml

```yaml
# Global AI configuration
global:
  role: "AI expertise and background"
  tone: "Communication style"
  constraints: "Safety and compliance rules"

# Operation-specific prompts
operations:
  schema_analysis:
    base: "Main prompt for analysis"
    evaluation_criteria: "What to evaluate"
    output_format: "How to structure response"
    context_variables: ["list", "of", "variables"]
  
  schema_evolution:
    compatibility_analysis: "How to check compatibility"
    migration_planning: "How to create migration plans"
    risk_assessment: "How to assess risks"

# Environment configurations
environments:
  production:
    tone_adjustment: "Production-specific tone"
    risk_tolerance: "low"
    additional_context: "Production considerations"
  
  development:
    tone_adjustment: "Dev-specific tone"
    risk_tolerance: "high"
    additional_context: "Development considerations"

# Custom templates
templates:
  error_analysis: |
    Analyze error: ${error_message}
    Context: ${error_context}
  
  capacity_planning: |
    Current: ${current_throughput}
    Growth: ${growth_rate}

# Settings
settings:
  max_tokens: 2000
  temperature: 0.7
  use_chain_of_thought: true
  require_confirmation_for:
    - production_changes
    - delete_operations
```

### Available Operations for Customization

1. **schema_analysis** - Schema evaluation and recommendations
2. **schema_evolution** - Evolution planning and migration
3. **breaking_changes** - Detection and fixes
4. **documentation** - Auto-documentation generation
5. **ecosystem_analysis** - Complete health assessment
6. **pipeline_analysis** - Data flow validation
7. **nlp_query** - Natural language processing
8. **compatibility_fix** - Auto-fix strategies
9. **consumer_impact** - Impact assessment

### Dynamic Variables

Use template variables in prompts:

```yaml
operations:
  schema_analysis:
    base: |
      Analyze schema: ${schema_name}
      Version: ${version}
      Environment: ${environment}
      Consumers: ${downstream_consumers}
```

### Organization-Specific Customization

```python
# Programmatically customize for your organization
ui = PromptConfigurationUI(agent)

# Update AI role
await ui.update_global_role(
    "You are a Kafka expert for Healthcare Corp, "
    "specializing in HIPAA compliance and patient data..."
)

# Set production tone
await ui.set_environment_tone(
    "production",
    "Be extremely cautious with patient data. "
    "Always consider HIPAA requirements."
)

# Add custom template
await ui.add_custom_template(
    "hipaa_check",
    "Verify HIPAA compliance for: ${data_fields}"
)
```

## 🎨 Use Cases for Prompt Configuration

### 1. Compliance-Focused Organization
```yaml
global:
  constraints: |
    - Always check GDPR compliance for EU data
    - Verify PCI DSS for payment fields
    - Ensure SOC2 audit requirements
```

### 2. High-Performance Trading Platform
```yaml
operations:
  schema_analysis:
    evaluation_criteria: |
      - Latency impact (target: <1ms)
      - Message size optimization
      - Compression efficiency
      - Serialization performance
```

### 3. Multi-Team Enterprise
```yaml
environments:
  team_analytics:
    tone_adjustment: "Focus on data science requirements"
  team_platform:
    tone_adjustment: "Focus on infrastructure and reliability"
  team_product:
    tone_adjustment: "Focus on feature delivery speed"
```

## 📊 Complete Feature Set

### Ecosystem Management
- **Comprehensive Analysis**: Full ecosystem health with custom scoring
- **Pipeline Validation**: End-to-end data flow verification
- **Topic-Schema Alignment**: Automated correlation and validation
- **Consumer Intelligence**: Impact analysis with custom criteria

### Schema Operations
- **Evolution Planning**: Customizable migration strategies
- **Compatibility Checking**: Configurable rule sets
- **Auto-Documentation**: Template-based generation
- **Breaking Change Detection**: Custom detection rules

### Monitoring & Alerting
- **Real-time Monitoring**: WebSocket updates with custom alerts
- **Health Scoring**: Configurable scoring algorithms
- **Risk Assessment**: Environment-specific thresholds
- **Alert Routing**: Custom notification channels

## 🔧 Advanced Configuration

### Prompt Testing
```python
# Test prompts before deployment
ui = PromptConfigurationUI(agent)

prompt = await ui.test_prompt(
    PromptOperation.SCHEMA_EVOLUTION,
    "Test input for evolution",
    environment="production"
)
print(f"Generated prompt: {prompt}")
```

### Dynamic Reload
```python
# Reload prompts without restart
await agent.reload_prompts()
```

### Prompt Builder
```python
from prompt_manager import PromptBuilder

builder = PromptBuilder(agent.prompt_manager)
prompt = (builder
    .with_operation(PromptOperation.SCHEMA_EVOLUTION)
    .with_environment("production")
    .with_variables(
        subject="critical-events",
        consumer_count=50,
        business_criticality="CRITICAL"
    )
    .add_section("Special considerations...")
    .build("Evaluate schema change"))
```

## 📚 Documentation

- [Prompt Configuration Guide](docs/PROMPTS.md)
- [API Reference](docs/API.md)
- [Setup Guide](docs/SETUP.md)
- [Examples](examples/)

## 🎯 Benefits of Configurable Prompts

1. **No Code Changes**: Modify AI behavior through configuration
2. **Environment Awareness**: Different behavior for dev/staging/prod
3. **Organization Alignment**: Match your company's terminology and policies
4. **Compliance Ready**: Built-in support for regulatory requirements
5. **Team Customization**: Different prompts for different teams
6. **Rapid Iteration**: Test and refine prompts without deployment
7. **Consistency**: Standardized AI responses across the organization

## 🚀 Getting Started

1. **Run the Demo**: `python examples/prompt_customization_demo.py`
2. **Customize prompts.yaml**: Add your organization's requirements
3. **Test Your Prompts**: Use the testing utilities
4. **Deploy**: Start using customized AI behavior

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Kafka Schema Registry MCP Server](https://github.com/aywengo/kafka-schema-reg-mcp)
- [Kafka Brokers MCP Server](https://github.com/aywengo/kafka-brokers-mcp)
- Model Context Protocol (MCP) by Anthropic
- LLM providers: Anthropic, OpenAI, Google

---

**⭐ Star this repo if you find it helpful!**

**🔥 The most flexible and customizable Kafka AI Agent available!**