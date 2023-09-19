"""The sesame lock component."""
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up this integration using yaml."""
    # This function is called if the integration is set up using YAML.
    # It's only here for backwards compatibility.
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SesameLock from a config entry."""
    # Forward to the lock platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "lock")
    )
    return True
