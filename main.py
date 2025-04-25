import httpx
import random as random_module  # Renamed to avoid conflict
import typer
from typing import Optional
import pandas as pd
from rich.table import Table
from rich.console import Console

from constants import NEW_TESTAMENT_BOOKS, OLD_TESTAMENT_BOOKS, API_BASE, VERSIONS_URL
from models import Testament
from helpers import get_all_books, get_random_book, fetch_versions, fetch_chapter, fetch_verse, get_random_chapter_verse, get_bible_limits,format_book_name_for_display


app = typer.Typer(help="Bible Verse Terminal App", rich_markup_mode="rich")


# ======================================================================================================

# main.py (updated random command)
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
        
        # Convert to display format for CSV lookup
        display_book = format_book_name_for_display(selected_book)
        
        # If no chapter or verse specified, get random ones within valid limits
        if chapter is None or verse is None:
            valid_chapter, valid_verse = get_random_chapter_verse(selected_book)
            selected_chapter = chapter if chapter is not None else valid_chapter
            selected_verse = verse if verse is not None else valid_verse
        
        # Fetch using API-formatted name
        verse_data = fetch_verse(version, selected_book, selected_chapter, selected_verse)
        
        # Display with properly formatted book name
        display_result(
            verse_data["text"], 
            f"{display_book} {selected_chapter}:{selected_verse}"
        )
        
    except httpx.HTTPStatusError as e:
        display_name = format_book_name_for_display(selected_book)
        typer.secho(
            f"Verse not found: {display_name} {selected_chapter}:{selected_verse}", 
            fg=typer.colors.YELLOW
        )
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED)
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



# =====================================================================================================
# helpers.py (add this function)

# main.py (add this new command)
@app.command()
def limits():
    """Show a table of Bible verse limits grouped by book"""
    try:
        console = Console()
        limits_df = get_bible_limits()
        
        # Group by book and aggregate chapters/verses
        grouped = limits_df.groupby('Book').agg({
            'Chapter': ['count', 'min', 'max'],
            'Verses': ['min', 'max', 'mean']
        }).reset_index()
        
        # Flatten multi-index columns
        grouped.columns = [' '.join(col).strip() for col in grouped.columns.values]
        
        # Create Rich table
        table = Table(title="Bible Verse Limits by Book", show_header=True, header_style="bold magenta")
        table.add_column("Book", style="cyan")
        table.add_column("Chapters", justify="right")
        table.add_column("First Ch.", justify="right")
        table.add_column("Last Ch.", justify="right")
        table.add_column("Min Verses", justify="right")
        table.add_column("Max Verses", justify="right")
        table.add_column("Avg Verses", justify="right")
        
        # Add rows
        for _, row in grouped.iterrows():
            table.add_row(
                row['Book'],
                str(row['Chapter count']),
                str(row['Chapter min']),
                str(row['Chapter max']),
                str(row['Verses min']),
                str(row['Verses max']),
                f"{row['Verses mean']:.1f}"
            )
        
        console.print(table)
        console.print(f"[bold]Total books:[/bold] {len(grouped)}")
        
    except Exception as e:
        typer.secho(f"Error displaying limits: {e}", fg=typer.colors.RED)
def display_result(text: str, reference: str):
    """Display the verse/chapter with formatting"""
    typer.echo("\n" + "=" * 50)
    typer.secho(reference, fg=typer.colors.GREEN, bold=True)
    typer.echo("-" * 50)
    typer.secho(text, fg=typer.colors.CYAN)
    typer.echo("=" * 50 + "\n")

if __name__ == "__main__":
    app()