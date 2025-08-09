# kafka_ai_agent_configurable.py
"""
Enhanced Kafka AI Agent with Configurable System Prompts
Supports dynamic prompt customization through configuration files
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# MCP Manager imports
from mcp_manager import MCPManager, UnifiedMCPClient, CrossMCPAnalyzer, MCPServerType

# Prompt Manager imports
from prompt_manager import (
    PromptManager, 
    PromptContext, 
    PromptOperation, 
    PromptBuilder,
    load_prompt_manager
)

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
class ComprehensiveAnalysis:
    """Results from comprehensive Kafka ecosystem analysis"""
    timestamp: datetime
    environment: str
    schemas: Dict[str, Any] = field(default_factory=dict)
    topics: Dict[str, Any] = field(default_factory=dict)
    consumer_groups: Dict[str, Any] = field(default_factory=dict)
    alignment_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    health_score: float = 100.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


class ConfigurableKafkaAIAgent:
    """Enhanced AI Agent with configurable prompts for Kafka ecosystem management"""
    
    def __init__(self, config_path: str = "config.yaml", prompts_path: str = "prompts.yaml"):
        """Initialize the Configurable AI Agent"""
        self.config = self._load_config(config_path)
        self.prompt_manager = load_prompt_manager(prompts_path)
        self.mcp_manager = MCPManager()
        self.unified_client = UnifiedMCPClient(self.mcp_manager)
        self.cross_analyzer = CrossMCPAnalyzer(self.unified_client)
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
    
    async def initialize(self):
        """Initialize all MCP connections"""
        await self.unified_client.initialize()
        logger.info("Configurable Kafka AI Agent initialized")
    
    async def reload_prompts(self):
        """Reload prompts from configuration file"""
        self.prompt_manager.reload_prompts()
        logger.info("Prompts reloaded successfully")
    
    async def customize_prompts(self, org_config: Dict[str, Any]):
        """Customize prompts for a specific organization"""
        self.prompt_manager.customize_for_organization(org_config)
        logger.info("Prompts customized for organization")
    
    async def comprehensive_ecosystem_analysis(self, environment: str = "dev") -> ComprehensiveAnalysis:
        """Perform comprehensive analysis using configured prompts"""
        analysis = ComprehensiveAnalysis(
            timestamp=datetime.utcnow(),
            environment=environment
        )
        
        # Get topology report
        topology = await self.cross_analyzer.generate_topology_report(environment)
        
        analysis.schemas = topology.get("schemas", {})
        analysis.topics = topology.get("topics", {})
        analysis.consumer_groups = topology.get("consumer_groups", {})
        
        # Check alignment
        alignment = await self.unified_client.analyze_topic_schema_alignment(environment)
        
        # Calculate health score and identify issues
        self._calculate_health_score(analysis, alignment)
        
        # Use configured prompts for recommendations
        context = PromptContext(
            operation=PromptOperation.ECOSYSTEM_ANALYSIS,
            environment=environment,
            variables={
                "environment": environment,
                "topics_count": len(analysis.topics),
                "schemas_count": len(analysis.schemas),
                "consumer_groups_count": len(analysis.consumer_groups),
                "alignment_issues": json.dumps(analysis.alignment_issues),
                "topics_with_schemas_percentage": len(alignment["topics_with_schemas"]) / max(len(analysis.topics), 1) * 100,
                "average_consumer_lag": self._calculate_avg_lag(analysis.consumer_groups),
                "under_replicated_partitions": 0,  # Would calculate from topology
                "average_disk_usage": 75,  # Would get from metrics
                "error_rate_per_minute": 0.1,  # Would get from metrics
                "schema_changes_per_week": 5  # Would calculate from history
            }
        )
        
        # Get AI recommendations
        recommendations_prompt = self.prompt_manager.get_full_prompt(
            context,
            f"Analyze this Kafka ecosystem and provide recommendations: {json.dumps(topology, indent=2)[:2000]}"
        )
        
        llm_response = await self._query_llm_with_prompt(recommendations_prompt, context)
        analysis.recommendations = self._parse_recommendations(llm_response)
        
        # Risk assessment
        analysis.risk_assessment = await self._assess_risks_with_prompts(topology, alignment, environment)
        
        return analysis
    
    async def analyze_schema_with_prompts(
        self,
        subject: str,
        environment: str = "dev"
    ) -> Dict[str, Any]:
        """Analyze schema using configured prompts"""
        # Get schema details
        schema_result = await self.unified_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        
        schema = json.loads(schema_result.content[0].text)
        
        # Get versions
        versions_result = await self.unified_client.call_tool(
            "get_schema_versions",
            {"subject": subject, "registry": environment}
        )
        versions = json.loads(versions_result.content[0].text)
        
        # Build context for prompts
        context = PromptContext(
            operation=PromptOperation.SCHEMA_ANALYSIS,
            environment=environment,
            variables={
                "schema_name": subject,
                "version": versions[-1] if versions else 1,
                "environment": environment,
                "compatibility_mode": self._get_compatibility_mode(environment),
                "downstream_consumers": await self._get_consumers_for_topic(subject, environment)
            }
        )
        
        # Get analysis from LLM using configured prompts
        analysis_prompt = self.prompt_manager.get_full_prompt(
            context,
            f"Schema Definition: {json.dumps(schema, indent=2)}"
        )
        
        analysis = await self._query_llm_with_prompt(analysis_prompt, context)
        
        return {
            "subject": subject,
            "version": versions[-1] if versions else 1,
            "analysis": analysis,
            "prompt_context": context.variables
        }
    
    async def intelligent_schema_evolution_with_prompts(
        self,
        subject: str,
        proposed_changes: Dict[str, Any],
        environment: str = "dev"
    ) -> Dict:
        """Manage schema evolution using configured prompts"""
        result = {
            "subject": subject,
            "environment": environment,
            "proposed_changes": proposed_changes
        }
        
        # Get current schema
        current_schema = await self.unified_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        result["current_schema"] = json.loads(current_schema.content[0].text)
        
        # Check compatibility
        new_schema = self._apply_schema_changes(result["current_schema"], proposed_changes)
        compatibility = await self.unified_client.call_tool(
            "check_compatibility",
            {
                "subject": subject,
                "schema_definition": new_schema,
                "registry": environment
            }
        )
        result["compatibility"] = json.loads(compatibility.content[0].text)
        
        # Get affected consumers
        affected_consumers = await self._get_affected_consumers(subject, environment)
        
        # Build context for evolution analysis
        context = PromptContext(
            operation=PromptOperation.SCHEMA_EVOLUTION,
            environment=environment,
            variables={
                "subject": subject,
                "current_version": result["current_schema"].get("version", 1),
                "proposed_changes": json.dumps(proposed_changes),
                "affected_consumers": affected_consumers,
                "consumer_count": len(affected_consumers),
                "environment": environment,
                "compatibility_mode": self._get_compatibility_mode(environment),
                "compatibility_issues": result["compatibility"].get("messages", []),
                "daily_message_volume": 1000000,  # Would get from metrics
                "business_criticality": "HIGH",  # Would get from metadata
                "days_since_last_change": 30  # Would calculate from history
            }
        )
        
        # Get migration plan from LLM
        migration_prompt = self.prompt_manager.get_full_prompt(
            context,
            f"Current Schema: {json.dumps(result['current_schema'], indent=2)[:1000]}\n"
            f"Proposed Changes: {json.dumps(proposed_changes, indent=2)}"
        )
        
        migration_plan = await self._query_llm_with_prompt(migration_prompt, context)
        result["migration_plan"] = self._parse_migration_plan(migration_plan)
        
        # Risk assessment based on environment settings
        risk_tolerance = self.prompt_manager.get_risk_tolerance(environment)
        result["risk_level"] = self._assess_risk_with_tolerance(
            result["compatibility"],
            affected_consumers,
            risk_tolerance
        )
        
        # Check if confirmation is required
        if self.prompt_manager.requires_confirmation("production_changes") and environment == "production":
            result["requires_confirmation"] = True
            result["confirmation_message"] = (
                f"This change affects {len(affected_consumers)} consumers in production. "
                f"Risk level: {result['risk_level']}. Please confirm before proceeding."
            )
        
        return result
    
    async def auto_fix_compatibility_with_prompts(
        self,
        subject: str,
        new_schema: Dict,
        environment: str = "dev"
    ) -> Dict:
        """Auto-fix compatibility issues using configured prompts"""
        # Check compatibility first
        compatibility = await self.unified_client.call_tool(
            "check_compatibility",
            {
                "subject": subject,
                "schema_definition": new_schema,
                "registry": environment
            }
        )
        
        compatibility_result = json.loads(compatibility.content[0].text)
        
        if compatibility_result.get("is_compatible", True):
            return {
                "fixed": False,
                "reason": "Schema is already compatible",
                "original_schema": new_schema
            }
        
        # Build context for fix
        context = PromptContext(
            operation=PromptOperation.COMPATIBILITY_FIX,
            environment=environment,
            variables={
                "original_schema": json.dumps(new_schema, indent=2),
                "compatibility_issues": compatibility_result.get("messages", []),
                "compatibility_mode": self._get_compatibility_mode(environment),
                "fix_constraints": "Maintain semantic meaning and minimize changes"
            }
        )
        
        # Get fix from LLM
        fix_prompt = self.prompt_manager.get_full_prompt(
            context,
            f"Fix compatibility issues in this schema: {json.dumps(new_schema, indent=2)}"
        )
        
        fixed_schema_str = await self._query_llm_with_prompt(fix_prompt, context)
        
        try:
            # Extract JSON from response
            fixed_schema = self._extract_json_from_response(fixed_schema_str)
            
            # Verify the fix
            verify_result = await self.unified_client.call_tool(
                "check_compatibility",
                {
                    "subject": subject,
                    "schema_definition": fixed_schema,
                    "registry": environment
                }
            )
            
            verify_compatibility = json.loads(verify_result.content[0].text)
            
            return {
                "fixed": verify_compatibility.get("is_compatible", False),
                "original_schema": new_schema,
                "fixed_schema": fixed_schema,
                "changes_made": self._diff_schemas(new_schema, fixed_schema),
                "prompt_used": fix_prompt[:500]  # Include part of prompt for debugging
            }
        except Exception as e:
            logger.error(f"Failed to fix schema: {e}")
            return {
                "fixed": False,
                "reason": f"Failed to generate valid fix: {str(e)}",
                "original_schema": new_schema
            }
    
    async def natural_language_query_with_prompts(
        self,
        query: str,
        environment: str = "dev"
    ) -> str:
        """Process natural language query using configured prompts"""
        # Build context
        context = PromptContext(
            operation=PromptOperation.NLP_QUERY,
            environment=environment,
            variables={
                "user_query": query,
                "environment": environment,
                "conversation_context": self.context_memory.get("conversation", []),
                "user_role": self.context_memory.get("user_role", "developer"),
                "environment_context": environment
            }
        )
        
        # Get intent and response using configured prompts
        nlp_prompt = self.prompt_manager.get_full_prompt(context, query)
        response = await self._query_llm_with_prompt(nlp_prompt, context)
        
        # Store in conversation memory
        if "conversation" not in self.context_memory:
            self.context_memory["conversation"] = []
        self.context_memory["conversation"].append({
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Format response according to settings
        formatted_response = self.prompt_manager.format_response(response)
        
        return formatted_response
    
    async def generate_documentation_with_prompts(
        self,
        subject: str,
        environment: str = "dev"
    ) -> str:
        """Generate documentation using configured prompts"""
        # Get schema and metadata
        schema_result = await self.unified_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        schema = json.loads(schema_result.content[0].text)
        
        # Get related topics
        related_topics = await self._get_related_topics(subject, environment)
        
        # Build context
        context = PromptContext(
            operation=PromptOperation.DOCUMENTATION,
            environment=environment,
            variables={
                "schema_name": subject,
                "schema_definition": json.dumps(schema, indent=2),
                "version": schema.get("version", 1),
                "environment": environment,
                "compatibility_mode": self._get_compatibility_mode(environment),
                "last_updated": datetime.utcnow().isoformat(),
                "owner_team": self.context_memory.get("owner_team", "Data Team"),
                "related_topics": ", ".join(related_topics)
            }
        )
        
        # Generate documentation
        doc_prompt = self.prompt_manager.get_full_prompt(
            context,
            f"Generate comprehensive documentation for {subject}"
        )
        
        documentation = await self._query_llm_with_prompt(doc_prompt, context)
        
        # Format according to output settings
        return self.prompt_manager.format_response(documentation)
    
    async def analyze_error_with_prompts(
        self,
        error_message: str,
        error_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze errors using configured prompt templates"""
        # Use custom template for error analysis
        error_prompt = self.prompt_manager.get_template_prompt(
            "error_analysis",
            {
                "error_message": error_message,
                "error_context": json.dumps(error_context, indent=2)
            }
        )
        
        analysis = await self._query_llm(error_prompt)
        
        return {
            "error": error_message,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _query_llm_with_prompt(self, prompt: str, context: PromptContext) -> str:
        """Query LLM with configured prompt settings"""
        provider = self.config['llm_providers']['primary']
        
        # Get settings from prompt manager
        max_tokens = self.prompt_manager.get_max_tokens()
        temperature = self.prompt_manager.get_temperature()
        
        try:
            if provider == LLMProvider.ANTHROPIC.value:
                response = self.llm_provider.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.content[0].text
            
            elif provider == LLMProvider.OPENAI.value:
                response = await self.llm_provider.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            
            elif provider == LLMProvider.GOOGLE.value:
                response = self.llm_provider.generate_content(prompt)
                return response.text
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            
            # Try fallback provider if configured
            fallback = self.config['llm_providers'].get('fallback')
            if fallback and fallback != provider:
                logger.info(f"Trying fallback provider: {fallback}")
                # Switch provider temporarily and retry
                original_provider = self.llm_provider
                self.config['llm_providers']['primary'] = fallback
                self.llm_provider = self._init_llm_provider()
                
                try:
                    result = await self._query_llm(prompt)
                    return result
                finally:
                    # Restore original provider
                    self.config['llm_providers']['primary'] = provider
                    self.llm_provider = original_provider
            
            return "LLM query failed"
    
    async def _query_llm(self, prompt: str) -> str:
        """Direct LLM query (backward compatibility)"""
        context = PromptContext(
            operation=PromptOperation.NLP_QUERY,
            environment="dev"
        )
        return await self._query_llm_with_prompt(prompt, context)
    
    def _calculate_health_score(self, analysis: ComprehensiveAnalysis, alignment: Dict):
        """Calculate health score with configurable weights"""
        # Start with perfect score
        analysis.health_score = 100.0
        
        # Deduct for alignment issues
        if alignment["topics_without_schemas"]:
            analysis.alignment_issues.append(
                f"Topics without schemas: {', '.join(alignment['topics_without_schemas'])}"
            )
            analysis.health_score -= len(alignment["topics_without_schemas"]) * 5
        
        if alignment["schemas_without_topics"]:
            analysis.alignment_issues.append(
                f"Orphaned schemas: {', '.join(alignment['schemas_without_topics'])}"
            )
            analysis.health_score -= len(alignment["schemas_without_topics"]) * 2
        
        # Ensure score doesn't go below 0
        analysis.health_score = max(0, analysis.health_score)
    
    def _calculate_avg_lag(self, consumer_groups: Dict) -> float:
        """Calculate average consumer lag"""
        # Simplified calculation
        return 1000.0
    
    async def _assess_risks_with_prompts(self, topology: Dict, alignment: Dict, environment: str) -> Dict:
        """Assess risks using configured risk tolerance"""
        risk_tolerance = self.prompt_manager.get_risk_tolerance(environment)
        
        risks = {
            "level": "LOW",
            "tolerance": risk_tolerance,
            "factors": [],
            "score": 0
        }
        
        # Apply different thresholds based on risk tolerance
        if risk_tolerance == "low":
            # Stricter risk assessment for production
            threshold_multiplier = 0.5
        elif risk_tolerance == "high":
            # More lenient for development
            threshold_multiplier = 2.0
        else:
            threshold_multiplier = 1.0
        
        # Check for risks
        for topic, details in topology.get("topics", {}).items():
            if details.get("replication_factor", 1) < 2:
                risks["factors"].append(f"Topic {topic} has no replication")
                risks["score"] += 20 / threshold_multiplier
        
        if len(alignment.get("topics_without_schemas", [])) > 5 * threshold_multiplier:
            risks["factors"].append("Many topics without schemas")
            risks["score"] += 30 / threshold_multiplier
        
        # Determine risk level
        if risks["score"] >= 50:
            risks["level"] = "HIGH"
        elif risks["score"] >= 25:
            risks["level"] = "MEDIUM"
        
        return risks
    
    def _get_compatibility_mode(self, environment: str) -> str:
        """Get compatibility mode for environment"""
        env_config = self.config.get("environments", {}).get(environment, {})
        return env_config.get("compatibility", "BACKWARD")
    
    async def _get_consumers_for_topic(self, subject: str, environment: str) -> List[str]:
        """Get list of consumers for a topic"""
        # Simplified - would query actual consumer groups
        return ["consumer-group-1", "consumer-group-2"]
    
    async def _get_affected_consumers(self, subject: str, environment: str) -> List[str]:
        """Get affected consumers for a schema change"""
        return await self._get_consumers_for_topic(subject, environment)
    
    async def _get_related_topics(self, subject: str, environment: str) -> List[str]:
        """Get related topics for documentation"""
        # Simplified - would analyze actual relationships
        return ["related-topic-1", "related-topic-2"]
    
    def _apply_schema_changes(self, current_schema: Dict, changes: Dict) -> Dict:
        """Apply changes to a schema"""
        import copy
        new_schema = copy.deepcopy(current_schema)
        
        if "add_fields" in changes:
            if "fields" not in new_schema:
                new_schema["fields"] = []
            for field in changes["add_fields"]:
                new_schema["fields"].append(field)
        
        if "remove_fields" in changes:
            new_schema["fields"] = [
                f for f in new_schema.get("fields", [])
                if f.get("name") not in changes["remove_fields"]
            ]
        
        return new_schema
    
    def _assess_risk_with_tolerance(self, compatibility: Dict, affected_consumers: List, tolerance: str) -> str:
        """Assess risk level based on tolerance setting"""
        if not compatibility.get("is_compatible", True):
            return "HIGH" if tolerance == "low" else "MEDIUM"
        elif len(affected_consumers) > 10:
            return "MEDIUM" if tolerance == "low" else "LOW"
        else:
            return "LOW"
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        
        # Try to parse entire response as JSON
        try:
            return json.loads(response)
        except:
            # Try to find JSON-like structure
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            raise ValueError("No valid JSON found in response")
    
    def _diff_schemas(self, schema1: Dict, schema2: Dict) -> List[str]:
        """Find differences between two schemas"""
        differences = []
        
        # Compare fields
        fields1 = {f.get("name"): f for f in schema1.get("fields", [])}
        fields2 = {f.get("name"): f for f in schema2.get("fields", [])}
        
        for name in fields1:
            if name not in fields2:
                differences.append(f"Field '{name}' removed")
        
        for name in fields2:
            if name not in fields1:
                differences.append(f"Field '{name}' added")
            elif fields1[name] != fields2[name]:
                differences.append(f"Field '{name}' modified")
        
        return differences
    
    def _parse_recommendations(self, llm_response: str) -> List[str]:
        """Parse recommendations from LLM response"""
        recommendations = []
        for line in llm_response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up the line
                line = line.lstrip('0123456789.-•').strip()
                if line:
                    recommendations.append(line)
        return recommendations[:5]  # Top 5 recommendations
    
    def _parse_migration_plan(self, llm_response: str) -> List[str]:
        """Parse migration plan from LLM response"""
        return self._parse_recommendations(llm_response)


class PromptConfigurationUI:
    """Helper class for managing prompt configurations through UI or API"""
    
    def __init__(self, agent: ConfigurableKafkaAIAgent):
        self.agent = agent
    
    async def update_global_role(self, role_description: str):
        """Update the global AI role description"""
        org_config = {
            "global": {
                "role": role_description
            }
        }
        await self.agent.customize_prompts(org_config)
    
    async def update_operation_prompt(self, operation: str, prompt_section: str, content: str):
        """Update a specific operation prompt section"""
        org_config = {
            "operations": {
                operation: {
                    prompt_section: content
                }
            }
        }
        await self.agent.customize_prompts(org_config)
    
    async def set_environment_tone(self, environment: str, tone: str):
        """Set the tone for a specific environment"""
        org_config = {
            "environments": {
                environment: {
                    "tone_adjustment": tone
                }
            }
        }
        await self.agent.customize_prompts(org_config)
    
    async def add_custom_template(self, template_name: str, template_content: str):
        """Add a custom prompt template"""
        org_config = {
            "templates": {
                template_name: template_content
            }
        }
        await self.agent.customize_prompts(org_config)
    
    def get_current_prompts(self) -> Dict:
        """Get current prompt configuration"""
        return self.agent.prompt_manager.prompts_config
    
    async def test_prompt(self, operation: PromptOperation, test_input: str, environment: str = "dev") -> str:
        """Test a prompt with sample input"""
        context = PromptContext(
            operation=operation,
            environment=environment,
            variables={}
        )
        
        prompt = self.agent.prompt_manager.get_full_prompt(context, test_input)
        return prompt