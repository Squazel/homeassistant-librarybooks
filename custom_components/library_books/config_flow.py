import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN, 
    CONF_LIBRARY_URL, 
    CONF_LIBRARY_TYPE, 
    CONF_UPDATE_INTERVAL, 
    CONF_CALENDAR_NAME,
    CONF_USE_SEPARATE_CALENDARS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_CALENDAR_NAME,
    LIBRARY_TYPES
)

class LibraryBooksConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Library Books."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate the input
            try:
                # Test connection here if needed
                return self.async_create_entry(
                    title=user_input[CONF_NAME], 
                    data=user_input
                )
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_LIBRARY_TYPE): vol.In(LIBRARY_TYPES),
            vol.Required(CONF_LIBRARY_URL): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
            vol.Optional(CONF_CALENDAR_NAME, default=DEFAULT_CALENDAR_NAME): str,
            vol.Optional(CONF_USE_SEPARATE_CALENDARS, default=True): bool,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )