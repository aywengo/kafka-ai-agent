# mcp_manager.py
"""
MCP Manager - Handles multiple MCP server connections
Integrates Schema Registry and Kafka Brokers MCP servers
"""

import asyncio
import logging
from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPServerType(Enum):
    """Available MCP server types"""
    SCHEMA_REGISTRY = "schema_registry"
    KAFKA_BROKERS = "kafka_brokers"
    # Future: Add more MCP servers as needed
    # KSQLDB = "ksqldb"
    # CONNECT = "connect"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    type: MCPServerType
    command: str
    args: List[str]
    enabled: bool = True
    description: str = ""


class MCPManager:
    """Manages multiple MCP server connections"""
    
    def __init__(self):
        """Initialize MCP Manager"""
        self.servers: Dict[MCPServerType, ClientSession] = {}
        self.configs: Dict[MCPServerType, MCPServerConfig] = self._get_default_configs()
        self.connected = False
        
    def _get_default_configs(self) -> Dict[MCPServerType, MCPServerConfig]:
        """Get default MCP server configurations"""
        return {
            MCPServerType.SCHEMA_REGISTRY: MCPServerConfig(
                name="Kafka Schema Registry MCP",
                type=MCPServerType.SCHEMA_REGISTRY,
                command="npx",
                args=["-y", "@aywengo/kafka-schema-reg-mcp"],
                description="Manages Kafka Schema Registry operations"
            ),
            MCPServerType.KAFKA_BROKERS: MCPServerConfig(
                name="Kafka Brokers MCP",
                type=MCPServerType.KAFKA_BROKERS,
                command="npx",
                args=["-y", "@aywengo/kafka-brokers-mcp"],
                description="Manages Kafka brokers, topics, and consumer groups"
            )
        }
    
    async def connect_all(self) -> Dict[MCPServerType, bool]:
        """Connect to all enabled MCP servers"""
        results = {}
        
        for server_type, config in self.configs.items():
            if config.enabled:
                try:
                    await self.connect_server(server_type)
                    results[server_type] = True
                    logger.info(f"Connected to {config.name}")
                except Exception as e:
                    results[server_type] = False
                    logger.error(f"Failed to connect to {config.name}: {e}")
        
        self.connected = any(results.values())
        return results
    
    async def connect_server(self, server_type: MCPServerType) -> ClientSession:
        """Connect to a specific MCP server"""
        config = self.configs[server_type]
        
        server_params = StdioServerParameters(
            command=config.command,
            args=config.args
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.servers[server_type] = session
                logger.info(f"Successfully connected to {config.name}")
                return session
    
    async def call_tool(self, server_type: MCPServerType, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific MCP server"""
        if server_type not in self.servers:
            raise ValueError(f"Not connected to {server_type.value} server")
        
        session = self.servers[server_type]
        return await session.call_tool(tool_name, arguments)
    
    async def get_available_tools(self, server_type: MCPServerType) -> List[str]:
        """Get list of available tools from a specific MCP server"""
        if server_type not in self.servers:
            raise ValueError(f"Not connected to {server_type.value} server")
        
        session = self.servers[server_type]
        tools = await session.list_tools()
        return [tool.name for tool in tools]
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        for server_type, session in self.servers.items():
            try:
                # MCP sessions are managed by context managers
                logger.info(f"Disconnected from {self.configs[server_type].name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_type.value}: {e}")
        
        self.servers.clear()
        self.connected = False
    
    def is_connected(self, server_type: Optional[MCPServerType] = None) -> bool:
        """Check if connected to MCP server(s)"""
        if server_type:
            return server_type in self.servers
        return self.connected


class UnifiedMCPClient:
    """Unified client for multiple MCP servers with intelligent routing"""
    
    def __init__(self, manager: MCPManager):
        """Initialize unified MCP client"""
        self.manager = manager
        self.tool_registry = {}
        
    async def initialize(self):
        """Initialize and map all available tools"""
        await self.manager.connect_all()
        await self._build_tool_registry()
    
    async def _build_tool_registry(self):
        """Build a registry of which tools belong to which server"""
        self.tool_registry.clear()
        
        for server_type in MCPServerType:
            if self.manager.is_connected(server_type):
                try:
                    tools = await self.manager.get_available_tools(server_type)
                    for tool in tools:
                        self.tool_registry[tool] = server_type
                    logger.info(f"Registered {len(tools)} tools from {server_type.value}")
                except Exception as e:
                    logger.error(f"Failed to get tools from {server_type.value}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool, automatically routing to the correct MCP server"""
        if tool_name not in self.tool_registry:
            # Try to determine server from tool name patterns
            server_type = self._infer_server_type(tool_name)
            if not server_type:
                raise ValueError(f"Unknown tool: {tool_name}")
        else:
            server_type = self.tool_registry[tool_name]
        
        return await self.manager.call_tool(server_type, tool_name, arguments)
    
    def _infer_server_type(self, tool_name: str) -> Optional[MCPServerType]:
        """Infer which server a tool belongs to based on naming patterns"""
        schema_patterns = ['schema', 'subject', 'compatibility', 'registry', 'context']
        broker_patterns = ['topic', 'broker', 'partition', 'consumer', 'producer', 'offset']
        
        tool_lower = tool_name.lower()
        
        if any(pattern in tool_lower for pattern in schema_patterns):
            return MCPServerType.SCHEMA_REGISTRY
        elif any(pattern in tool_lower for pattern in broker_patterns):
            return MCPServerType.KAFKA_BROKERS
        
        return None
    
    async def get_schema_for_topic(self, topic_name: str, environment: str = "dev") -> Dict:
        """Get schema information for a specific topic"""
        # First, get topic details from broker MCP
        topic_info = await self.call_tool(
            "get_topic_details",
            {"topic": topic_name, "cluster": environment}
        )
        
        # Then get schema from registry MCP
        # Convention: topic name usually matches subject name
        schema_info = await self.call_tool(
            "get_schema",
            {"subject": f"{topic_name}-value", "registry": environment}
        )
        
        return {
            "topic": topic_info,
            "schema": schema_info
        }
    
    async def analyze_topic_schema_alignment(self, environment: str = "dev") -> Dict:
        """Analyze alignment between topics and schemas"""
        # Get all topics from broker MCP
        topics = await self.call_tool(
            "list_topics",
            {"cluster": environment}
        )
        
        # Get all schemas from registry MCP
        subjects = await self.call_tool(
            "list_subjects",
            {"registry": environment}
        )
        
        # Analyze alignment
        alignment = {
            "topics_with_schemas": [],
            "topics_without_schemas": [],
            "schemas_without_topics": [],
            "misaligned": []
        }
        
        for topic in topics:
            value_subject = f"{topic}-value"
            key_subject = f"{topic}-key"
            
            if value_subject in subjects or key_subject in subjects:
                alignment["topics_with_schemas"].append(topic)
            else:
                alignment["topics_without_schemas"].append(topic)
        
        for subject in subjects:
            # Remove -value or -key suffix to get topic name
            base_name = subject.replace("-value", "").replace("-key", "")
            if base_name not in topics:
                alignment["schemas_without_topics"].append(subject)
        
        return alignment
    
    async def get_consumer_group_schemas(self, consumer_group: str, environment: str = "dev") -> Dict:
        """Get schemas for all topics consumed by a consumer group"""
        # Get consumer group details from broker MCP
        group_info = await self.call_tool(
            "get_consumer_group",
            {"group_id": consumer_group, "cluster": environment}
        )
        
        schemas = {}
        for topic in group_info.get("topics", []):
            try:
                schema = await self.call_tool(
                    "get_schema",
                    {"subject": f"{topic}-value", "registry": environment}
                )
                schemas[topic] = schema
            except Exception as e:
                logger.warning(f"No schema found for topic {topic}: {e}")
                schemas[topic] = None
        
        return {
            "consumer_group": consumer_group,
            "topics": group_info.get("topics", []),
            "schemas": schemas
        }
    
    async def validate_topic_messages_against_schema(
        self,
        topic: str,
        sample_size: int = 10,
        environment: str = "dev"
    ) -> Dict:
        """Validate actual messages in a topic against its schema"""
        # Get schema from registry
        schema = await self.call_tool(
            "get_schema",
            {"subject": f"{topic}-value", "registry": environment}
        )
        
        # Get sample messages from topic
        messages = await self.call_tool(
            "consume_messages",
            {
                "topic": topic,
                "cluster": environment,
                "max_messages": sample_size,
                "timeout": 5000
            }
        )
        
        # Validate messages against schema
        validation_results = []
        for msg in messages:
            # Here you would implement actual schema validation
            # This is a simplified example
            validation_results.append({
                "offset": msg.get("offset"),
                "valid": True,  # Would be actual validation result
                "errors": []
            })
        
        return {
            "topic": topic,
            "schema": schema,
            "messages_validated": len(messages),
            "validation_results": validation_results
        }


class CrossMCPAnalyzer:
    """Analyzer that leverages multiple MCP servers for comprehensive insights"""
    
    def __init__(self, unified_client: UnifiedMCPClient):
        """Initialize cross-MCP analyzer"""
        self.client = unified_client
    
    async def analyze_data_pipeline(self, topic_chain: List[str], environment: str = "dev") -> Dict:
        """Analyze a complete data pipeline across multiple topics"""
        pipeline_analysis = {
            "topics": [],
            "schemas": [],
            "compatibility_matrix": {},
            "consumer_groups": [],
            "data_flow": []
        }
        
        for i, topic in enumerate(topic_chain):
            # Get topic details
            topic_info = await self.client.call_tool(
                "get_topic_details",
                {"topic": topic, "cluster": environment}
            )
            pipeline_analysis["topics"].append(topic_info)
            
            # Get schema
            try:
                schema = await self.client.call_tool(
                    "get_schema",
                    {"subject": f"{topic}-value", "registry": environment}
                )
                pipeline_analysis["schemas"].append(schema)
                
                # Check compatibility with next topic in chain
                if i < len(topic_chain) - 1:
                    next_topic = topic_chain[i + 1]
                    compatibility = await self._check_schema_compatibility(
                        topic, next_topic, environment
                    )
                    pipeline_analysis["compatibility_matrix"][f"{topic}->{next_topic}"] = compatibility
            except Exception as e:
                logger.error(f"Error analyzing topic {topic}: {e}")
        
        return pipeline_analysis
    
    async def _check_schema_compatibility(self, topic1: str, topic2: str, environment: str) -> Dict:
        """Check schema compatibility between two topics"""
        schema1 = await self.client.call_tool(
            "get_schema",
            {"subject": f"{topic1}-value", "registry": environment}
        )
        
        schema2 = await self.client.call_tool(
            "get_schema",
            {"subject": f"{topic2}-value", "registry": environment}
        )
        
        # Check if schema2 can consume from schema1
        compatibility = await self.client.call_tool(
            "check_compatibility",
            {
                "subject": f"{topic2}-value",
                "schema_definition": schema1,
                "registry": environment
            }
        )
        
        return compatibility
    
    async def generate_topology_report(self, environment: str = "dev") -> Dict:
        """Generate a complete Kafka topology report"""
        report = {
            "timestamp": asyncio.get_event_loop().time(),
            "environment": environment,
            "brokers": {},
            "topics": {},
            "schemas": {},
            "consumer_groups": {},
            "producers": {},
            "health_status": {}
        }
        
        # Get broker information
        brokers = await self.client.call_tool(
            "list_brokers",
            {"cluster": environment}
        )
        report["brokers"] = brokers
        
        # Get all topics
        topics = await self.client.call_tool(
            "list_topics",
            {"cluster": environment}
        )
        
        for topic in topics:
            # Get topic details
            topic_details = await self.client.call_tool(
                "get_topic_details",
                {"topic": topic, "cluster": environment}
            )
            report["topics"][topic] = topic_details
            
            # Get associated schema
            try:
                schema = await self.client.call_tool(
                    "get_schema",
                    {"subject": f"{topic}-value", "registry": environment}
                )
                report["schemas"][topic] = schema
            except:
                report["schemas"][topic] = None
        
        # Get consumer groups
        consumer_groups = await self.client.call_tool(
            "list_consumer_groups",
            {"cluster": environment}
        )
        
        for group in consumer_groups:
            group_details = await self.client.call_tool(
                "get_consumer_group",
                {"group_id": group, "cluster": environment}
            )
            report["consumer_groups"][group] = group_details
        
        return report