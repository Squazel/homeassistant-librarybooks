"""Sensor platform for library books integration."""
import logging
from typing import Any, Dict, List, Optional, cast

from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LibraryBooksCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the library books sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    library_name = entry.data.get("name", "Library")
    
    entities = [
        LibraryBooksTotalSensor(coordinator, library_name),
        LibraryBooksOverdueSensor(coordinator, library_name),
    ]
    
    async_add_entities(entities)

class LibraryBooksTotalSensor(CoordinatorEntity, SensorEntity):
    """Sensor tracking total number of library books."""

    def __init__(self, coordinator: LibraryBooksCoordinator, library_name: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.library_name = library_name
        
        self._attr_unique_id = f"{DOMAIN}_{library_name.lower().replace(' ', '_')}_total_books"
        self._attr_name = f"{library_name} Total Books"
        self._attr_icon = "mdi:book-multiple"
        self._attr_device_class = "library_books"
        self._attr_native_unit_of_measurement = "books"
        
    @property
    def native_value(self) -> int:
        """Return the total number of books."""
        if not self.coordinator.data:
            return 0
        
        return len(self.coordinator.data)
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes about the books."""
        if not self.coordinator.data:
            return {}
            
        return {
            "books": [
                {
                    "title": book.title,
                    "author": book.author,
                    "due_date": book.due_date.isoformat(),
                    "is_overdue": book.is_overdue,
                    "days_until_due": book.days_until_due,
                }
                for book in self.coordinator.data
            ]
        }

class LibraryBooksOverdueSensor(CoordinatorEntity, SensorEntity):
    """Sensor tracking number of overdue books."""

    def __init__(self, coordinator: LibraryBooksCoordinator, library_name: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.library_name = library_name
        
        self._attr_unique_id = f"{DOMAIN}_{library_name.lower().replace(' ', '_')}_overdue_books"
        self._attr_name = f"{library_name} Overdue Books"
        self._attr_icon = "mdi:book-alert"
        self._attr_device_class = "library_books"
        self._attr_native_unit_of_measurement = "books"
        
    @property
    def native_value(self) -> int:
        """Return the number of overdue books."""
        if not self.coordinator.data:
            return 0
        
        return sum(1 for book in self.coordinator.data if book.is_overdue)
        
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes about overdue books."""
        if not self.coordinator.data:
            return {}
            
        return {
            "overdue_books": [
                {
                    "title": book.title,
                    "author": book.author,
                    "due_date": book.due_date.isoformat(),
                    "days_overdue": abs(book.days_until_due),
                }
                for book in self.coordinator.data if book.is_overdue
            ]
        }