# prompt_manager.py
"""
Prompt Manager for Kafka AI Agent
Manages system prompts from configuration file with dynamic templating
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from string import Template
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptOperation(Enum):
    """Available prompt operations"""
    SCHEMA_ANALYSIS = "schema_analysis"
    SCHEMA_EVOLUTION = "schema_evolution"
    BREAKING_CHANGES = "breaking_changes"
    DOCUMENTATION = "documentation"
    ECOSYSTEM_ANALYSIS = "ecosystem_analysis"
    PIPELINE_ANALYSIS = "pipeline_analysis"
    NLP_QUERY = "nlp_query"
    COMPATIBILITY_FIX = "compatibility_fix"
    CONSUMER_IMPACT = "consumer_impact"
    ERROR_ANALYSIS = "error_analysis"
    CAPACITY_PLANNING = "capacity_planning"
    MIGRATION_CHECKLIST = "migration_checklist"


@dataclass
class PromptContext:
    """Context variables for prompt templating"""
    operation: PromptOperation
    environment: str = "development"
    variables: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


class PromptManager:
    """Manages system prompts with dynamic templating and environment-specific customization"""
    
    def __init__(self, prompts_file: str = "prompts.yaml"):
        """Initialize the prompt manager"""
        self.prompts_file = prompts_file
        self.prompts_config = self._load_prompts()
        self.cache = {}
        
    def _load_prompts(self) -> Dict:
        """Load prompts from YAML configuration file"""
        prompts_path = Path(self.prompts_file)
        
        # Try multiple locations
        if not prompts_path.exists():
            # Try in config directory
            prompts_path = Path("config") / self.prompts_file
            
        if not prompts_path.exists():
            # Try in parent directory
            prompts_path = Path("..") / self.prompts_file
            
        if not prompts_path.exists():
            # Use default prompts
            logger.warning(f"Prompts file {self.prompts_file} not found, using defaults")
            return self._get_default_prompts()
        
        try:
            with open(prompts_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading prompts file: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        """Get default prompts if configuration file is not available"""
        return {
            "global": {
                "role": "You are an expert Kafka architect and data engineer.",
                "tone": "Be professional and helpful.",
                "constraints": "Prioritize safety and reliability."
            },
            "operations": {
                "schema_analysis": {
                    "base": "Analyze this Kafka schema for improvements."
                },
                "schema_evolution": {
                    "base": "Analyze the proposed schema evolution."
                }
            },
            "settings": {
                "max_tokens": 2000,
                "temperature": 0.7
            }
        }
    
    def reload_prompts(self):
        """Reload prompts from configuration file"""
        self.prompts_config = self._load_prompts()
        self.cache.clear()
        logger.info("Prompts reloaded from configuration")
    
    def get_system_prompt(self, context: PromptContext) -> str:
        """Get the complete system prompt for an operation"""
        cache_key = f"{context.operation.value}_{context.environment}"
        
        # Check cache
        if cache_key in self.cache and self._is_cache_enabled():
            return self.cache[cache_key]
        
        # Build system prompt
        prompt_parts = []
        
        # Add global role and context
        global_config = self.prompts_config.get("global", {})
        if global_config.get("role"):
            prompt_parts.append(global_config["role"])
        
        # Add environment-specific context
        env_config = self.prompts_config.get("environments", {}).get(context.environment, {})
        if env_config.get("additional_context"):
            prompt_parts.append(env_config["additional_context"])
        
        # Add tone guidance
        tone = global_config.get("tone", "")
        if env_config.get("tone_adjustment"):
            tone = f"{tone}\n{env_config['tone_adjustment']}"
        if tone:
            prompt_parts.append(f"Communication style:\n{tone}")
        
        # Add constraints
        if global_config.get("constraints"):
            prompt_parts.append(f"Constraints:\n{global_config['constraints']}")
        
        system_prompt = "\n\n".join(prompt_parts)
        
        # Cache if enabled
        if self._is_cache_enabled():
            self.cache[cache_key] = system_prompt
        
        return system_prompt
    
    def get_operation_prompt(self, context: PromptContext) -> str:
        """Get the operation-specific prompt"""
        operation_config = self.prompts_config.get("operations", {}).get(context.operation.value, {})
        
        if not operation_config:
            logger.warning(f"No prompt configuration for operation: {context.operation.value}")
            return f"Perform {context.operation.value} operation."
        
        prompt_parts = []
        
        # Add base prompt
        if operation_config.get("base"):
            base_prompt = self._apply_template(operation_config["base"], context.variables)
            prompt_parts.append(base_prompt)
        
        # Add specific sections based on operation
        for section in ["evaluation_criteria", "compatibility_analysis", "migration_planning",
                       "risk_assessment", "detection_rules", "fix_suggestions",
                       "structure", "field_documentation", "health_scoring",
                       "recommendations", "risk_identification", "flow_validation",
                       "bottleneck_detection", "optimization_suggestions",
                       "intent_recognition", "operation_mapping", "response_generation",
                       "fix_strategy", "validation", "impact_assessment", "coordination_plan"]:
            
            if section in operation_config:
                section_prompt = self._apply_template(
                    operation_config[section],
                    context.variables
                )
                prompt_parts.append(section_prompt)
        
        # Add output format if specified
        if operation_config.get("output_format"):
            prompt_parts.append(f"Output Format:\n{operation_config['output_format']}")
        
        return "\n\n".join(prompt_parts)
    
    def get_full_prompt(self, context: PromptContext, user_input: str) -> str:
        """Get the complete prompt including system, operation, and user input"""
        system_prompt = self.get_system_prompt(context)
        operation_prompt = self.get_operation_prompt(context)
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{operation_prompt}\n\nUser Input:\n{user_input}"
        
        # Add chain-of-thought if enabled
        if self._use_chain_of_thought():
            full_prompt = f"{full_prompt}\n\nLet's think step by step:"
        
        return full_prompt
    
    def get_template_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Get a custom template prompt"""
        templates = self.prompts_config.get("templates", {})
        
        if template_name not in templates:
            logger.warning(f"Template {template_name} not found")
            return ""
        
        template = templates[template_name]
        return self._apply_template(template, variables)
    
    def _apply_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """Apply variable substitution to a template string"""
        if not variables:
            return template_str
        
        try:
            # Use safe substitution to avoid KeyError for missing variables
            template = Template(template_str)
            return template.safe_substitute(**variables)
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            return template_str
    
    def get_settings(self) -> Dict[str, Any]:
        """Get prompt engineering settings"""
        return self.prompts_config.get("settings", {})
    
    def get_max_tokens(self) -> int:
        """Get max tokens setting"""
        return self.get_settings().get("max_tokens", 2000)
    
    def get_temperature(self) -> float:
        """Get temperature setting"""
        return self.get_settings().get("temperature", 0.7)
    
    def _use_chain_of_thought(self) -> bool:
        """Check if chain-of-thought reasoning should be used"""
        return self.get_settings().get("use_chain_of_thought", True)
    
    def _is_cache_enabled(self) -> bool:
        """Check if prompt caching is enabled"""
        return self.get_settings().get("cache_prompts", True)
    
    def requires_confirmation(self, operation: str) -> bool:
        """Check if an operation requires confirmation"""
        require_confirmation = self.get_settings().get("require_confirmation_for", [])
        return operation in require_confirmation
    
    def get_risk_tolerance(self, environment: str) -> str:
        """Get risk tolerance for an environment"""
        env_config = self.prompts_config.get("environments", {}).get(environment, {})
        return env_config.get("risk_tolerance", "medium")
    
    def format_response(self, response: str, format_type: Optional[str] = None) -> str:
        """Format response according to settings"""
        if format_type is None:
            format_type = self.get_settings().get("output_format", "markdown")
        
        if format_type == "markdown":
            # Already in markdown format
            return response
        elif format_type == "json":
            # Try to extract JSON from response
            import json
            try:
                # Look for JSON blocks in the response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                    return json.dumps(json.loads(json_str), indent=2)
                return response
            except:
                return response
        else:
            # Plain text - remove markdown formatting
            response = response.replace("**", "")
            response = response.replace("*", "")
            response = response.replace("#", "")
            response = response.replace("`", "")
            return response
    
    def get_examples_for_operation(self, operation: PromptOperation, count: Optional[int] = None) -> List[str]:
        """Get few-shot examples for an operation"""
        if not self.get_settings().get("include_examples", True):
            return []
        
        if count is None:
            count = self.get_settings().get("example_count", 2)
        
        # In a real implementation, this would fetch from a examples database
        # For now, return empty list
        return []
    
    def customize_for_organization(self, org_config: Dict[str, Any]):
        """Customize prompts for a specific organization"""
        # Merge organization-specific configuration
        if org_config.get("global"):
            self.prompts_config["global"].update(org_config["global"])
        
        if org_config.get("operations"):
            for op, config in org_config["operations"].items():
                if op in self.prompts_config["operations"]:
                    self.prompts_config["operations"][op].update(config)
        
        # Clear cache after customization
        self.cache.clear()
        logger.info("Prompts customized for organization")


class PromptBuilder:
    """Builder class for constructing complex prompts"""
    
    def __init__(self, manager: PromptManager):
        self.manager = manager
        self.context = None
        self.sections = []
        
    def with_operation(self, operation: PromptOperation) -> 'PromptBuilder':
        """Set the operation for the prompt"""
        if not self.context:
            self.context = PromptContext(operation=operation)
        else:
            self.context.operation = operation
        return self
    
    def with_environment(self, environment: str) -> 'PromptBuilder':
        """Set the environment for the prompt"""
        if not self.context:
            self.context = PromptContext(operation=PromptOperation.NLP_QUERY, environment=environment)
        else:
            self.context.environment = environment
        return self
    
    def with_variables(self, **variables) -> 'PromptBuilder':
        """Add context variables for templating"""
        if not self.context:
            self.context = PromptContext(operation=PromptOperation.NLP_QUERY)
        
        if self.context.variables is None:
            self.context.variables = {}
        
        self.context.variables.update(variables)
        return self
    
    def add_section(self, section: str) -> 'PromptBuilder':
        """Add a custom section to the prompt"""
        self.sections.append(section)
        return self
    
    def add_examples(self, count: int = 2) -> 'PromptBuilder':
        """Add few-shot examples to the prompt"""
        examples = self.manager.get_examples_for_operation(self.context.operation, count)
        if examples:
            examples_section = "Examples:\n" + "\n".join(examples)
            self.sections.append(examples_section)
        return self
    
    def build(self, user_input: str = "") -> str:
        """Build the final prompt"""
        if not self.context:
            raise ValueError("Context not set for prompt building")
        
        base_prompt = self.manager.get_full_prompt(self.context, user_input)
        
        if self.sections:
            additional = "\n\n".join(self.sections)
            return f"{base_prompt}\n\n{additional}"
        
        return base_prompt


def load_prompt_manager(config_path: Optional[str] = None) -> PromptManager:
    """Factory function to load prompt manager"""
    if config_path:
        return PromptManager(config_path)
    
    # Try to find prompts.yaml in common locations
    for path in ["prompts.yaml", "config/prompts.yaml", "../prompts.yaml"]:
        if Path(path).exists():
            return PromptManager(path)
    
    # Use defaults if no file found
    return PromptManager()


# Example usage
if __name__ == "__main__":
    # Initialize prompt manager
    manager = load_prompt_manager()
    
    # Example 1: Get prompt for schema analysis
    context = PromptContext(
        operation=PromptOperation.SCHEMA_ANALYSIS,
        environment="production",
        variables={
            "schema_name": "user-events",
            "version": 3,
            "environment": "production",
            "compatibility_mode": "BACKWARD"
        }
    )
    
    prompt = manager.get_full_prompt(context, "Analyze the user-events schema")
    print("Schema Analysis Prompt:")
    print(prompt)
    print("\n" + "="*50 + "\n")
    
    # Example 2: Use prompt builder
    builder = PromptBuilder(manager)
    prompt = (builder
             .with_operation(PromptOperation.SCHEMA_EVOLUTION)
             .with_environment("production")
             .with_variables(
                 subject="order-events",
                 current_version=5,
                 consumer_count=12,
                 compatibility_mode="FULL"
             )
             .add_examples(2)
             .build("Evaluate adding a new required field"))
    
    print("Schema Evolution Prompt:")
    print(prompt)