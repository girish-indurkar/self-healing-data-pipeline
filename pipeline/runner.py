"""
Main pipeline runner for the self-healing data pipeline.

Orchestrates the full self-healing loop:
  Load CSV → Validate → Diagnose → (Approve) → Fix → Re-validate
"""

import logging
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

from self_healing_pipeline.agent.diagnose import SAFE_ACTIONS, RISKY_ACTIONS, diagnose
from self_healing_pipeline.apply_fix import apply_fix, EscalateError
from self_healing_pipeline.validator import validate_schema, DEFAULT_SCHEMA

logger = logging.getLogger(__name__)
console = Console()


def _show_errors(errors: list[dict]) -> None:
    """Display validation errors in a rich table."""
    table = Table(title="🔍 Validation Errors", show_lines=True)
    table.add_column("Type", style="red bold")
    table.add_column("Details", style="yellow")
    for err in errors:
        details_str = ", ".join(f"{k}: {v}" for k, v in err["details"].items())
        table.add_row(err["error_type"], details_str)
    console.print(table)


def _show_diagnosis(diag: dict) -> None:
    """Display diagnosis result."""
    confidence = diag.get("confidence", 0)
    conf_color = "green" if confidence >= 0.7 else "yellow" if confidence >= 0.4 else "red"
    console.print(f"\n🩺 [bold]Root Cause:[/bold] {diag.get('root_cause', 'Unknown')}")
    console.print(f"   [dim]Reasoning:[/dim] {diag.get('reasoning', 'N/A')}")
    console.print(f"   [dim]Source:[/dim] {diag.get('source', 'N/A')}")
    console.print(f"   [{conf_color}]Confidence: {confidence:.0%}[/{conf_color}]")
    fix = diag.get("fix", {})
    action = fix.get("action", "unknown")
    action_color = "green" if action in SAFE_ACTIONS else "yellow"
    console.print(f"   [{action_color}]Proposed Fix: {fix}[/{action_color}]")


def run_pipeline(
    csv_path: str | Path,
    expected_schema: dict | None = None,
    max_retries: int = 3,
    auto_approve: bool = False,
) -> tuple[pd.DataFrame | None, dict]:
    """
    Run the self-healing pipeline on a CSV file.

    Args:
        csv_path: Path to the CSV file to process.
        expected_schema: Expected schema dict. Uses DEFAULT_SCHEMA if None.
        max_retries: Maximum number of heal attempts.
        auto_approve: If True, auto-approve risky fixes without prompting.

    Returns:
        Tuple of (cleaned DataFrame or None, report dict).
    """
    csv_path = Path(csv_path)
    if expected_schema is None:
        expected_schema = DEFAULT_SCHEMA

    report = {
        "input_file": str(csv_path),
        "errors_found": [],
        "fixes_applied": [],
        "status": "pending",
    }

    # Step 1: Load CSV
    console.print(f"\n📂 Loading [bold]{csv_path.name}[/bold]...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        console.print(f"[red]❌ File not found: {csv_path}[/red]")
        report["status"] = "failed"
        report["error"] = f"File not found: {csv_path}"
        return None, report
    except Exception as e:
        console.print(f"[red]❌ Failed to load CSV: {e}[/red]")
        report["status"] = "failed"
        report["error"] = str(e)
        return None, report

    console.print(f"   Loaded {len(df)} rows × {len(df.columns)} columns")

    # Step 2-7: Validate → Diagnose → Fix loop
    applied_fixes = []
    for attempt in range(1, max_retries + 1):
        console.print(f"\n{'─' * 50}")
        console.print(f"🔄 [bold]Healing Attempt {attempt}/{max_retries}[/bold]")

        # Validate
        errors = validate_schema(df, expected_schema)
        if not errors:
            console.print("[green]✅ All validations passed![/green]")
            report["status"] = "success"
            break

        report["errors_found"].extend(errors)
        _show_errors(errors)

        # Diagnose first error
        error = errors[0]
        console.print("\n🤖 Diagnosing...")
        diag = diagnose(error, expected_schema, applied_fixes)
        _show_diagnosis(diag)

        fix = diag.get("fix", {})
        action = fix.get("action", "unknown")

        # Check approval for risky actions
        if action in RISKY_ACTIONS and not auto_approve:
            if action == "escalate":
                console.print(f"\n[red]🚨 Escalation required: {fix.get('reason')}[/red]")
                report["status"] = "escalated"
                report["escalation_reason"] = fix.get("reason")
                return df, report

            console.print(f"\n[yellow]⚠️ Risky action: {action}[/yellow]")
            user_input = console.input("[yellow]Approve this fix? (yes/no): [/yellow]").strip().lower()
            if user_input not in ("yes", "y"):
                console.print("[dim]Fix skipped by user.[/dim]")
                continue

        # Apply fix
        try:
            df = apply_fix(df, fix)
            applied_fixes.append(fix)
            report["fixes_applied"].append({
                "attempt": attempt,
                "diagnosis": diag,
                "fix": fix,
                "result": "applied",
            })
        except EscalateError as e:
            console.print(f"\n[red]🚨 {e}[/red]")
            report["status"] = "escalated"
            report["escalation_reason"] = str(e)
            return df, report
        except Exception as e:
            console.print(f"[red]❌ Fix failed: {e}[/red]")
            report["fixes_applied"].append({
                "attempt": attempt,
                "fix": fix,
                "result": f"failed: {e}",
            })
    else:
        # Exhausted all retries
        final_errors = validate_schema(df, expected_schema)
        if final_errors:
            console.print(f"\n[yellow]⚠️ {len(final_errors)} error(s) remain after {max_retries} attempts[/yellow]")
            report["status"] = "partial"
        else:
            report["status"] = "success"

    return df, report

