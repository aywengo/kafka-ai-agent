# kafka_ai_agent_enhanced.py
"""
Enhanced Kafka AI Agent - Intelligent Kafka Ecosystem Management
Integrates both Schema Registry and Kafka Brokers MCP servers
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


@dataclass
class DataPipelineAnalysis:
    """Analysis of a data pipeline across topics"""
    pipeline_name: str
    topics: List[str]
    schemas: List[Dict]
    compatibility_matrix: Dict[str, bool]
    bottlenecks: List[str]
    optimization_suggestions: List[str]


class EnhancedKafkaAIAgent:
    """Enhanced AI Agent for complete Kafka ecosystem management"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the Enhanced AI Agent"""
        self.config = self._load_config(config_path)
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
        logger.info("Enhanced Kafka AI Agent initialized with multiple MCP servers")
    
    async def comprehensive_ecosystem_analysis(self, environment: str = "dev") -> ComprehensiveAnalysis:
        """Perform comprehensive analysis of the entire Kafka ecosystem"""
        analysis = ComprehensiveAnalysis(
            timestamp=datetime.utcnow(),
            environment=environment
        )
        
        # Get topology report from cross-analyzer
        topology = await self.cross_analyzer.generate_topology_report(environment)
        
        # Analyze schemas
        analysis.schemas = topology.get("schemas", {})
        
        # Analyze topics
        analysis.topics = topology.get("topics", {})
        
        # Analyze consumer groups
        analysis.consumer_groups = topology.get("consumer_groups", {})
        
        # Check alignment between topics and schemas
        alignment = await self.unified_client.analyze_topic_schema_alignment(environment)
        
        # Identify issues
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
        
        # Use LLM to generate recommendations
        recommendations_prompt = f"""
        Analyze this Kafka ecosystem state and provide recommendations:
        
        Environment: {environment}
        Topics: {len(analysis.topics)}
        Schemas: {len(analysis.schemas)}
        Consumer Groups: {len(analysis.consumer_groups)}
        Alignment Issues: {analysis.alignment_issues}
        
        Topology Details: {json.dumps(topology, indent=2)[:2000]}  # Truncate for LLM
        
        Provide:
        1. Top 5 recommendations for improvement
        2. Risk assessment
        3. Optimization opportunities
        """
        
        llm_response = await self._query_llm(recommendations_prompt)
        analysis.recommendations = self._parse_recommendations(llm_response)
        
        # Perform risk assessment
        analysis.risk_assessment = await self._assess_risks(topology, alignment)
        
        return analysis
    
    async def analyze_data_pipeline(
        self,
        pipeline_name: str,
        topic_chain: List[str],
        environment: str = "dev"
    ) -> DataPipelineAnalysis:
        """Analyze a complete data pipeline across multiple topics"""
        pipeline_data = await self.cross_analyzer.analyze_data_pipeline(
            topic_chain, environment
        )
        
        analysis = DataPipelineAnalysis(
            pipeline_name=pipeline_name,
            topics=topic_chain,
            schemas=pipeline_data.get("schemas", []),
            compatibility_matrix=pipeline_data.get("compatibility_matrix", {}),
            bottlenecks=[],
            optimization_suggestions=[]
        )
        
        # Identify bottlenecks
        for topic_info in pipeline_data.get("topics", []):
            # Check partition count
            if topic_info.get("partitions", 1) < 3:
                analysis.bottlenecks.append(
                    f"Topic {topic_info.get('name')} has only {topic_info.get('partitions')} partitions"
                )
            
            # Check replication factor
            if topic_info.get("replication_factor", 1) < 2:
                analysis.bottlenecks.append(
                    f"Topic {topic_info.get('name')} has replication factor of {topic_info.get('replication_factor')}"
                )
        
        # Use LLM for optimization suggestions
        optimization_prompt = f"""
        Analyze this data pipeline and suggest optimizations:
        
        Pipeline: {pipeline_name}
        Topics: {' -> '.join(topic_chain)}
        Compatibility: {json.dumps(analysis.compatibility_matrix, indent=2)}
        Bottlenecks: {analysis.bottlenecks}
        
        Suggest:
        1. Schema evolution strategy
        2. Performance optimizations
        3. Reliability improvements
        """
        
        llm_response = await self._query_llm(optimization_prompt)
        analysis.optimization_suggestions = self._parse_suggestions(llm_response)
        
        return analysis
    
    async def intelligent_schema_evolution(
        self,
        subject: str,
        proposed_changes: Dict[str, Any],
        environment: str = "dev"
    ) -> Dict:
        """Intelligently manage schema evolution with impact analysis"""
        result = {
            "subject": subject,
            "current_version": None,
            "proposed_version": None,
            "compatibility": None,
            "impact_analysis": {},
            "migration_plan": [],
            "risk_level": "LOW"
        }
        
        # Get current schema
        current_schema = await self.unified_client.call_tool(
            "get_schema",
            {"subject": subject, "version": "latest", "registry": environment}
        )
        result["current_version"] = current_schema
        
        # Apply proposed changes to create new schema
        new_schema = self._apply_schema_changes(current_schema, proposed_changes)
        result["proposed_version"] = new_schema
        
        # Check compatibility
        compatibility = await self.unified_client.call_tool(
            "check_compatibility",
            {
                "subject": subject,
                "schema_definition": new_schema,
                "registry": environment
            }
        )
        result["compatibility"] = compatibility
        
        # Analyze impact on consumers
        topic_name = subject.replace("-value", "").replace("-key", "")
        
        # Get consumer groups for this topic
        consumer_groups = await self.unified_client.call_tool(
            "list_consumer_groups",
            {"cluster": environment}
        )
        
        affected_consumers = []
        for group in consumer_groups:
            group_details = await self.unified_client.call_tool(
                "get_consumer_group",
                {"group_id": group, "cluster": environment}
            )
            if topic_name in group_details.get("topics", []):
                affected_consumers.append(group)
        
        result["impact_analysis"]["affected_consumers"] = affected_consumers
        result["impact_analysis"]["consumer_count"] = len(affected_consumers)
        
        # Generate migration plan using LLM
        migration_prompt = f"""
        Create a migration plan for this schema evolution:
        
        Subject: {subject}
        Current Schema: {json.dumps(current_schema, indent=2)[:1000]}
        Proposed Changes: {json.dumps(proposed_changes, indent=2)}
        Affected Consumers: {affected_consumers}
        Compatibility: {compatibility}
        
        Generate:
        1. Step-by-step migration plan
        2. Rollback strategy
        3. Testing requirements
        4. Risk assessment (LOW/MEDIUM/HIGH)
        """
        
        llm_response = await self._query_llm(migration_prompt)
        result["migration_plan"] = self._parse_migration_plan(llm_response)
        result["risk_level"] = self._assess_risk_level(compatibility, affected_consumers)
        
        return result
    
    async def auto_fix_compatibility_issues(
        self,
        subject: str,
        new_schema: Dict,
        environment: str = "dev"
    ) -> Dict:
        """Automatically fix schema compatibility issues"""
        # Check compatibility
        compatibility = await self.unified_client.call_tool(
            "check_compatibility",
            {
                "subject": subject,
                "schema_definition": new_schema,
                "registry": environment
            }
        )
        
        if compatibility.get("is_compatible", True):
            return {
                "fixed": False,
                "reason": "Schema is already compatible",
                "original_schema": new_schema
            }
        
        # Use LLM to suggest fixes
        fix_prompt = f"""
        Fix these schema compatibility issues:
        
        Schema: {json.dumps(new_schema, indent=2)}
        Issues: {compatibility.get('messages', [])}
        
        Provide a corrected schema that maintains backward compatibility.
        Return only valid JSON schema definition.
        """
        
        llm_response = await self._query_llm(fix_prompt)
        
        try:
            fixed_schema = json.loads(llm_response)
            
            # Verify the fix
            verify_compatibility = await self.unified_client.call_tool(
                "check_compatibility",
                {
                    "subject": subject,
                    "schema_definition": fixed_schema,
                    "registry": environment
                }
            )
            
            return {
                "fixed": verify_compatibility.get("is_compatible", False),
                "original_schema": new_schema,
                "fixed_schema": fixed_schema,
                "changes_made": self._diff_schemas(new_schema, fixed_schema)
            }
        except json.JSONDecodeError:
            return {
                "fixed": False,
                "reason": "Failed to generate valid schema fix",
                "original_schema": new_schema
            }
    
    async def topic_schema_health_check(
        self,
        topic: str,
        environment: str = "dev"
    ) -> Dict:
        """Perform health check on topic-schema alignment"""
        health_report = {
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": "HEALTHY",
            "issues": [],
            "metrics": {}
        }
        
        # Get topic details
        topic_details = await self.unified_client.call_tool(
            "get_topic_details",
            {"topic": topic, "cluster": environment}
        )
        health_report["metrics"]["partitions"] = topic_details.get("partitions", 0)
        health_report["metrics"]["replication_factor"] = topic_details.get("replication_factor", 0)
        
        # Check for schema
        try:
            schema = await self.unified_client.call_tool(
                "get_schema",
                {"subject": f"{topic}-value", "registry": environment}
            )
            health_report["schema_present"] = True
            
            # Validate sample messages
            validation = await self.unified_client.validate_topic_messages_against_schema(
                topic, sample_size=10, environment=environment
            )
            
            invalid_messages = [v for v in validation["validation_results"] if not v["valid"]]
            if invalid_messages:
                health_report["health_status"] = "DEGRADED"
                health_report["issues"].append(
                    f"{len(invalid_messages)} messages failed schema validation"
                )
        except Exception as e:
            health_report["schema_present"] = False
            health_report["health_status"] = "UNHEALTHY"
            health_report["issues"].append(f"No schema found: {str(e)}")
        
        # Check consumer lag
        consumer_groups = await self._get_topic_consumer_groups(topic, environment)
        total_lag = 0
        for group in consumer_groups:
            lag = await self._get_consumer_lag(group, topic, environment)
            total_lag += lag
        
        health_report["metrics"]["total_consumer_lag"] = total_lag
        if total_lag > 10000:
            health_report["health_status"] = "DEGRADED"
            health_report["issues"].append(f"High consumer lag: {total_lag}")
        
        return health_report
    
    async def generate_data_catalog(self, environment: str = "dev") -> Dict:
        """Generate a comprehensive data catalog with documentation"""
        catalog = {
            "generated_at": datetime.utcnow().isoformat(),
            "environment": environment,
            "topics": {},
            "schemas": {},
            "data_flows": [],
            "documentation": {}
        }
        
        # Get all topics
        topics = await self.unified_client.call_tool(
            "list_topics",
            {"cluster": environment}
        )
        
        for topic in topics:
            # Get topic details
            topic_info = await self.unified_client.call_tool(
                "get_topic_details",
                {"topic": topic, "cluster": environment}
            )
            catalog["topics"][topic] = topic_info
            
            # Get schema if exists
            try:
                schema = await self.unified_client.call_tool(
                    "get_schema",
                    {"subject": f"{topic}-value", "registry": environment}
                )
                catalog["schemas"][topic] = schema
                
                # Generate documentation using LLM
                doc_prompt = f"""
                Generate data catalog documentation for:
                
                Topic: {topic}
                Schema: {json.dumps(schema, indent=2)[:1000]}
                Partitions: {topic_info.get('partitions')}
                
                Include:
                1. Business purpose
                2. Data flow description
                3. Field descriptions
                4. Usage examples
                """
                
                documentation = await self._query_llm(doc_prompt)
                catalog["documentation"][topic] = documentation
            except:
                catalog["schemas"][topic] = None
                catalog["documentation"][topic] = "No schema available"
        
        # Identify data flows
        catalog["data_flows"] = await self._identify_data_flows(catalog)
        
        return catalog
    
    async def _query_llm(self, prompt: str) -> str:
        """Query the configured LLM provider"""
        provider = self.config['llm_providers']['primary']
        
        try:
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
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return "LLM query failed"
    
    def _parse_recommendations(self, llm_response: str) -> List[str]:
        """Parse recommendations from LLM response"""
        # Simple parsing - in production use structured output
        recommendations = []
        for line in llm_response.split('\n'):
            if line.strip() and any(char.isdigit() for char in line[:3]):
                recommendations.append(line.strip())
        return recommendations[:5]  # Top 5 recommendations
    
    def _parse_suggestions(self, llm_response: str) -> List[str]:
        """Parse suggestions from LLM response"""
        return self._parse_recommendations(llm_response)
    
    def _parse_migration_plan(self, llm_response: str) -> List[str]:
        """Parse migration plan from LLM response"""
        return self._parse_recommendations(llm_response)
    
    async def _assess_risks(self, topology: Dict, alignment: Dict) -> Dict:
        """Assess risks in the Kafka ecosystem"""
        risks = {
            "level": "LOW",
            "factors": [],
            "score": 0
        }
        
        # Check for single points of failure
        for topic, details in topology.get("topics", {}).items():
            if details.get("replication_factor", 1) < 2:
                risks["factors"].append(f"Topic {topic} has no replication")
                risks["score"] += 20
        
        # Check for missing schemas
        if len(alignment.get("topics_without_schemas", [])) > 5:
            risks["factors"].append("Many topics without schemas")
            risks["score"] += 30
        
        # Determine risk level
        if risks["score"] >= 50:
            risks["level"] = "HIGH"
        elif risks["score"] >= 25:
            risks["level"] = "MEDIUM"
        
        return risks
    
    def _apply_schema_changes(self, current_schema: Dict, changes: Dict) -> Dict:
        """Apply changes to a schema"""
        # Deep copy current schema
        import copy
        new_schema = copy.deepcopy(current_schema)
        
        # Apply changes (simplified - implement based on your needs)
        if "add_fields" in changes:
            for field in changes["add_fields"]:
                new_schema["fields"].append(field)
        
        if "remove_fields" in changes:
            new_schema["fields"] = [
                f for f in new_schema["fields"]
                if f["name"] not in changes["remove_fields"]
            ]
        
        return new_schema
    
    def _assess_risk_level(self, compatibility: Dict, affected_consumers: List) -> str:
        """Assess risk level of a schema change"""
        if not compatibility.get("is_compatible", True):
            return "HIGH"
        elif len(affected_consumers) > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _diff_schemas(self, schema1: Dict, schema2: Dict) -> List[str]:
        """Find differences between two schemas"""
        differences = []
        # Simplified diff - implement proper schema comparison
        if json.dumps(schema1) != json.dumps(schema2):
            differences.append("Schema structure changed")
        return differences
    
    async def _get_topic_consumer_groups(self, topic: str, environment: str) -> List[str]:
        """Get consumer groups for a topic"""
        all_groups = await self.unified_client.call_tool(
            "list_consumer_groups",
            {"cluster": environment}
        )
        
        topic_groups = []
        for group in all_groups:
            details = await self.unified_client.call_tool(
                "get_consumer_group",
                {"group_id": group, "cluster": environment}
            )
            if topic in details.get("topics", []):
                topic_groups.append(group)
        
        return topic_groups
    
    async def _get_consumer_lag(self, group: str, topic: str, environment: str) -> int:
        """Get consumer lag for a group on a topic"""
        # Simplified - implement actual lag calculation
        return 0
    
    async def _identify_data_flows(self, catalog: Dict) -> List[Dict]:
        """Identify data flows based on topic naming and schemas"""
        flows = []
        topics = list(catalog["topics"].keys())
        
        # Simple pattern matching for data flows
        # In production, use more sophisticated analysis
        for i, topic1 in enumerate(topics):
            for topic2 in topics[i+1:]:
                if topic1.split('-')[0] == topic2.split('-')[0]:
                    flows.append({
                        "source": topic1,
                        "destination": topic2,
                        "type": "potential_pipeline"
                    })
        
        return flows


class EnhancedSchemaMonitor:
    """Enhanced monitoring with both schema and broker insights"""
    
    def __init__(self, agent: EnhancedKafkaAIAgent):
        """Initialize enhanced monitor"""
        self.agent = agent
        self.monitoring = False
        self.alerts = []
        
    async def start_monitoring(self, interval: int = 60):
        """Start comprehensive monitoring"""
        self.monitoring = True
        logger.info("Starting enhanced Kafka ecosystem monitoring...")
        
        while self.monitoring:
            try:
                await self._comprehensive_check()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
    
    async def _comprehensive_check(self):
        """Perform comprehensive ecosystem check"""
        # Get all environments from config
        environments = self.agent.config.get("environments", {}).keys()
        
        for env in environments:
            # Perform ecosystem analysis
            analysis = await self.agent.comprehensive_ecosystem_analysis(env)
            
            # Check for issues
            if analysis.health_score < 80:
                self.alerts.append({
                    "timestamp": datetime.utcnow(),
                    "environment": env,
                    "health_score": analysis.health_score,
                    "issues": analysis.alignment_issues
                })
            
            # Log status
            logger.info(
                f"Environment {env}: Health Score={analysis.health_score}, "
                f"Issues={len(analysis.alignment_issues)}"
            )
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        logger.info("Enhanced monitoring stopped")
    
    def get_alerts(self) -> List[Dict]:
        """Get current alerts"""
        return self.alerts