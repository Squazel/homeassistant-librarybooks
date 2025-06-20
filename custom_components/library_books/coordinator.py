"""Data coordinator for library books integration."""
from datetime import timedelta
import logging
from typing import Dict, List, Any, Optional
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import Entity

from .library_scraper import BaseLibraryScraper
from .models import LibraryBook

_LOGGER = logging.getLogger(__name__)

class LibraryBooksCoordinator(DataUpdateCoordinator):
    """Class to manage fetching library books data."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        scraper: BaseLibraryScraper, 
        name: str, 
        update_interval: timedelta = timedelta(hours=6)
    ):
        """Initialize."""
        self.scraper = scraper
        self.library_name = name
        self.books: List[LibraryBook] = []
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"Library Books {name}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> List[LibraryBook]:
        """Fetch data from API."""
        try:
            books = await self.scraper.get_books_with_retry(max_retries=2, force_login=True)
            
            # Add library name to books for multi-library setups
            for book in books:
                book.library_name = self.library_name
                
            return books
            
        except Exception as ex:
            _LOGGER.warning(f"Failed to fetch library books: {ex}")
            # Raise UpdateFailed but keep entities available with last known state
            raise UpdateFailed(f"Error fetching library books: {ex}")
    
    # Renewal functionality is disabled for now
    # async def renew_book(self, book: LibraryBook) -> bool:
    #    """Renew a library book."""
    #    _LOGGER.warning("Book renewal functionality is not yet implemented")
    #    return False