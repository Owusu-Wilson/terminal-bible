import httpx
import random as random_module  # Renamed to avoid conflict
import typer
from typing import Optional
from enum import Enum
from rich.table import Table
from rich.console import Console

from constants import NEW_TESTAMENT_BOOKS, OLD_TESTAMENT_BOOKS, API_BASE, VERSIONS_URL
from models import Testament
from helpers import get_all_books, get_random_book, fetch_versions, fetch_chapter, fetch_verse

app = typer.Typer(help="Bible Verse Terminal App", rich_markup_mode="rich")


# ======================================================================================================


@app.command()
def random(
    version: str = typer.Option("en-kjv", "--version", "-v", help="Bible version"),
    testament: Testament = typer.Option(Testament.ALL, "--testament", "-t", help="Filter by testament"),
    book: Optional[str] = typer.Option(None, "--book", "-b", help="Specify a book", autocompletion=get_all_books),
    chapter: Optional[int] = typer.Option(None, "--chapter", "-c", help="Specify a chapter"),
    verse: Optional[int] = typer.Option(None, "--verse", "-vs", help="Specify a verse")
):
    """Get a random Bible verse (default) or specific verse if arguments provided"""
    try:
        # If no book specified, get random book based on testament
        selected_book = book if book else get_random_book(testament)
        
        # If no chapter specified, get random chapter (1-50)
        selected_chapter = chapter if chapter is not None else random_module.randint(1, 50)
        
        # If no verse specified, get random verse (1-30)
        selected_verse = verse if verse is not None else random_module.randint(1, 30)
        
        verse_data = fetch_verse(version, selected_book, selected_chapter, selected_verse)
        display_result(verse_data["text"], f"{selected_book.title()} {selected_chapter}:{selected_verse}")
        
    except httpx.HTTPStatusError as e:
        typer.secho(f"Verse not found: {selected_book} {selected_chapter}:{selected_verse}", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

# ======================================================================================================

@app.command()
def chapter(
    book: str = typer.Argument(..., help="Book name", autocompletion=get_all_books),
    chapter: int = typer.Argument(..., help="Chapter number"),
    version: str = typer.Option("en-kjv", "--version", "-v", help="Bible version")
):
    """Get an entire chapter"""
    try:
        chapter_data = fetch_chapter(version, book, chapter)
        display_result("\n".join([v["text"] for v in chapter_data["verses"]]), 
                     f"{book.title()} {chapter}")
    except Exception as e:
        typer.secho(f"Error fetching chapter: {e}", fg=typer.colors.RED)


# ======================================================================================================
@app.command()
def versions():
    """List all available Bible versions in a beautiful table"""
    try:
        console = Console()
        versions_data = fetch_versions()
        if not isinstance(versions_data, list):
            typer.secho("Unexpected API response format", fg=typer.colors.RED)
            return

        table = Table(title="Available Bible Versions", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=12)
        table.add_column("Language", style="green", width=15)
        table.add_column("Version Name", style="blue", width=40)
        table.add_column("Scope", style="yellow", width=20)
        
        for version in versions_data:
            table.add_row(
                version.get("id", "N/A"),
                version.get("language", {}).get("name", "N/A"),
                version.get("version", "N/A"),
                version.get("scope", "N/A")
            )
        
        console.print(table)
        console.print(f"[bold]Total versions available:[/bold] {len(versions_data)}")
        
    except Exception as e:
        typer.secho(f"Error fetching versions: {e}", fg=typer.colors.RED)


# ======================================================================================================

@app.command()
def books(
    testament: Testament = typer.Option(Testament.ALL, "--testament", "-t", help="Filter by testament")
):
    """List all Bible books"""
    typer.echo("\nBible Books:\n")
    
    if testament in [Testament.OLD, Testament.ALL]:
        typer.secho("Old Testament:", fg=typer.colors.YELLOW, bold=True)
        for book in OLD_TESTAMENT_BOOKS:
            typer.echo(f"  {book.title()}")
    
    if testament in [Testament.NEW, Testament.ALL]:
        typer.secho("\nNew Testament:", fg=typer.colors.YELLOW, bold=True)
        for book in NEW_TESTAMENT_BOOKS:
            typer.echo(f"  {book.title()}")

def display_result(text: str, reference: str):
    """Display the verse/chapter with formatting"""
    typer.echo("\n" + "=" * 50)
    typer.secho(reference, fg=typer.colors.GREEN, bold=True)
    typer.echo("-" * 50)
    typer.secho(text, fg=typer.colors.BLUE)
    typer.echo("=" * 50 + "\n")

if __name__ == "__main__":
    app()