# helpers.py
import httpx
import random as random_module
import pandas as pd
import re
from typing import Dict, Tuple
from constants import OLD_TESTAMENT_BOOKS, NEW_TESTAMENT_BOOKS, API_BASE, VERSIONS_URL
from models import Testament

# Load CSV data
OLD_TESTAMENT_LIMITS = pd.read_csv('old_testament_limits.csv')
NEW_TESTAMENT_LIMITS = pd.read_csv('new_testament_limits.csv')
BIBLE_LIMITS = pd.concat([OLD_TESTAMENT_LIMITS, NEW_TESTAMENT_LIMITS])

# Standardize book names in the DataFrame
BIBLE_LIMITS['Book'] = BIBLE_LIMITS['Book'].str.strip().str.title()

def format_book_name_for_api(book_name: str) -> str:
    """Convert display book names (e.g., '1 Corinthians') to API format (e.g., '1corinthians')"""
    # Remove spaces and punctuation, convert to lowercase
    return re.sub(r'[\s\'-]', '', book_name).lower()

def format_book_name_for_display(api_name: str) -> str:
    """Convert API book names (e.g., '1corinthians') to display format (e.g., '1 Corinthians')"""
    # Insert space after numbers and capitalize first letters
    formatted = re.sub(r'(\d)([a-z])', r'\1 \2', api_name)
    return formatted.title()

def get_all_books():
    """Combine books from both testaments"""
    return OLD_TESTAMENT_BOOKS + NEW_TESTAMENT_BOOKS

def get_random_book(testament: Testament = Testament.ALL):
    """Get a random book based on testament filter"""
    if testament == Testament.OLD:
        return random_module.choice(OLD_TESTAMENT_BOOKS)
    elif testament == Testament.NEW:
        return random_module.choice(NEW_TESTAMENT_BOOKS)
    return random_module.choice(get_all_books())

def get_random_chapter_verse(book: str) -> Tuple[int, int]:
    """Get random chapter and verse within valid limits for the book"""
    # Convert API-style name to display format for CSV lookup
    display_name = format_book_name_for_display(book)
    book_df = BIBLE_LIMITS[BIBLE_LIMITS['Book'].str.lower() == display_name.lower()]
    
    if not book_df.empty:
        chapter_row = book_df.sample(1).iloc[0]
        return chapter_row['Chapter'], random_module.randint(1, chapter_row['Verses'])
    else:
        raise ValueError(f"Book {book} not found in limits CSV")

def fetch_versions():
    """Fetch available Bible versions"""
    response = httpx.get(VERSIONS_URL)
    response.raise_for_status()
    return response.json()

def fetch_verse(version: str, book: str, chapter: int, verse: int):
    """Fetch a specific verse from the API"""
    api_book_name = format_book_name_for_api(book)
    url = f"{API_BASE}/{version}/books/{api_book_name}/chapters/{chapter}/verses/{verse}.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

def fetch_chapter(version: str, book: str, chapter: int):
    """Fetch an entire chapter from the API"""
    api_book_name = format_book_name_for_api(book)
    url = f"{API_BASE}/{version}/books/{api_book_name}/chapters/{chapter}.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

def get_bible_limits() -> pd.DataFrame:
    """Get the complete Bible limits DataFrame"""
    return BIBLE_LIMITS