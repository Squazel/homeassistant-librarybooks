"""Library Books integration for Home Assistant."""

# Only import Home Assistant modules when actually running in HA
try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.const import CONF_NAME
    
    from .const import (
        DOMAIN,
        CONF_LIBRARY_TYPE,
        CONF_LIBRARY_URL,
        CONF_USERNAME,
        CONF_PASSWORD,
        CONF_UPDATE_INTERVAL,
    )
    from .coordinator import LibraryBooksCoordinator
    
    HOMEASSISTANT_AVAILABLE = True
except ImportError:
    # Running in test environment without Home Assistant
    HOMEASSISTANT_AVAILABLE = False

# Only define HA functions if HA is available
if HOMEASSISTANT_AVAILABLE:
    async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Set up Library Books from a config entry."""
        
        # Each config entry gets its own coordinator/scraper instance
        coordinator = LibraryBooksCoordinator(
            hass=hass,
            name=entry.data[CONF_NAME],
            library_type=entry.data[CONF_LIBRARY_TYPE],
            library_url=entry.data[CONF_LIBRARY_URL],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            update_interval=entry.data[CONF_UPDATE_INTERVAL],
        )
        
        # Store coordinator with unique key
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
        
        # Create calendar entity with library name
        await hass.config_entries.async_forward_entry_setups(entry, ["calendar"])
        
        return True

    async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """Unload a config entry."""
        unload_ok = await hass.config_entries.async_unload_platforms(entry, ["calendar"])
        if unload_ok:
            coordinator = hass.data[DOMAIN].pop(entry.entry_id)
            await coordinator.async_shutdown()
        
        return unload_ok