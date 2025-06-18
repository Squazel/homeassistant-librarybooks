"""Calendar platform for Library Books integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Library Books calendar."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    library_name = entry.data.get(CONF_NAME, "Library")
    
    async_add_entities([LibraryBooksCalendar(coordinator, entry.entry_id, library_name)], True)


class LibraryBooksCalendar(CalendarEntity):
    """Library Books Calendar."""

    def __init__(self, coordinator, entry_id, library_name):
        """Initialize the calendar."""
        self.coordinator = coordinator
        self._entry_id = entry_id
        self._library_name = library_name
        self._attr_unique_id = f"{entry_id}_calendar"
        self._attr_name = f"Library Books {library_name}"

    @property
    def event(self) -> Optional[CalendarEvent]:
        """Return the next upcoming event."""
        now = dt_util.now()
        events = self._get_events(now, now + timedelta(days=365))
        if not events:
            return None
        
        # Sort events by start time and return the first (soonest) one
        return sorted(events, key=lambda x: x.start)[0]

    async def async_get_events(
        self, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get all events in a specific time frame."""
        return self._get_events(start_date, end_date)
        
    def _get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get all events in a specific time frame."""
        events = []
        
        # Make sure data is up-to-date
        if hasattr(self.coordinator, "async_update"):
            self.coordinator.async_update()
        
        for book in self.coordinator.data:
            if not book.get("due_date"):
                continue
                
            # Parse the due date
            try:
                due_date = dt_util.parse_datetime(book["due_date"])
                if not due_date:
                    # Try parsing as date if datetime fails
                    due_date = dt_util.start_of_local_day(
                        dt_util.parse_date(book["due_date"])
                    )
                
                # Skip if no valid date or outside requested range
                if not due_date or due_date < start_date or due_date > end_date:
                    continue
                    
                # Create calendar event (all-day event)
                event = CalendarEvent(
                    summary=book.get("title", "Unknown Book"),
                    start=due_date.date(),
                    end=(due_date + timedelta(days=1)).date(),
                    description=f"Author: {book.get('author', 'Unknown')}\nDue date: {book['due_date']}",
                    all_day=True,
                )
                events.append(event)
            except (ValueError, TypeError) as err:
                _LOGGER.error("Error parsing date for book %s: %s", book.get("title"), err)
                
        return events

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "library_name": self._library_name,
        }