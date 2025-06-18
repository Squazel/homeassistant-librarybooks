from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import logging
import asyncio

from .models import LibraryBook

_LOGGER = logging.getLogger(__name__)

class BaseLibraryScraper(ABC):
    """Base class for library website scrapers."""
    
    def __init__(self, library_url: str, username: str, password: str, session=None):
        """
        Initialize the scraper.
        
        Args:
            library_url: URL of the library website
            username: Library account username/card number
            password: Library account password/PIN
            session: Optional HTTP session
        """
        self.library_url = library_url
        self.username = username
        self.password = password
        self.session = session
        self._logged_in = False
    
    @abstractmethod
    async def login(self) -> bool:
        """Login to the library system. Returns True if successful."""
        pass
    
    @abstractmethod
    async def get_outstanding_books(self) -> List[LibraryBook]:
        """Retrieve list of outstanding books. Returns list of LibraryBook objects."""
        pass
    
    @abstractmethod
    async def renew_book(self, book: LibraryBook) -> bool:
        """Attempt to renew a book. Returns True if successful."""
        pass
    
    async def logout(self) -> None:
        """Logout from the library system."""
        self._logged_in = False
    
    @property
    def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        return self._logged_in
    
    async def get_books_with_retry(self, max_retries: int = 3) -> List[LibraryBook]:
        """Get outstanding books with retry logic."""
        for attempt in range(max_retries):
            try:
                if not self._logged_in:
                    await self.login()
                
                books = await self.get_outstanding_books()
                return books
            
            except Exception as e:
                _LOGGER.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return []