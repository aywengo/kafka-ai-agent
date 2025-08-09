# tests/test_agent.py
"""
Unit tests for Kafka AI Agent
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

from kafka_ai_agent import KafkaAIAgent, SchemaAnalysis, LLMProvider


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'environments': {
            'dev': {
                'registry_url': 'http://localhost:8081',
                'context': 'development',
                'compatibility': 'BACKWARD'
            }
        },
        'mcp_server': {
            'host': 'localhost',
            'port': 8000
        },
        'llm_providers': {
            'primary': 'anthropic',
            'fallback': 'openai'
        },
        'features': {
            'auto_documentation': True,
            'breaking_change_prevention': True
        }
    }


@pytest.fixture
def agent(mock_config):
    """Create agent instance for testing"""
    with patch.object(KafkaAIAgent, '_load_config', return_value=mock_config):
        with patch.object(KafkaAIAgent, '_init_llm_provider', return_value=Mock()):
            return KafkaAIAgent('test_config.yaml')


class TestKafkaAIAgent:
    """Test cases for KafkaAIAgent"""
    
    @pytest.mark.asyncio
    async def test_analyze_schema_evolution(self, agent):
        """Test schema evolution analysis"""
        # Mock MCP client
        mock_mcp_client = AsyncMock()
        mock_mcp_client.call_tool.side_effect = [
            Mock(content=[Mock(text='[1, 2, 3]')]),  # versions
            Mock(content=[Mock(text='{"type": "record", "name": "Test"}')]),  # schema
        ]
        agent.mcp_client = mock_mcp_client
        
        # Mock LLM response
        with patch.object(agent, '_query_llm', return_value='Test analysis'):
            result = await agent.analyze_schema_evolution('test-subject', 'dev')
        
        assert isinstance(result, SchemaAnalysis)
        assert result.schema_name == 'test-subject'
        assert result.version == 3
    
    @pytest.mark.asyncio
    async def test_detect_breaking_changes_compatible(self, agent):
        """Test breaking change detection for compatible schema"""
        mock_mcp_client = AsyncMock()
        mock_mcp_client.call_tool.return_value = Mock(
            content=[Mock(text='{"is_compatible": true}')]
        )
        agent.mcp_client = mock_mcp_client
        
        new_schema = {"type": "record", "name": "Test"}
        result = await agent.detect_breaking_changes('test-subject', new_schema, 'dev')
        
        assert result['compatible'] is True
        assert result['message'] == 'No breaking changes detected'
    
    @pytest.mark.asyncio
    async def test_detect_breaking_changes_incompatible(self, agent):
        """Test breaking change detection for incompatible schema"""
        mock_mcp_client = AsyncMock()
        mock_mcp_client.call_tool.side_effect = [
            Mock(content=[Mock(text='{"is_compatible": false, "messages": ["Field removed"]}')]),
            Mock(content=[Mock(text='[]')])  # evolution path
        ]
        agent.mcp_client = mock_mcp_client
        
        with patch.object(agent, '_query_llm', return_value='Add default value'):
            new_schema = {"type": "record", "name": "Test"}
            result = await agent.detect_breaking_changes('test-subject', new_schema, 'dev')
        
        assert result['compatible'] is False
        assert 'Field removed' in result['issues']
        assert result['suggested_fixes'] == 'Add default value'
    
    @pytest.mark.asyncio
    async def test_generate_documentation(self, agent):
        """Test documentation generation"""
        mock_mcp_client = AsyncMock()
        mock_mcp_client.call_tool.return_value = Mock(
            content=[Mock(text='{"type": "record", "name": "Test"}')]
        )
        agent.mcp_client = mock_mcp_client
        
        with patch.object(agent, '_query_llm', return_value='# Test Documentation'):
            with patch.object(agent, '_save_documentation', new_callable=AsyncMock):
                doc = await agent.generate_documentation('test-subject', 'dev')
        
        assert doc == '# Test Documentation'
    
    @pytest.mark.asyncio
    async def test_natural_language_query(self, agent):
        """Test natural language query processing"""
        mock_mcp_client = AsyncMock()
        mock_mcp_client.call_tool.return_value = Mock(
            content=[Mock(text='["subject1", "subject2"]')]
        )
        agent.mcp_client = mock_mcp_client
        
        with patch.object(agent, '_query_llm', return_value='list schemas'):
            response = await agent.natural_language_query(
                'What schemas are available?',
                'dev'
            )
        
        assert 'Available schemas' in response


class TestSchemaMonitor:
    """Test cases for SchemaMonitor"""
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, agent):
        """Test schema monitoring start"""
        from kafka_ai_agent import SchemaMonitor
        
        monitor = SchemaMonitor(agent)
        
        # Mock _check_schemas to stop after one iteration
        async def mock_check():
            monitor.monitoring = False
        
        with patch.object(monitor, '_check_schemas', side_effect=mock_check):
            await monitor.start_monitoring(interval=0.1)
        
        assert monitor.monitoring is False
    
    def test_stop_monitoring(self, agent):
        """Test schema monitoring stop"""
        from kafka_ai_agent import SchemaMonitor
        
        monitor = SchemaMonitor(agent)
        monitor.monitoring = True
        monitor.stop_monitoring()
        
        assert monitor.monitoring is False