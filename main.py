import random
import typer
from typing import Optional
from enum import Enum

app = typer.Typer(help="Bible Verse Finder")

class Testament(str, Enum):
    old = "old"
    new = "new"
    all = "all"

# Sample Bible database (in a real app, use a proper database or API)
BIBLE_VERSES = {
    "old": {
        "genesis": [
            "In the beginning God created the heavens and the earth. (Gen 1:1)",
            "Let there be light. (Gen 1:3)"
        ],
        "psalms": [
            "The LORD is my shepherd, I lack nothing. (Ps 23:1)",
            "Create in me a pure heart, O God. (Ps 51:10)"
        ]
    },
    "new": {
        "john": [
            "For God so loved the world... (John 3:16)",
            "I am the way, the truth, and the life. (John 14:6)"
        ],
        "romans": [
            "All have sinned and fall short... (Rom 3:23)",
            "The wages of sin is death... (Rom 6:23)"
        ]
    }
}

def get_all_books():
    """Combine books from both testaments"""
    return list(BIBLE_VERSES["old"].keys()) + list(BIBLE_VERSES["new"].keys())

@app.command()
def verse(
    random: bool = typer.Option(False, "--random", "-r", help="Get random verse"),
    testament: Optional[Testament] = typer.Option(None, "--testament", "-t", help="Filter by testament"),
    book: Optional[str] = typer.Option(None, "--book", "-b", help="Filter by book name", autocompletion=get_all_books)
):
    """
    Get Bible verses with various filters
    """
    if random:
        get_random_verse(testament, book)
    else:
        get_verse(testament, book)

def get_random_verse(testament: Optional[Testament] = None, book: Optional[str] = None):
    """Display a random verse based on filters"""
    filtered_verses = []
    
    # Determine which testaments to include
    testaments_to_search = []
    if testament == Testament.old or testament is None:
        testaments_to_search.append("old")
    if testament == Testament.new or testament is None:
        testaments_to_search.append("new")
    
    # Collect verses based on filters
    for testament_key in testaments_to_search:
        for book_name, verses in BIBLE_VERSES[testament_key].items():
            if book and book_name.lower() != book.lower():
                continue
            filtered_verses.extend(verses)
    
    if not filtered_verses:
        typer.secho("No verses found matching your criteria", fg=typer.colors.RED)
        raise typer.Exit()
    
    chosen_verse = random.choice(filtered_verses)
    display_verse(chosen_verse)

def get_verse(testament: Optional[Testament] = None, book: Optional[str] = None):
    """Display verses based on filters (non-random)"""
    # Implementation would be similar but show all matching verses
    # For brevity, we'll just show sample verses
    sample_verses = [
        "Sample verse 1",
        "Sample verse 2"
    ]
    for verse in sample_verses:
        display_verse(verse)

def display_verse(verse_text: str):
    """Display a verse with beautiful formatting"""
    typer.echo("\n" + "=" * 50)
    typer.secho(verse_text, fg=typer.colors.BLUE, bold=True)
    typer.echo("=" * 50 + "\n")

if __name__ == "__main__":
    app()