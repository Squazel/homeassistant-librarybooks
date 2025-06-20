"""Calendar platform for Library Books integration."""
from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .models import LibraryBook
from .const import DOMAIN, CONF_NAME
from .coordinator import LibraryBooksCoordinator

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
    """A calendar for library books."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, library_name):
        """Initialize the calendar."""
        self.coordinator = coordinator
        self._entry_id = entry_id
        self._library_name = library_name
        self._attr_name = library_name
        self._attr_unique_id = f"{entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        now = dt_util.now()
        events = self._get_events(now, now + timedelta(days=365))
        return events[0] if events else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return self._get_events(start_date, end_date)

    def _get_events(self, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        events = []
        books: list[LibraryBook] = self.coordinator.data or []

        for book in books:
            if not book.due_date:
                continue

            due_date = book.due_date

            if start_date.date() <= due_date < end_date.date():
                event = CalendarEvent(
                    start=due_date,
                    end=due_date + timedelta(days=1),
                    summary=book.title or "Unknown Title",
                    description=f"Author: {book.author or 'N/A'}\nOverdue: {'Yes' if book.is_overdue else 'No'}",
                    uid=book.barcode,
                )
                events.append(event)
        
        events.sort(key=lambda e: e.start)
        return events

    @property
    def name(self) -> str:
        """Return the name of the calendar."""
        return self._attr_name

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "library_name": self._library_name,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Calendar is available even if the last update failed, as long as we have previous data
        return self.coordinator.last_update_success or (
            hasattr(self.coordinator, 'data') and self.coordinator.data is not None
        )