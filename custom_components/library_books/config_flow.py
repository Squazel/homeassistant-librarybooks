"""Config flow for Library Books integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import slugify

from .const import DOMAIN, CONF_LIBRARY_TYPE, CONF_LIBRARY_URL, CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from .scrapers.libero_scraper import LiberoLibraryScraper

_LOGGER = logging.getLogger(__name__)

LIBRARY_TYPES = ["libero"]

class LibraryBooksConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Library Books."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Create unique ID using library name and username - properly slugified
            safe_library_name = slugify(user_input[CONF_NAME])
            safe_username = slugify(user_input[CONF_USERNAME])
            unique_id = f"{user_input[CONF_LIBRARY_TYPE]}_{safe_library_name}_{safe_username}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            
            try:
                # Validate the library credentials
                library_type = user_input[CONF_LIBRARY_TYPE]
                library_url = user_input[CONF_LIBRARY_URL]
                username = user_input[CONF_USERNAME]
                password = user_input[CONF_PASSWORD]
                name = user_input[CONF_NAME]
                
                if library_type == "libero":
                    scraper = LiberoLibraryScraper(library_url, username, password)
                else:
                    errors["base"] = "unsupported_library"
                    return self.async_show_form(
                        step_id="user", data_schema=self._get_schema(), errors=errors
                    )

                # Try to login
                login_successful = await scraper.login()
                if not login_successful:
                    errors["base"] = "invalid_auth"
                    return self.async_show_form(
                        step_id="user", data_schema=self._get_schema(user_input), errors=errors
                    )

                # Create the config entry
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
                
            except Exception:
                _LOGGER.exception("Unexpected exception during setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", 
            data_schema=self._get_schema(user_input), 
            errors=errors
        )
        
    def _get_schema(self, user_input=None):
        """Get schema with defaults from user_input if available."""
        if user_input is None:
            user_input = {}
            
        return vol.Schema({
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, "Library")): str,
            vol.Required(
                CONF_LIBRARY_TYPE, 
                default=user_input.get(CONF_LIBRARY_TYPE, "libero")
            ): vol.In(LIBRARY_TYPES),
            vol.Required(CONF_LIBRARY_URL, default=user_input.get(CONF_LIBRARY_URL, "")): str,
            vol.Required(CONF_USERNAME, default=user_input.get(CONF_USERNAME, "")): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
        })