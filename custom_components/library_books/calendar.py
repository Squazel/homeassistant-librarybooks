from datetime import datetime, timedelta
from typing import List, Optional
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .library_scraper import LibraryBook
from .coordinator import LibraryBooksCoordinator

_LOGGER = logging.getLogger(__name__)

class LibraryBooksCalendar(CalendarEntity):
    """Calendar entity for library books."""
    
    def __init__(self, hass: HomeAssistant, coordinator: LibraryBooksCoordinator, library_name: str):
        self.hass = hass
        self.coordinator = coordinator
        self._library_name = library_name
        self._attr_name = f"Library Books - {library_name}"
        self._attr_unique_id = f"library_books_calendar_{library_name.lower().replace(' ', '_')}"
    
    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._library_name)},
            name=f"Library Books - {self._library_name}",
            manufacturer="Library Books Integration",
        )
    
    @property
    def event(self) -> Optional[CalendarEvent]:
        """Return the next upcoming event."""
        events = self._get_calendar_events()
        if events:
            return min(events, key=lambda x: x.start)
        return None
    
    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events within the specified date range."""
        return [
            event for event in self._get_calendar_events()
            if start_date <= event.start <= end_date
        ]
    
    def _get_calendar_events(self) -> List[CalendarEvent]:
        """Convert library books to calendar events."""
        events = []
        books = self.coordinator.data.get(self._library_name, [])
        
        for book in books:
            # Create event for due date
            due_datetime = datetime.combine(book.due_date, datetime.min.time())
            
            event = CalendarEvent(
                start=due_datetime,
                end=due_datetime + timedelta(hours=1),  # 1-hour duration
                summary=f"📚 {book.title} due",
                description=f"Book: {book.title}\nAuthor: {book.author}\nDue: {book.due_date.strftime('%B %d, %Y')}",
                uid=f"library_book_{book.title}_{book.due_date}"
            )
            events.append(event)
        
        return events
    
    async def async_update(self) -> None:
        """Update the calendar."""
        await self.coordinator.async_request_refresh()