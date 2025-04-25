import httpx
import random as random_module
from constants import OLD_TESTAMENT_BOOKS, NEW_TESTAMENT_BOOKS, API_BASE, VERSIONS_URL
from models import Testament


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

def fetch_versions():
    """Fetch available Bible versions"""
    response = httpx.get(VERSIONS_URL)
    response.raise_for_status()
    return response.json()

def fetch_verse(version: str, book: str, chapter: int, verse: int):
    """Fetch a specific verse from the API"""
    url = f"{API_BASE}/{version}/books/{book}/chapters/{chapter}/verses/{verse}.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()

def fetch_chapter(version: str, book: str, chapter: int):
    """Fetch an entire chapter from the API"""
    url = f"{API_BASE}/{version}/books/{book}/chapters/{chapter}.json"
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()
