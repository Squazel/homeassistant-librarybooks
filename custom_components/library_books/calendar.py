"""Calendar platform for library books integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import LibraryBooksCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Library Books calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    library_name = entry.data[CONF_NAME]
    username = entry.data[CONF_USERNAME]
    
    # Create calendar for this library
    calendar = LibraryBooksCalendar(coordinator, entry.entry_id, library_name, username)
    async_add_entities([calendar], True)

class LibraryBooksCalendar(CalendarEntity):
    """Library Books Calendar class."""

    def __init__(self, coordinator, entry_id, library_name, username):
        """Initialize the Library Books calendar."""
        self.coordinator = coordinator
        self._entry_id = entry_id
        self._library_name = library_name
        self._username = username
        
        # Set display name to just the library name from config
        self._name = library_name
        
        # Generate entity ID using both library name and username - properly slugified
        safe_library_name = slugify(library_name)
        safe_username = slugify(username)
        
        # Unique ID should match the entity ID pattern but include entry_id for complete uniqueness
        self._attr_unique_id = f"{DOMAIN}_calendar_{safe_library_name}_{safe_username}_{entry_id}"
        
        # Create entity ID matching the pattern: calendar.library_books_libraryname_username
        self.entity_id = f"calendar.library_books_{safe_library_name}_{safe_username}"
    
    @property
    def name(self):
        """Return the name of the entity."""
        return self._name