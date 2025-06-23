"""Test configuration and fixtures."""
import pytest
import requests
from unittest.mock import Mock

@pytest.fixture
def mock_session():
    """Mock requests session for testing."""
    session = Mock(spec=requests.Session)
    return session

@pytest.fixture
def sample_library_book():
    """Sample library book for testing."""
    from datetime import date
    from custom_components.library_books.models import LibraryBook
    
    return LibraryBook(
        title="Test Book",
        author="Test Author",
        due_date=date(2025, 7, 1),
        isbn="1234567890",
        renewable=True
    )