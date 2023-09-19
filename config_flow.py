import logging
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class SesameLockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # TODO: validate auth with api
            return self.async_create_entry(title="SesameLock", data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(self._data_schema_with_defaults()),  
            errors=errors,
        )

    @staticmethod
    def _data_schema_with_defaults():
        """Return schema with defaults."""
        return {
            vol.Required("api_key", default="api_key"): str,
            vol.Required("device_uuid", default="device_uuid"): str,
            vol.Required("client_secret", default="client_secret"): str,
        }