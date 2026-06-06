"""
main.py — CLI entrypoint for the Recipe Recommendation Agent.

Usage:
    python main.py [--provider anthropic|openai|groq|gemini]
"""

import argparse
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from recipe_agent import run_agent
from recipe_agent.config import CHROMA_DB_PATH
from recipe_agent.providers import REGISTRY, available_providers

console = Console()

BANNER = """
[bold cyan]  Recipe Recommendation Agent[/bold cyan]
[dim]  Powered by RAG over RecipeNLG[/dim]
"""


def _check_db() -> None:
    if not (os.path.isdir(CHROMA_DB_PATH) and any(os.scandir(CHROMA_DB_PATH))):
        console.print(Panel(
            "[bold red]ChromaDB index not found.[/bold red]\n\n"
            "Run [bold cyan]python ingest.py[/bold cyan] first to build the recipe index.",
            title="Setup Required",
            border_style="red",
        ))
        sys.exit(1)


def _check_api_key(provider: str) -> None:
    env_var = REGISTRY[provider].api_key_env
    if not os.environ.get(env_var):
        console.print(Panel(
            f"[bold red]Missing API key.[/bold red]\n\n"
            f"Set [bold cyan]{env_var}[/bold cyan] before running:\n\n"
            f"    [bold]set {env_var}=your-key-here[/bold]   (Windows)\n"
            f"    [bold]export {env_var}=your-key-here[/bold]   (macOS/Linux)",
            title="Setup Required",
            border_style="red",
        ))
        sys.exit(1)


def _ask(prompt: str) -> str:
    try:
        return Prompt.ask(f"[bold green]{prompt}[/bold green]").strip()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Cancelled.[/yellow]")
        sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recipe Recommendation Agent")
    parser.add_argument(
        "--provider",
        choices=available_providers(),
        default="anthropic",
        help="LLM provider to use (default: anthropic)",
    )
    args = parser.parse_args()
    provider = args.provider

    provider_cls = REGISTRY[provider]
    model_label = f"{provider_cls.model} ({provider})"

    console.print(Panel(
        BANNER + f"\n[dim]  Model: [bold]{model_label}[/bold][/dim]",
        border_style="cyan",
        padding=(0, 2),
    ))

    _check_db()
    _check_api_key(provider)

    console.print()
    console.print("[dim]Enter your preferences below. Press [bold]Ctrl-C[/bold] to exit.[/dim]")
    console.print()

    preferences = _ask("Dietary preferences (e.g. vegetarian, gluten-free, low-carb)") or "no restrictions"
    ingredients = _ask("Available ingredients (comma-separated)") or "pantry staples"

    console.print()
    console.rule(f"[cyan]Searching with {provider_cls.model}…[/cyan]")
    console.print()

    with console.status("[bold cyan]Agent is thinking…[/bold cyan]", spinner="dots"):
        try:
            result = run_agent(preferences=preferences, ingredients=ingredients, provider=provider)
        except Exception as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")
            sys.exit(1)

    console.print()
    console.rule("[cyan]Recommendations[/cyan]")
    console.print()
    console.print(Markdown(result))
    console.print()


if __name__ == "__main__":
    main()
