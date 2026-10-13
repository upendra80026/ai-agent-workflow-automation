import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from core.engine import WorkflowEngine
from core.excel_loader import load_test_questions_from_excel

console = Console()


def interactive_cli():
    engine = WorkflowEngine("AI_Agent_Workflow_Assessment.xlsx")
    test_questions = load_test_questions_from_excel("AI_Agent_Workflow_Assessment.xlsx")

    console.print(Panel.fit(
        "[bold cyan]AI Agent Workflow Automation System[/bold cyan]\n"
        "[dim]Powered by Dynamic Excel Workflow Engine & Pluggable Tool Architecture[/dim]\n\n"
        "Type your request in natural language, choose a sample test question, or type 'exit'.",
        border_style="cyan"
    ))

    console.print("[yellow]Quick Test Examples from Excel:[/yellow]")
    for idx, q in enumerate(test_questions, start=1):
        console.print(f"  [bold cyan]{idx}.[/bold cyan] [dim][{q['workflow_id']}][/dim] \"{q['test_request']}\"")
    console.print("")

    while True:
        user_input = Prompt.ask("\n[bold green]Enter Request (or 1-10, 'all', 'exit')[/bold green]")
        if not user_input or user_input.strip().lower() in ["exit", "quit", "q"]:
            console.print("[dim]Exiting agent system. Goodbye![/dim]")
            break

        if user_input.strip().lower() == "all":
            from run_all_tests import run_comprehensive_evaluation
            run_comprehensive_evaluation()
            continue

        # Handle numeric selection
        if user_input.strip().isdigit():
            idx = int(user_input.strip())
            if 1 <= idx <= len(test_questions):
                user_input = test_questions[idx - 1]["test_request"]
                console.print(f"[dim]Running preset {idx}: \"{user_input}\"[/dim]")

        console.print(f"\n[cyan]Thinking & Routing Query...[/cyan]")
        result = engine.execute(user_input)

        # Print formatted agent trace
        console.print(Panel(
            f"[bold]Selected Workflow:[/bold] [yellow]{result.workflow_id}[/yellow] - [bold]{result.workflow_name}[/bold]\n"
            f"[bold]Confidence:[/bold] {result.confidence_score*100:.1f}%\n"
            f"[bold]Reasoning:[/bold] {result.selection_reasoning}\n"
            f"[bold]Total Latency:[/bold] {result.total_duration_ms:.1f} ms",
            title="🎯 Workflow Identification",
            border_style="yellow"
        ))

        steps_text = []
        for s in result.steps_executed:
            tool_info = f" [cyan]({s.tool_called})[/cyan]" if s.tool_called else ""
            status_badge = "[green]✓ SUCCESS[/green]" if s.status == "SUCCESS" else f"[red]✗ {s.status}[/red]"
            steps_text.append(f"  [bold]{s.step_number}.[/bold] {s.step_name}{tool_info} - {status_badge} ({s.duration_ms:.1f}ms)")
            if s.output_summary:
                steps_text.append(f"     [dim]↳ Output: {s.output_summary}[/dim]")

        console.print(Panel(
            "\n".join(steps_text),
            title=f"📋 Steps Executed ({len(result.steps_executed)})",
            border_style="blue"
        ))

        if result.decisions_made:
            dec_text = []
            for d in result.decisions_made:
                icon = "[green]✓[/green]" if d.condition_met else "[red]✗[/red]"
                dec_text.append(f"  {icon} [bold]Rule:[/bold] `{d.rule}`\n     ↳ [dim]Action:[/dim] {d.action_taken}")
            console.print(Panel(
                "\n".join(dec_text),
                title=f"⚖️ Conditions & Decisions Evaluated ({len(result.decisions_made)})",
                border_style="magenta"
            ))

        console.print(Panel(
            Markdown(result.final_output),
            title="🏁 Final Agent Result",
            border_style="green"
        ))


if __name__ == "__main__":
    interactive_cli()
