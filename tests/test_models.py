"""Test the data models."""
import pytest
import sys
from pathlib import Path
from datetime import date, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly from the models module to avoid __init__.py
from custom_components.library_books.models import LibraryBook

def test_library_book_creation():
    """Test creating a LibraryBook."""
    book = LibraryBook(
        title="Test Book",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.due_date == date(2025, 7, 1)
    assert book.renewable is True  # Default value

def test_library_book_overdue():
    """Test overdue detection."""
    # Overdue book
    overdue_book = LibraryBook(
        title="Overdue Book",
        author="Author",
        due_date=date.today() - timedelta(days=1)
    )
    assert overdue_book.is_overdue is True
    
    # Not overdue book
    future_book = LibraryBook(
        title="Future Book", 
        author="Author",
        due_date=date.today() + timedelta(days=7)
    )
    assert future_book.is_overdue is False

def test_days_until_due():
    """Test days until due calculation."""
    book = LibraryBook(
        title="Test Book",
        author="Author", 
        due_date=date.today() + timedelta(days=5)
    )
    assert book.days_until_due == 5

def test_library_book_str():
    """Test string representation."""
    book = LibraryBook(
        title="Test Book",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    expected = "Test Book by Test Author (Due: 2025-07-01)"
    assert str(book) == expected

def test_title_cleaning_trailing_slash():
    """Test that trailing slashes are removed from titles."""
    book = LibraryBook(
        title="Test Book /",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test Book"

def test_title_cleaning_multiple_trailing_slashes():
    """Test that multiple trailing slashes are removed from titles."""
    book = LibraryBook(
        title="Test Book ///",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test Book"

def test_title_cleaning_trailing_whitespace_and_slashes():
    """Test that trailing whitespace and slashes are removed from titles."""
    book = LibraryBook(
        title="Test Book  / /  ",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test Book"

def test_title_cleaning_preserves_internal_slashes():
    """Test that internal slashes are preserved in titles."""
    book = LibraryBook(
        title="Test/Book with/internal slashes",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test/Book with/internal slashes"

def test_title_cleaning_preserves_internal_slashes_removes_trailing():
    """Test that internal slashes are preserved but trailing ones are removed."""
    book = LibraryBook(
        title="Test/Book with/internal slashes / ",
        author="Test Author",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test/Book with/internal slashes"

def test_author_cleaning_trailing_slash():
    """Test that trailing slashes are removed from authors."""
    book = LibraryBook(
        title="Test Book",
        author="Test Author /",
        due_date=date(2025, 7, 1)
    )
    assert book.author == "Test Author"

def test_author_cleaning_multiple_trailing_slashes():
    """Test that multiple trailing slashes are removed from authors."""
    book = LibraryBook(
        title="Test Book",
        author="Test Author ///",
        due_date=date(2025, 7, 1)
    )
    assert book.author == "Test Author"

def test_author_cleaning_trailing_whitespace_and_slashes():
    """Test that trailing whitespace and slashes are removed from authors."""
    book = LibraryBook(
        title="Test Book",
        author="Test Author  / /  ",
        due_date=date(2025, 7, 1)
    )
    assert book.author == "Test Author"

def test_title_and_author_cleaning_both():
    """Test that both title and author are cleaned simultaneously."""
    book = LibraryBook(
        title="Test Book / ",
        author="Test Author  / ",
        due_date=date(2025, 7, 1)
    )
    assert book.title == "Test Book"
    assert book.author == "Test Author"

def test_empty_title_and_author_handling():
    """Test that empty or None values don't cause errors."""
    book = LibraryBook(
        title="",
        author="",
        due_date=date(2025, 7, 1)
    )
    assert book.title == ""
    assert book.author == ""

def test_leading_whitespace_removed():
    """Test that leading whitespace is removed by strip() and trailing slashes (and additional whitespace) are removed by regex."""
    book = LibraryBook(
        title="  Test Book / ",
        author="  Test Author / ",
        due_date=date(2025, 7, 1)
    )
    # .strip() removes leading/trailing whitespace, then regex removes trailing slashes (and additional whitespace)
    assert book.title == "Test Book"
    assert book.author == "Test Author"