# examples/multi_mcp_demo.py
"""
Demo script showing the power of multi-MCP integration
Demonstrates how Schema Registry MCP and Kafka Brokers MCP work together
"""

import asyncio
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Import the enhanced agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka_ai_agent_enhanced import EnhancedKafkaAIAgent

console = Console()


async def demo_ecosystem_analysis():
    """Demo: Comprehensive ecosystem analysis using both MCP servers"""
    console.print("\n[bold cyan]🔍 Demo 1: Comprehensive Ecosystem Analysis[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    # Perform comprehensive analysis
    with console.status("Analyzing Kafka ecosystem..."):
        analysis = await agent.comprehensive_ecosystem_analysis("dev")
    
    # Display results
    console.print(Panel.fit(
        f"[green]Health Score: {analysis.health_score:.1f}%[/green]\n"
        f"Topics: {len(analysis.topics)}\n"
        f"Schemas: {len(analysis.schemas)}\n"
        f"Consumer Groups: {len(analysis.consumer_groups)}",
        title="Ecosystem Health"
    ))
    
    if analysis.alignment_issues:
        console.print("\n[yellow]⚠ Issues Found:[/yellow]")
        for issue in analysis.alignment_issues:
            console.print(f"  • {issue}")
    
    if analysis.recommendations:
        console.print("\n[cyan]💡 AI Recommendations:[/cyan]")
        for rec in analysis.recommendations[:3]:
            console.print(f"  • {rec}")
    
    return analysis


async def demo_pipeline_validation():
    """Demo: Validate a data pipeline across multiple topics"""
    console.print("\n[bold cyan]🔄 Demo 2: Data Pipeline Validation[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    # Define a sample pipeline
    pipeline_topics = [
        "raw-events",
        "validated-events",
        "enriched-events",
        "aggregated-events"
    ]
    
    console.print(f"Pipeline: {' → '.join(pipeline_topics)}\n")
    
    with console.status("Analyzing data pipeline..."):
        analysis = await agent.analyze_data_pipeline(
            "event-processing-pipeline",
            pipeline_topics,
            "dev"
        )
    
    # Show compatibility matrix
    table = Table(title="Schema Compatibility Matrix")
    table.add_column("Flow", style="cyan")
    table.add_column("Compatible", style="magenta")
    
    for flow, compatible in analysis.compatibility_matrix.items():
        status = "✅ Yes" if compatible else "❌ No"
        table.add_row(flow, status)
    
    console.print(table)
    
    # Show bottlenecks
    if analysis.bottlenecks:
        console.print("\n[yellow]⚠ Bottlenecks Detected:[/yellow]")
        for bottleneck in analysis.bottlenecks:
            console.print(f"  • {bottleneck}")
    
    # Show optimization suggestions
    if analysis.optimization_suggestions:
        console.print("\n[cyan]💡 Optimization Suggestions:[/cyan]")
        for suggestion in analysis.optimization_suggestions[:3]:
            console.print(f"  • {suggestion}")
    
    return analysis


async def demo_schema_topic_alignment():
    """Demo: Check alignment between schemas and topics"""
    console.print("\n[bold cyan]🔗 Demo 3: Schema-Topic Alignment Check[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    with console.status("Checking schema-topic alignment..."):
        alignment = await agent.unified_client.analyze_topic_schema_alignment("dev")
    
    # Display alignment results
    table = Table(title="Schema-Topic Alignment")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Items", style="yellow")
    
    table.add_row(
        "Topics with Schemas",
        str(len(alignment["topics_with_schemas"])),
        ", ".join(alignment["topics_with_schemas"][:3]) + ("..." if len(alignment["topics_with_schemas"]) > 3 else "")
    )
    
    table.add_row(
        "Topics without Schemas",
        str(len(alignment["topics_without_schemas"])),
        ", ".join(alignment["topics_without_schemas"][:3]) + ("..." if len(alignment["topics_without_schemas"]) > 3 else "")
    )
    
    table.add_row(
        "Orphaned Schemas",
        str(len(alignment["schemas_without_topics"])),
        ", ".join(alignment["schemas_without_topics"][:3]) + ("..." if len(alignment["schemas_without_topics"]) > 3 else "")
    )
    
    console.print(table)
    
    return alignment


async def demo_intelligent_schema_evolution():
    """Demo: Intelligent schema evolution with consumer impact analysis"""
    console.print("\n[bold cyan]🧬 Demo 4: Intelligent Schema Evolution[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    # Propose schema changes
    proposed_changes = {
        "add_fields": [
            {
                "name": "user_segment",
                "type": "string",
                "default": "unknown",
                "doc": "User segmentation category"
            }
        ]
    }
    
    console.print("Proposed Change: Add 'user_segment' field to user-events schema\n")
    
    with console.status("Analyzing schema evolution impact..."):
        result = await agent.intelligent_schema_evolution(
            "user-events",
            proposed_changes,
            "dev"
        )
    
    # Display impact analysis
    console.print(Panel.fit(
        f"[cyan]Compatibility:[/cyan] {'✅ Compatible' if result['compatibility'].get('is_compatible') else '❌ Incompatible'}\n"
        f"[cyan]Affected Consumers:[/cyan] {result['impact_analysis']['consumer_count']}\n"
        f"[cyan]Risk Level:[/cyan] {result['risk_level']}",
        title="Evolution Impact Analysis"
    ))
    
    # Show migration plan
    if result["migration_plan"]:
        console.print("\n[cyan]📋 Migration Plan:[/cyan]")
        for i, step in enumerate(result["migration_plan"][:5], 1):
            console.print(f"  {i}. {step}")
    
    return result


async def demo_topic_health_check():
    """Demo: Topic health check with schema validation"""
    console.print("\n[bold cyan]🏥 Demo 5: Topic Health Check[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    topic = "user-events"
    
    with console.status(f"Checking health of topic '{topic}'..."):
        health = await agent.topic_schema_health_check(topic, "dev")
    
    # Determine color based on health status
    status_color = {
        "HEALTHY": "green",
        "DEGRADED": "yellow",
        "UNHEALTHY": "red"
    }.get(health["health_status"], "white")
    
    # Display health status
    console.print(Panel.fit(
        f"[{status_color}]{health['health_status']}[/{status_color}]",
        title=f"Topic: {topic}"
    ))
    
    # Show metrics
    if health.get("metrics"):
        table = Table(title="Topic Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        for metric, value in health["metrics"].items():
            table.add_row(metric.replace("_", " ").title(), str(value))
        
        console.print(table)
    
    # Show issues if any
    if health.get("issues"):
        console.print("\n[yellow]⚠ Issues:[/yellow]")
        for issue in health["issues"]:
            console.print(f"  • {issue}")
    
    return health


async def demo_consumer_group_analysis():
    """Demo: Analyze consumer group with schema information"""
    console.print("\n[bold cyan]👥 Demo 6: Consumer Group Analysis[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    consumer_group = "analytics-processor"
    
    with console.status(f"Analyzing consumer group '{consumer_group}'..."):
        result = await agent.unified_client.get_consumer_group_schemas(
            consumer_group,
            "dev"
        )
    
    # Display consumer group info
    console.print(Panel.fit(
        f"[cyan]Consumer Group:[/cyan] {result['consumer_group']}\n"
        f"[cyan]Topics:[/cyan] {', '.join(result['topics'])}",
        title="Consumer Group Details"
    ))
    
    # Show schemas for each topic
    console.print("\n[cyan]📋 Topic Schemas:[/cyan]")
    for topic, schema in result["schemas"].items():
        if schema:
            console.print(f"  • {topic}: ✅ Schema registered")
        else:
            console.print(f"  • {topic}: ❌ No schema found")
    
    return result


async def demo_data_catalog_generation():
    """Demo: Generate comprehensive data catalog"""
    console.print("\n[bold cyan]📚 Demo 7: Data Catalog Generation[/bold cyan]\n")
    
    agent = EnhancedKafkaAIAgent()
    await agent.initialize()
    
    with console.status("Generating data catalog..."):
        catalog = await agent.generate_data_catalog("dev")
    
    # Display catalog summary
    console.print(Panel.fit(
        f"[cyan]Topics:[/cyan] {len(catalog['topics'])}\n"
        f"[cyan]Schemas:[/cyan] {len(catalog['schemas'])}\n"
        f"[cyan]Data Flows:[/cyan] {len(catalog['data_flows'])}\n"
        f"[cyan]Generated:[/cyan] {catalog['generated_at']}",
        title="Data Catalog Summary"
    ))
    
    # Show sample documentation
    if catalog["documentation"]:
        sample_topic = list(catalog["documentation"].keys())[0]
        console.print(f"\n[cyan]📝 Sample Documentation (Topic: {sample_topic}):[/cyan]")
        console.print(Panel(
            catalog["documentation"][sample_topic][:500] + "...",
            title="AI-Generated Documentation"
        ))
    
    return catalog


async def main():
    """Run all demos"""
    console.print("""
[bold magenta]╔══════════════════════════════════════════════════════════════╗
║     Kafka AI Agent - Multi-MCP Integration Demo              ║
║                                                              ║
║  Showcasing the power of combining:                         ║
║  • Kafka Schema Registry MCP Server                         ║
║  • Kafka Brokers MCP Server                                 ║
║  • AI-powered intelligence                                  ║
╚══════════════════════════════════════════════════════════════╝[/bold magenta]
    """)
    
    demos = [
        ("Ecosystem Analysis", demo_ecosystem_analysis),
        ("Pipeline Validation", demo_pipeline_validation),
        ("Schema-Topic Alignment", demo_schema_topic_alignment),
        ("Intelligent Schema Evolution", demo_intelligent_schema_evolution),
        ("Topic Health Check", demo_topic_health_check),
        ("Consumer Group Analysis", demo_consumer_group_analysis),
        ("Data Catalog Generation", demo_data_catalog_generation)
    ]
    
    results = {}
    
    for name, demo_func in demos:
        try:
            console.print(f"\n{'='*60}")
            result = await demo_func()
            results[name] = result
            await asyncio.sleep(1)  # Brief pause between demos
        except Exception as e:
            console.print(f"[red]Error in {name}: {e}[/red]")
            results[name] = None
    
    # Summary
    console.print(f"\n{'='*60}")
    console.print("\n[bold green]✅ Demo Complete![/bold green]\n")
    console.print("[cyan]Key Capabilities Demonstrated:[/cyan]")
    console.print("  • Complete ecosystem visibility across schemas and brokers")
    console.print("  • Data pipeline validation with compatibility checking")
    console.print("  • Intelligent schema evolution with impact analysis")
    console.print("  • Topic health monitoring with schema validation")
    console.print("  • Consumer group analysis with schema awareness")
    console.print("  • AI-powered documentation and recommendations")
    console.print("\n[yellow]Ready to transform your Kafka management![/yellow]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")
