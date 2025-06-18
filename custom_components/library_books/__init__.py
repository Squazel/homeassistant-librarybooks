"""The Library Books integration."""
import logging

# Try importing Home Assistant components, but don't fail if they're not available
# This keeps your tests working while still supporting Home Assistant integration
try:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.const import Platform
    
    PLATFORMS = [Platform.CALENDAR, Platform.SENSOR]
    
    async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Set up Library Books from a config entry."""
        from .coordinator import LibraryBooksCoordinator
        from .scrapers.libero_scraper import LiberoLibraryScraper
        from .const import DOMAIN, CONF_LIBRARY_TYPE, CONF_LIBRARY_URL, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
        
        _LOGGER = logging.getLogger(__name__)
        
        # Get configuration
        library_type = entry.data[CONF_LIBRARY_TYPE]
        library_url = entry.data[CONF_LIBRARY_URL]
        username = entry.data[CONF_USERNAME]
        password = entry.data[CONF_PASSWORD]
        name = entry.data[CONF_NAME]
        
        # Create appropriate scraper
        if library_type == "libero":
            scraper = LiberoLibraryScraper(library_url, username, password)
        else:
            return False
        
        # Create coordinator and store in hass data
        coordinator = LibraryBooksCoordinator(
            hass,
            _LOGGER,
            library_api=library_api,
            name=f"Library Books {library_name}",
            update_interval=timedelta(hours=6),
        )
        
        # Update the coordinator's data for the first time
        await coordinator.async_config_entry_first_refresh()
        
        # Store the coordinator directly in hass.data
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = coordinator
        
        await hass.config_entries.async_forward_entry_setups(
            entry, ["sensor", "calendar"]
        )
        return True
    
    async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Unload a config entry."""
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
        if unload_ok:
            coordinator = hass.data[DOMAIN][entry.entry_id]
            await coordinator.scraper.logout()
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
        
except ImportError:
    # When running tests without Home Assistant installed, these functions won't be available
    # This prevents tests from breaking
    pass

# Constants that don't depend on Home Assistant
DOMAIN = "library_books"