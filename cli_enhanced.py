#!/usr/bin/env python
# cli_enhanced.py
"""
Enhanced CLI for Kafka AI Agent with multi-MCP support
"""

import asyncio
import argparse
import json
import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.panel import Panel
from rich import print as rprint

from kafka_ai_agent_enhanced import EnhancedKafkaAIAgent, EnhancedSchemaMonitor

console = Console()


class KafkaAICLI:
    """Enhanced CLI for Kafka AI Agent"""
    
    def __init__(self):
        self.agent: Optional[EnhancedKafkaAIAgent] = None
        
    async def initialize(self):
        """Initialize the agent"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing Kafka AI Agent...", total=None)
            
            self.agent = EnhancedKafkaAIAgent()
            await self.agent.initialize()
            
            progress.update(task, completed=True)
        
        console.print("[green]✓[/green] Kafka AI Agent initialized successfully")
    
    async def ecosystem_analysis(self, args):
        """Perform ecosystem analysis"""
        await self.initialize()
        
        with console.status(f"Analyzing {args.environment} environment..."):
            analysis = await self.agent.comprehensive_ecosystem_analysis(args.environment)
        
        # Display results in a table
        table = Table(title=f"Ecosystem Analysis - {args.environment}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Health Score", f"{analysis.health_score:.1f}%")
        table.add_row("Topics", str(len(analysis.topics)))
        table.add_row("Schemas", str(len(analysis.schemas)))
        table.add_row("Consumer Groups", str(len(analysis.consumer_groups)))
        table.add_row("Risk Level", analysis.risk_assessment.get("level", "N/A"))
        
        console.print(table)
        
        if analysis.alignment_issues:
            console.print("\n[yellow]⚠ Alignment Issues:[/yellow]")
            for issue in analysis.alignment_issues:
                console.print(f"  • {issue}")
        
        if analysis.recommendations:
            console.print("\n[cyan]💡 Recommendations:[/cyan]")
            for rec in analysis.recommendations:
                console.print(f"  • {rec}")
    
    async def pipeline_analysis(self, args):
        """Analyze data pipeline"""
        await self.initialize()
        
        topics = args.topics.split(',')
        
        with console.status(f"Analyzing pipeline: {' -> '.join(topics)}..."):
            analysis = await self.agent.analyze_data_pipeline(
                args.name,
                topics,
                args.environment
            )
        
        console.print(Panel.fit(
            f"[bold]Pipeline: {analysis.pipeline_name}[/bold]\n"
            f"Topics: {' -> '.join(analysis.topics)}",
            title="Pipeline Analysis"
        ))
        
        # Show compatibility matrix
        if analysis.compatibility_matrix:
            console.print("\n[cyan]Compatibility Matrix:[/cyan]")
            for flow, compatible in analysis.compatibility_matrix.items():
                status = "[green]✓[/green]" if compatible else "[red]✗[/red]"
                console.print(f"  {flow}: {status}")
        
        # Show bottlenecks
        if analysis.bottlenecks:
            console.print("\n[yellow]⚠ Bottlenecks:[/yellow]")
            for bottleneck in analysis.bottlenecks:
                console.print(f"  • {bottleneck}")
        
        # Show optimization suggestions
        if analysis.optimization_suggestions:
            console.print("\n[cyan]💡 Optimization Suggestions:[/cyan]")
            for suggestion in analysis.optimization_suggestions:
                console.print(f"  • {suggestion}")
    
    async def schema_evolution(self, args):
        """Manage schema evolution"""
        await self.initialize()
        
        # Load proposed changes from file
        with open(args.changes_file, 'r') as f:
            changes = json.load(f)
        
        with console.status(f"Analyzing schema evolution for {args.subject}..."):
            result = await self.agent.intelligent_schema_evolution(
                args.subject,
                changes,
                args.environment
            )
        
        # Display compatibility status
        if result["compatibility"].get("is_compatible", False):
            console.print("[green]✓[/green] Schema changes are compatible")
        else:
            console.print("[red]✗[/red] Schema changes have compatibility issues")
            
            if args.auto_fix:
                console.print("\n[yellow]Attempting auto-fix...[/yellow]")
                fix_result = await self.agent.auto_fix_compatibility_issues(
                    args.subject,
                    result["proposed_version"],
                    args.environment
                )
                
                if fix_result["fixed"]:
                    console.print("[green]✓[/green] Compatibility issues fixed")
                    console.print("\nFixed schema:")
                    syntax = Syntax(
                        json.dumps(fix_result["fixed_schema"], indent=2),
                        "json",
                        theme="monokai"
                    )
                    console.print(syntax)
                else:
                    console.print("[red]✗[/red] Could not auto-fix compatibility issues")
        
        # Show impact analysis
        console.print(f"\n[cyan]Impact Analysis:[/cyan]")
        console.print(f"  Affected consumers: {result['impact_analysis']['consumer_count']}")
        console.print(f"  Risk level: {result['risk_level']}")
        
        # Show migration plan
        if result["migration_plan"]:
            console.print("\n[cyan]Migration Plan:[/cyan]")
            for step in result["migration_plan"]:
                console.print(f"  {step}")
    
    async def topic_health(self, args):
        """Check topic health"""
        await self.initialize()
        
        with console.status(f"Checking health of topic {args.topic}..."):
            health = await self.agent.topic_schema_health_check(
                args.topic,
                args.environment
            )
        
        # Display health status with color coding
        status_color = {
            "HEALTHY": "green",
            "DEGRADED": "yellow",
            "UNHEALTHY": "red"
        }.get(health["health_status"], "white")
        
        console.print(Panel.fit(
            f"[{status_color}]{health['health_status']}[/{status_color}]",
            title=f"Topic Health: {args.topic}"
        ))
        
        # Show metrics
        if health.get("metrics"):
            table = Table(title="Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for metric, value in health["metrics"].items():
                table.add_row(metric, str(value))
            
            console.print(table)
        
        # Show issues
        if health.get("issues"):
            console.print("\n[yellow]⚠ Issues:[/yellow]")
            for issue in health["issues"]:
                console.print(f"  • {issue}")
    
    async def generate_catalog(self, args):
        """Generate data catalog"""
        await self.initialize()
        
        with console.status(f"Generating data catalog for {args.environment}..."):
            catalog = await self.agent.generate_data_catalog(args.environment)
        
        if args.output:
            # Save to file
            with open(args.output, 'w') as f:
                if args.format == "json":
                    json.dump(catalog, f, indent=2)
                else:
                    # Convert to markdown
                    f.write("# Kafka Data Catalog\n\n")
                    f.write(f"Generated: {catalog['generated_at']}\n\n")
                    for topic, doc in catalog['documentation'].items():
                        f.write(f"## {topic}\n\n{doc}\n\n")
            
            console.print(f"[green]✓[/green] Catalog saved to {args.output}")
        else:
            # Display summary
            console.print(Panel.fit(
                f"Topics: {len(catalog['topics'])}\n"
                f"Schemas: {len(catalog['schemas'])}\n"
                f"Data Flows: {len(catalog['data_flows'])}",
                title="Data Catalog Summary"
            ))
    
    async def monitor(self, args):
        """Start monitoring"""
        await self.initialize()
        
        monitor = EnhancedSchemaMonitor(self.agent)
        
        console.print(f"[cyan]Starting monitoring (interval: {args.interval}s)...[/cyan]")
        console.print("Press Ctrl+C to stop\n")
        
        try:
            await monitor.start_monitoring(args.interval)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            console.print("\n[yellow]Monitoring stopped[/yellow]")
            
            # Show alerts
            alerts = monitor.get_alerts()
            if alerts:
                console.print(f"\n[red]Alerts ({len(alerts)}):[/red]")
                for alert in alerts:
                    console.print(f"  • [{alert['environment']}] Score: {alert['health_score']:.1f}")


async def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Kafka AI Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ecosystem analysis
    ecosystem_parser = subparsers.add_parser(
        "ecosystem",
        help="Analyze entire Kafka ecosystem"
    )
    ecosystem_parser.add_argument(
        "--environment", "-e",
        default="dev",
        help="Environment to analyze"
    )
    
    # Pipeline analysis
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Analyze data pipeline"
    )
    pipeline_parser.add_argument(
        "--name", "-n",
        required=True,
        help="Pipeline name"
    )
    pipeline_parser.add_argument(
        "--topics", "-t",
        required=True,
        help="Comma-separated list of topics in order"
    )
    pipeline_parser.add_argument(
        "--environment", "-e",
        default="dev",
        help="Environment"
    )
    
    # Schema evolution
    evolution_parser = subparsers.add_parser(
        "evolve",
        help="Manage schema evolution"
    )
    evolution_parser.add_argument(
        "--subject", "-s",
        required=True,
        help="Schema subject"
    )
    evolution_parser.add_argument(
        "--changes-file", "-c",
        required=True,
        help="JSON file with proposed changes"
    )
    evolution_parser.add_argument(
        "--auto-fix", "-a",
        action="store_true",
        help="Auto-fix compatibility issues"
    )
    evolution_parser.add_argument(
        "--environment", "-e",
        default="dev",
        help="Environment"
    )
    
    # Topic health
    health_parser = subparsers.add_parser(
        "health",
        help="Check topic health"
    )
    health_parser.add_argument(
        "--topic", "-t",
        required=True,
        help="Topic name"
    )
    health_parser.add_argument(
        "--environment", "-e",
        default="dev",
        help="Environment"
    )
    
    # Generate catalog
    catalog_parser = subparsers.add_parser(
        "catalog",
        help="Generate data catalog"
    )
    catalog_parser.add_argument(
        "--environment", "-e",
        default="dev",
        help="Environment"
    )
    catalog_parser.add_argument(
        "--output", "-o",
        help="Output file"
    )
    catalog_parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="json",
        help="Output format"
    )
    
    # Monitor
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Start monitoring"
    )
    monitor_parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Monitoring interval in seconds"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = KafkaAICLI()
    
    try:
        if args.command == "ecosystem":
            await cli.ecosystem_analysis(args)
        elif args.command == "pipeline":
            await cli.pipeline_analysis(args)
        elif args.command == "evolve":
            await cli.schema_evolution(args)
        elif args.command == "health":
            await cli.topic_health(args)
        elif args.command == "catalog":
            await cli.generate_catalog(args)
        elif args.command == "monitor":
            await cli.monitor(args)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())