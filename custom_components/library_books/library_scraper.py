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
    
    @abstractmethod
    async def login(self) -> bool:
        """Login to the library system. Returns True if successful."""
        pass
    
    @abstractmethod
    async def get_outstanding_books(self, force_login: bool = True) -> List[LibraryBook]:
        """Retrieve list of outstanding books. Returns list of LibraryBook objects."""
        pass
    
    @abstractmethod
    async def renew_book(self, book: LibraryBook) -> bool:
        """Attempt to renew a book. Returns True if successful."""
        pass

    @abstractmethod
    async def logout(self) -> None:
        """Logout from the library system."""
        def close_session():
            if self.session:
                self.session.close()
        
        if self.session:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, close_session)
            self.session = None
    
    async def get_books_with_retry(self, max_retries: int = 3, force_login: bool = True) -> List[LibraryBook]:
        """Get outstanding books with retry logic."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                _LOGGER.debug(f"Fetching books, attempt {attempt + 1}/{max_retries}")
                books = await self.get_outstanding_books(force_login=force_login)
                _LOGGER.debug(f"Successfully fetched {len(books)} books")
                return books
                    
            except Exception as e:
                last_exception = e
                _LOGGER.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries failed
        if last_exception:
            _LOGGER.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
            raise last_exception
        else:
            # This shouldn't happen, but just in case
            error_msg = f"All {max_retries} attempts failed with no exception captured"
            _LOGGER.error(error_msg)
            raise Exception(error_msg)