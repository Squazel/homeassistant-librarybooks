"""Test configuration and fixtures."""
import pytest
import aiohttp
from unittest.mock import AsyncMock

@pytest.fixture
async def mock_session():
    """Mock aiohttp session for testing."""
    session = AsyncMock(spec=aiohttp.ClientSession)
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