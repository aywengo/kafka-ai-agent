#!/usr/bin/env python
# examples/prompt_customization_demo.py
"""
Demo script showing how to customize system prompts for the Kafka AI Agent
"""

import asyncio
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka_ai_agent_configurable import ConfigurableKafkaAIAgent, PromptConfigurationUI
from prompt_manager import PromptOperation, PromptContext, PromptBuilder

console = Console()


async def demo_default_prompts():
    """Demo: Using default prompts"""
    console.print("\n[bold cyan]Demo 1: Default Prompts[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    
    # Analyze a schema with default prompts
    console.print("Analyzing schema with default prompts...")
    
    result = await agent.analyze_schema_with_prompts(
        "user-events",
        "dev"
    )
    
    console.print(Panel.fit(
        f"Analysis completed using default prompts\n"
        f"Subject: {result['subject']}\n"
        f"Version: {result['version']}",
        title="Default Analysis"
    ))
    
    # Show part of the analysis
    console.print("\n[cyan]Analysis Result (excerpt):[/cyan]")
    console.print(result['analysis'][:500] + "...")


async def demo_environment_specific_prompts():
    """Demo: Environment-specific prompt behavior"""
    console.print("\n[bold cyan]Demo 2: Environment-Specific Prompts[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    
    # Compare prompts for different environments
    environments = ["development", "staging", "production"]
    
    for env in environments:
        context = PromptContext(
            operation=PromptOperation.SCHEMA_EVOLUTION,
            environment=env
        )
        
        system_prompt = agent.prompt_manager.get_system_prompt(context)
        
        console.print(f"\n[yellow]Environment: {env}[/yellow]")
        console.print(f"Risk Tolerance: {agent.prompt_manager.get_risk_tolerance(env)}")
        
        # Show environment-specific tone
        env_config = agent.prompt_manager.prompts_config.get("environments", {}).get(env, {})
        if env_config.get("tone_adjustment"):
            console.print(f"Tone: {env_config['tone_adjustment'][:100]}...")


async def demo_custom_organization_prompts():
    """Demo: Customizing prompts for an organization"""
    console.print("\n[bold cyan]Demo 3: Organization-Specific Customization[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    
    # Create custom organization configuration
    org_config = {
        "global": {
            "role": """
            You are a Kafka expert for ACME Corp, specializing in:
            - E-commerce event streaming
            - Real-time fraud detection
            - Customer behavior analytics
            
            Always consider ACME's specific requirements:
            - PCI compliance for payment data
            - GDPR compliance for EU customers
            - 99.99% uptime SLA
            """,
            "tone": """
            - Use ACME Corp terminology
            - Reference internal documentation codes
            - Be concise but thorough
            - Always include compliance considerations
            """
        },
        "operations": {
            "schema_analysis": {
                "evaluation_criteria": """
                Evaluate based on ACME standards:
                1. PCI compliance for payment fields
                2. GDPR compliance for PII
                3. Performance SLA requirements
                4. Data retention policies
                5. Internal naming conventions (ACME-SCHEMA-001)
                """
            }
        }
    }
    
    console.print("[yellow]Applying ACME Corp customization...[/yellow]")
    await agent.customize_prompts(org_config)
    
    # Test with customized prompts
    result = await agent.analyze_schema_with_prompts(
        "payment-events",
        "production"
    )
    
    console.print(Panel.fit(
        "Analysis now includes:\n"
        "• PCI compliance checks\n"
        "• GDPR considerations\n"
        "• ACME-specific standards",
        title="Customized Analysis"
    ))


async def demo_prompt_builder():
    """Demo: Using the PromptBuilder for complex prompts"""
    console.print("\n[bold cyan]Demo 4: Prompt Builder[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    
    # Build a complex prompt
    builder = PromptBuilder(agent.prompt_manager)
    
    prompt = (builder
             .with_operation(PromptOperation.SCHEMA_EVOLUTION)
             .with_environment("production")
             .with_variables(
                 subject="order-events",
                 current_version=5,
                 consumer_count=25,
                 daily_message_volume=5000000,
                 business_criticality="CRITICAL",
                 compatibility_mode="FULL"
             )
             .add_section("Special Considerations:\n- Black Friday traffic surge expected\n- New payment provider integration")
             .add_examples(2)
             .build("Evaluate adding new field 'loyalty_points' as required field"))
    
    console.print("[cyan]Built Complex Prompt:[/cyan]")
    console.print(Panel(
        prompt[:800] + "...",
        title="Generated Prompt"
    ))


async def demo_interactive_customization():
    """Demo: Interactive prompt customization"""
    console.print("\n[bold cyan]Demo 5: Interactive Customization[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    ui = PromptConfigurationUI(agent)
    
    console.print("[yellow]Let's customize the AI behavior interactively![/yellow]\n")
    
    # Get user input for customization
    if Confirm.ask("Would you like to customize the AI role?"):
        role = Prompt.ask(
            "Enter custom AI role description",
            default="You are a Kafka expert focused on data quality and performance."
        )
        await ui.update_global_role(role)
        console.print("[green]✓[/green] Role updated")
    
    if Confirm.ask("Would you like to set a custom tone for production?"):
        tone = Prompt.ask(
            "Enter tone for production environment",
            default="Be extremely cautious and always provide rollback procedures."
        )
        await ui.set_environment_tone("production", tone)
        console.print("[green]✓[/green] Production tone updated")
    
    if Confirm.ask("Would you like to add a custom template?"):
        template_name = Prompt.ask("Template name", default="incident_analysis")
        template_content = """
        Analyze this production incident:
        Incident: ${incident_description}
        Time: ${incident_time}
        Impact: ${impact_level}
        
        Provide:
        1. Root cause analysis
        2. Immediate mitigation
        3. Long-term prevention
        """
        await ui.add_custom_template(template_name, template_content)
        console.print("[green]✓[/green] Template added")
    
    # Show current configuration
    console.print("\n[cyan]Current Prompt Configuration:[/cyan]")
    config = ui.get_current_prompts()
    
    yaml_str = yaml.dump(config, default_flow_style=False)[:1000]
    syntax = Syntax(yaml_str, "yaml", theme="monokai")
    console.print(syntax)


async def demo_prompt_testing():
    """Demo: Testing prompts before using them"""
    console.print("\n[bold cyan]Demo 6: Prompt Testing[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    ui = PromptConfigurationUI(agent)
    
    # Test different operations
    test_cases = [
        (
            PromptOperation.BREAKING_CHANGES,
            "Field 'user_id' removed from schema"
        ),
        (
            PromptOperation.CAPACITY_PLANNING,
            "Current: 1M msg/day, Expected growth: 50% monthly"
        ),
        (
            PromptOperation.ERROR_ANALYSIS,
            "SerializationException: Unknown magic byte"
        )
    ]
    
    for operation, test_input in test_cases:
        console.print(f"\n[yellow]Testing {operation.value}:[/yellow]")
        
        prompt = await ui.test_prompt(operation, test_input, "production")
        
        console.print(Panel(
            prompt[:400] + "...",
            title=f"{operation.value} Prompt"
        ))


async def demo_dynamic_reload():
    """Demo: Dynamic prompt reloading"""
    console.print("\n[bold cyan]Demo 7: Dynamic Prompt Reloading[/bold cyan]\n")
    
    agent = ConfigurableKafkaAIAgent()
    await agent.initialize()
    
    console.print("[yellow]Original prompts loaded from prompts.yaml[/yellow]")
    
    # Show original settings
    original_max_tokens = agent.prompt_manager.get_max_tokens()
    original_temp = agent.prompt_manager.get_temperature()
    
    console.print(f"Max Tokens: {original_max_tokens}")
    console.print(f"Temperature: {original_temp}")
    
    console.print("\n[yellow]Modifying prompts.yaml externally...[/yellow]")
    console.print("(In production, this would be done through a UI or API)\n")
    
    # Simulate external modification
    if Confirm.ask("Reload prompts from file?"):
        await agent.reload_prompts()
        console.print("[green]✓[/green] Prompts reloaded")
        
        # Show new settings
        new_max_tokens = agent.prompt_manager.get_max_tokens()
        new_temp = agent.prompt_manager.get_temperature()
        
        if new_max_tokens != original_max_tokens or new_temp != original_temp:
            console.print(f"\nNew Max Tokens: {new_max_tokens}")
            console.print(f"New Temperature: {new_temp}")
        else:
            console.print("Settings unchanged")


async def main():
    """Run all prompt customization demos"""
    console.print("""
[bold magenta]╔══════════════════════════════════════════════════════════════╗
║     Kafka AI Agent - Prompt Customization Demo              ║
║                                                              ║
║  Demonstrating configurable system prompts for:             ║
║  • Environment-specific behavior                            ║
║  • Organization customization                               ║
║  • Dynamic prompt building                                  ║
║  • Interactive configuration                                ║
╚══════════════════════════════════════════════════════════════╝[/bold magenta]
    """)
    
    demos = [
        ("Default Prompts", demo_default_prompts),
        ("Environment-Specific Prompts", demo_environment_specific_prompts),
        ("Organization Customization", demo_custom_organization_prompts),
        ("Prompt Builder", demo_prompt_builder),
        ("Interactive Customization", demo_interactive_customization),
        ("Prompt Testing", demo_prompt_testing),
        ("Dynamic Reload", demo_dynamic_reload)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        console.print(f"\n[bold green]═══ Demo {i}/{len(demos)}: {name} ═══[/bold green]")
        
        try:
            await demo_func()
            await asyncio.sleep(1)
        except Exception as e:
            console.print(f"[red]Error in {name}: {e}[/red]")
    
    console.print("""
\n[bold green]✅ Demo Complete![/bold green]

[cyan]Key Takeaways:[/cyan]
• System prompts are fully configurable via YAML files
• Different environments can have different AI behaviors
• Organizations can customize prompts for their specific needs
• Prompts can be tested and validated before deployment
• Dynamic reloading allows runtime configuration changes
• PromptBuilder enables complex prompt construction

[yellow]This flexibility allows the Kafka AI Agent to adapt to any organization's 
specific requirements, terminology, and compliance needs![/yellow]
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")