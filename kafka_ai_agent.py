# kafka_ai_agent.py
"""
Kafka AI Agent - Intelligent Schema Registry Management
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# MCP Client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LLM Provider imports
from anthropic import Anthropic
from openai import AsyncOpenAI
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"


@dataclass
class SchemaAnalysis:
    """Results from schema analysis"""
    schema_name: str
    version: int
    compatibility_issues: List[str]
    suggestions: List[str]
    breaking_changes: List[str]
    documentation: str


class KafkaAIAgent:
    """Main AI Agent for Kafka Schema Registry management"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the AI Agent with configuration"""
        self.config = self._load_config(config_path)
        self.mcp_client = None
        self.llm_provider = self._init_llm_provider()
        self.context_memory = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_llm_provider(self):
        """Initialize the configured LLM provider"""
        provider = self.config['llm_providers']['primary']
        
        if provider == LLMProvider.ANTHROPIC.value:
            return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif provider == LLMProvider.OPENAI.value:
            return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == LLMProvider.GOOGLE.value:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            return genai.GenerativeModel('gemini-pro')
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def connect_mcp_server(self):
        """Establish connection to MCP Server"""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@aywengo/kafka-schema-reg-mcp"]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.mcp_client = session
                await session.initialize()
                logger.info("Connected to Kafka Schema Registry MCP Server")
                return session
    
    async def analyze_schema_evolution(self, subject: str, environment: str = "dev") -> SchemaAnalysis:
        """Analyze schema evolution and provide recommendations"""
        if not self.mcp_client:
            await self.connect_mcp_server()
        
        # Get schema versions
        result = await self.mcp_client.call_tool(
            "get_schema_versions",
            {"subject": subject, "registry": environment}
        )
        
        versions = json.loads(result.content[0].text)
        
        # Get latest schema
        latest_schema = await self.mcp_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        
        # Analyze with LLM
        analysis_prompt = f"""
        Analyze this Kafka schema for potential improvements:
        
        Schema: {subject}
        Version: {versions[-1] if versions else 1}
        Definition: {latest_schema.content[0].text}
        
        Please provide:
        1. Potential compatibility issues
        2. Suggestions for improvement
        3. Documentation for each field
        4. Best practices assessment
        """
        
        llm_response = await self._query_llm(analysis_prompt)
        
        # Parse LLM response and create SchemaAnalysis
        return self._parse_analysis_response(subject, versions[-1] if versions else 1, llm_response)
    
    async def detect_breaking_changes(self, subject: str, new_schema: Dict, environment: str = "dev") -> Dict:
        """Detect potential breaking changes before registration"""
        if not self.mcp_client:
            await self.connect_mcp_server()
        
        # Check compatibility
        result = await self.mcp_client.call_tool(
            "check_compatibility",
            {
                "subject": subject,
                "schema_definition": new_schema,
                "registry": environment
            }
        )
        
        compatibility_result = json.loads(result.content[0].text)
        
        if not compatibility_result.get("is_compatible", True):
            # Use LLM to suggest fixes
            fix_prompt = f"""
            The following schema has compatibility issues:
            
            New Schema: {json.dumps(new_schema, indent=2)}
            Issues: {compatibility_result.get('messages', [])}
            
            Suggest how to fix these compatibility issues while maintaining functionality.
            """
            
            fixes = await self._query_llm(fix_prompt)
            
            return {
                "compatible": False,
                "issues": compatibility_result.get('messages', []),
                "suggested_fixes": fixes,
                "safe_evolution_path": await self._generate_evolution_path(subject, new_schema)
            }
        
        return {"compatible": True, "message": "No breaking changes detected"}
    
    async def generate_documentation(self, subject: str, environment: str = "dev") -> str:
        """Generate comprehensive documentation for a schema"""
        if not self.mcp_client:
            await self.connect_mcp_server()
        
        # Get schema
        schema_result = await self.mcp_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        
        schema = json.loads(schema_result.content[0].text)
        
        # Generate documentation with LLM
        doc_prompt = f"""
        Generate comprehensive documentation for this Kafka schema:
        
        Schema Name: {subject}
        Definition: {json.dumps(schema, indent=2)}
        
        Include:
        1. Overview and purpose
        2. Field descriptions with examples
        3. Usage examples
        4. Related schemas
        5. Version history summary
        
        Format as Markdown.
        """
        
        documentation = await self._query_llm(doc_prompt)
        
        # Save documentation
        await self._save_documentation(subject, documentation)
        
        return documentation
    
    async def natural_language_query(self, query: str, environment: str = "dev") -> str:
        """Process natural language queries about schemas"""
        # Enhance query with context
        enhanced_prompt = f"""
        You are a Kafka Schema Registry assistant. 
        
        User Query: {query}
        Environment: {environment}
        
        Available operations:
        - List schemas
        - Check compatibility
        - View schema versions
        - Analyze dependencies
        - Generate migration plans
        
        Determine the user's intent and provide the appropriate response.
        """
        
        # Get LLM interpretation
        intent = await self._query_llm(enhanced_prompt)
        
        # Execute appropriate MCP operations based on intent
        response = await self._execute_intent(intent, environment)
        
        return response
    
    async def _query_llm(self, prompt: str) -> str:
        """Query the configured LLM provider"""
        provider = self.config['llm_providers']['primary']
        
        if provider == LLMProvider.ANTHROPIC.value:
            response = self.llm_provider.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.content[0].text
        
        elif provider == LLMProvider.OPENAI.value:
            response = await self.llm_provider.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        elif provider == LLMProvider.GOOGLE.value:
            response = self.llm_provider.generate_content(prompt)
            return response.text
        
        return "LLM query failed"
    
    async def _generate_evolution_path(self, subject: str, new_schema: Dict) -> List[Dict]:
        """Generate a safe evolution path for schema changes"""
        # Use Schema Evolution Assistant workflow
        if not self.mcp_client:
            await self.connect_mcp_server()
        
        result = await self.mcp_client.call_tool(
            "guided_schema_evolution",
            {"subject": subject, "current_schema": json.dumps(new_schema)}
        )
        
        return json.loads(result.content[0].text)
    
    def _parse_analysis_response(self, subject: str, version: int, llm_response: str) -> SchemaAnalysis:
        """Parse LLM response into SchemaAnalysis object"""
        # Simple parsing - in production, use structured output
        return SchemaAnalysis(
            schema_name=subject,
            version=version,
            compatibility_issues=[],  # Parse from llm_response
            suggestions=[],  # Parse from llm_response
            breaking_changes=[],  # Parse from llm_response
            documentation=llm_response
        )
    
    async def _save_documentation(self, subject: str, documentation: str):
        """Save generated documentation"""
        doc_path = f"docs/schemas/{subject}.md"
        os.makedirs(os.path.dirname(doc_path), exist_ok=True)
        with open(doc_path, 'w') as f:
            f.write(documentation)
        logger.info(f"Documentation saved for {subject}")
    
    async def _execute_intent(self, intent: str, environment: str) -> str:
        """Execute operations based on interpreted intent"""
        # This would map intents to specific MCP operations
        # Simplified example:
        if "list" in intent.lower():
            result = await self.mcp_client.call_tool(
                "list_subjects",
                {"registry": environment}
            )
            return f"Available schemas: {result.content[0].text}"
        
        return "Operation completed"


class SchemaMonitor:
    """Monitor schemas for changes and trigger actions"""
    
    def __init__(self, agent: KafkaAIAgent):
        self.agent = agent
        self.monitoring = False
        
    async def start_monitoring(self, interval: int = 60):
        """Start monitoring schemas for changes"""
        self.monitoring = True
        logger.info("Starting schema monitoring...")
        
        while self.monitoring:
            try:
                await self._check_schemas()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
    
    async def _check_schemas(self):
        """Check all schemas for changes"""
        # Implementation for checking schema changes
        pass
    
    def stop_monitoring(self):
        """Stop monitoring schemas"""
        self.monitoring = False
        logger.info("Schema monitoring stopped")


# CLI Interface
async def main():
    """Main CLI interface for the Kafka AI Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kafka AI Agent for Schema Registry Management")
    parser.add_argument("command", choices=["analyze", "check", "document", "query", "monitor"])
    parser.add_argument("--subject", help="Schema subject name")
    parser.add_argument("--environment", default="dev", help="Environment (dev/staging/prod)")
    parser.add_argument("--query", help="Natural language query")
    parser.add_argument("--schema-file", help="Path to new schema file")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = KafkaAIAgent()
    
    if args.command == "analyze":
        result = await agent.analyze_schema_evolution(args.subject, args.environment)
        print(f"Analysis for {args.subject}:")
        print(f"Suggestions: {result.suggestions}")
        
    elif args.command == "check":
        with open(args.schema_file, 'r') as f:
            new_schema = json.load(f)
        result = await agent.detect_breaking_changes(args.subject, new_schema, args.environment)
        print(f"Compatibility Check: {result}")
        
    elif args.command == "document":
        doc = await agent.generate_documentation(args.subject, args.environment)
        print(f"Documentation generated:\n{doc}")
        
    elif args.command == "query":
        response = await agent.natural_language_query(args.query, args.environment)
        print(f"Response: {response}")
        
    elif args.command == "monitor":
        monitor = SchemaMonitor(agent)
        await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())