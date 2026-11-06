"""
Interactive CLI for the self-healing data pipeline.

Provides a conversational interface where users can load datasets
and trigger self-healing by typing natural commands like:
  "hi dataset", "datapipeline", "heal", "fix my data", etc.
"""

import os
import sys
import logging
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from self_healing_pipeline.pipeline import run_pipeline
from self_healing_pipeline.validator import validate_schema, DEFAULT_SCHEMA

logger = logging.getLogger(__name__)
console = Console()

# Keywords that trigger different actions
GREETING_KEYWORDS = {"hi", "hello", "hey", "greetings", "howdy", "sup"}
DATA_KEYWORDS = {"dataset", "data", "load", "csv", "file", "open", "import"}
PIPELINE_KEYWORDS = {"datapipeline", "pipeline", "heal", "self-heal", "selfheal",
                     "run", "fix", "repair", "diagnose", "check", "validate"}
STATUS_KEYWORDS = {"status", "report", "result", "summary"}
SCHEMA_KEYWORDS = {"schema", "columns", "structure", "expected"}
HELP_KEYWORDS = {"help", "commands", "?", "usage"}
EXIT_KEYWORDS = {"exit", "quit", "bye", "q", "stop", "close"}

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║           🔧 Self-Healing Data Pipeline Agent 🔧              ║
║                                                               ║
║   Automatically detect and fix data quality issues            ║
║   Powered by Grok (xAI) + Rule-based Fallback                ║
║                                                               ║
║   Type 'help' for commands or just describe what you need!    ║
╚═══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
[bold cyan]Available Commands:[/bold cyan]

  [green]hi / hello[/green]          → Greet the agent
  [green]dataset / load[/green]      → Load a CSV dataset
  [green]datapipeline / heal[/green] → Run self-healing on loaded data
  [green]schema[/green]              → View expected schema
  [green]status / report[/green]     → View last healing report
  [green]help[/green]                → Show this help
  [green]exit / quit[/green]         → Exit

[bold yellow]💡 Pro Tips:[/bold yellow]
  • Type "[italic]hi dataset[/italic]" to load + preview data
  • Type "[italic]datapipeline[/italic]" or "[italic]fix[/italic]" to self-heal
  • You can combine keywords naturally!
"""


class InteractiveSession:
    """Manages the interactive CLI session state."""

    def __init__(self):
        self.df: pd.DataFrame | None = None
        self.csv_path: str | None = None
        self.last_report: dict | None = None
        self.schema = DEFAULT_SCHEMA

    def show_welcome(self):
        """Display welcome banner."""
        console.print(BANNER, style="bold blue")
        api_key = os.getenv("XAI_API_KEY")
        if api_key:
            console.print("  🟢 Grok API key detected — LLM diagnosis active\n", style="green")
        else:
            console.print("  🟡 No XAI_API_KEY — using rule-based fallback\n", style="yellow")

    def show_help(self):
        """Display help information."""
        console.print(Panel(HELP_TEXT, title="Help", border_style="cyan"))

    def show_schema(self):
        """Display the expected schema."""
        table = Table(title="📋 Expected Schema", box=box.ROUNDED)
        table.add_column("Column", style="cyan bold")
        table.add_column("Type", style="green")
        table.add_column("Nullable", style="yellow")
        table.add_column("Unique", style="magenta")
        for col, props in self.schema.items():
            table.add_row(
                col,
                props.get("type", "str"),
                "Yes" if props.get("nullable", True) else "No",
                "Yes" if props.get("unique", False) else "No",
            )
        console.print(table)

    def load_dataset(self, path: str | None = None):
        """Load a CSV dataset."""
        if not path:
            path = Prompt.ask("\n📂 Enter CSV file path")
        path = path.strip().strip('"').strip("'")

        if not Path(path).exists():
            console.print(f"[red]❌ File not found: {path}[/red]")
            return

        try:
            self.df = pd.read_csv(path)
            self.csv_path = path
            console.print(f"\n[green]✅ Loaded: {path}[/green]")
            console.print(f"   {len(self.df)} rows × {len(self.df.columns)} columns\n")
            self._preview_data()
        except Exception as e:
            console.print(f"[red]❌ Error loading file: {e}[/red]")

    def _preview_data(self):
        """Show a preview of the loaded data."""
        if self.df is None:
            return
        table = Table(title="📊 Data Preview (first 5 rows)", box=box.SIMPLE)
        for col in self.df.columns:
            table.add_column(str(col), style="cyan")
        for _, row in self.df.head(5).iterrows():
            table.add_row(*[str(v) for v in row.values])
        console.print(table)

    def run_healing(self):
        """Run the self-healing pipeline."""
        if self.df is None or self.csv_path is None:
            console.print("[yellow]⚠️ No dataset loaded. Let me ask for one...[/yellow]")
            self.load_dataset()
            if self.df is None:
                return

        console.print(Panel(
            f"🔧 Running self-healing on [bold]{Path(self.csv_path).name}[/bold]",
            style="blue",
        ))

        cleaned_df, report = run_pipeline(
            self.csv_path,
            expected_schema=self.schema,
            max_retries=3,
            auto_approve=False,
        )

        self.last_report = report

        if cleaned_df is not None:
            self.df = cleaned_df

        # Show summary
        status = report.get("status", "unknown")
        status_style = {
            "success": "green",
            "partial": "yellow",
            "failed": "red",
            "escalated": "red",
        }.get(status, "white")

        console.print(f"\n[{status_style}]📝 Pipeline Status: {status.upper()}[/{status_style}]")
        console.print(f"   Fixes applied: {len(report.get('fixes_applied', []))}")

        if status == "success" and cleaned_df is not None:
            console.print("\n[green]✨ Data is clean! Here's a preview:[/green]")
            self._preview_data()

    def show_status(self):
        """Show the last healing report."""
        if not self.last_report:
            console.print("[dim]No healing report yet. Run 'datapipeline' first.[/dim]")
            return

        report = self.last_report
        console.print(Panel(
            f"Status: [bold]{report['status'].upper()}[/bold]\n"
            f"File: {report['input_file']}\n"
            f"Errors found: {len(report.get('errors_found', []))}\n"
            f"Fixes applied: {len(report.get('fixes_applied', []))}",
            title="📝 Last Healing Report",
            border_style="cyan",
        ))

    def parse_and_execute(self, user_input: str):
        """Parse user input and execute appropriate actions."""
        tokens = set(user_input.lower().split())

        # Check for exit
        if tokens & EXIT_KEYWORDS:
            console.print("\n[dim]👋 Goodbye! Happy data healing![/dim]\n")
            sys.exit(0)

        # Track what actions to perform
        should_greet = bool(tokens & GREETING_KEYWORDS)
        should_load = bool(tokens & DATA_KEYWORDS)
        should_heal = bool(tokens & PIPELINE_KEYWORDS)
        should_status = bool(tokens & STATUS_KEYWORDS)
        should_schema = bool(tokens & SCHEMA_KEYWORDS)
        should_help = bool(tokens & HELP_KEYWORDS)

        # If nothing matched, check if the full input contains keywords
        if not any([should_greet, should_load, should_heal, should_status,
                     should_schema, should_help]):
            lower_input = user_input.lower()
            if any(kw in lower_input for kw in PIPELINE_KEYWORDS):
                should_heal = True
            elif any(kw in lower_input for kw in DATA_KEYWORDS):
                should_load = True
            else:
                console.print(
                    "[dim]🤔 I didn't understand that. Type 'help' for available commands.[/dim]"
                )
                return

        # Execute actions in order
        if should_greet:
            console.print("\n[bold green]👋 Hello! I'm your Self-Healing Pipeline Agent![/bold green]")
            console.print("[dim]I can help you detect and fix data quality issues automatically.[/dim]")

        if should_help:
            self.show_help()

        if should_schema:
            self.show_schema()

        if should_load:
            self.load_dataset()

        if should_heal:
            self.run_healing()

        if should_status:
            self.show_status()


def main():
    """Entry point for the interactive CLI."""
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    session = InteractiveSession()
    session.show_welcome()

    # Check for command-line arguments
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        session.load_dataset(csv_path)

    # REPL loop
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]🔧 Pipeline Agent[/bold cyan]")
            if not user_input.strip():
                continue
            session.parse_and_execute(user_input)
        except KeyboardInterrupt:
            console.print("\n[dim]👋 Goodbye![/dim]\n")
            break
        except EOFError:
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            logger.exception("Unexpected error in interactive session")


if __name__ == "__main__":
    main()

