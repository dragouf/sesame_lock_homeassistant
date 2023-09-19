"""Support for Sesame lock, by CANDY HOUSE."""
from __future__ import annotations

from typing import Any

from pysesame3.auth import WebAPIAuth
from pysesame3.chsesame2 import CHSesame2  # For SESAME 3, 4, 5
from pysesame3.helper import CHProductModel

import voluptuous as vol

from homeassistant.components.lock import PLATFORM_SCHEMA, LockEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_DEVICE_ID, CONF_API_KEY, CONF_UUID, CONF_CLIENT_SECRET, APPLICATION_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

ATTR_SERIAL_NO = "serial"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string, 
    vol.Required(CONF_UUID): cv.string, 
    vol.Required(CONF_CLIENT_SECRET): cv.string,
    })


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Sesame Lock platform."""
    api_key = config.get(CONF_API_KEY)
    device_uuid = config.get(CONF_UUID)
    secret_key = config.get(CONF_CLIENT_SECRET)

    auth = WebAPIAuth(apikey=api_key)

    add_entities(
        [SesameLockDevice(CHSesame2(
        authenticator=auth, device_uuid=device_uuid, secret_key=secret_key
    ))],
        update_before_add=True,
    )


class SesameLockDevice(LockEntity):
    """Representation of a Sesame device."""

    def __init__(self, sesame: CHSesame2) -> None:
        """Initialize the Sesame device."""
        self._sesame: CHSesame2 = sesame

        # Cached properties from pysesame object.
        self._device_id: str | None = None
        self._serial = None
        self._nickname: str | None = None
        self._is_locked = False
        self._responsive = True
        self._battery = -1

    @property
    def name(self) -> str | None:
        """Return the name of the device."""
        return self._nickname

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._responsive

    @property
    def is_locked(self) -> bool:
        """Return True if the device is currently locked, else False."""
        return self._is_locked

    def lock(self, **kwargs: Any) -> None:
        """Lock the device."""
        self._sesame.lock(APPLICATION_NAME)

    def unlock(self, **kwargs: Any) -> None:
        """Unlock the device."""
        self._sesame.unlock(APPLICATION_NAME)

    def update(self) -> None:
        """Update the internal state of the device."""
        status = self._sesame.mechStatus
        self._nickname = self._sesame.productModel.deviceModel()
        self._device_id = str(self._sesame.getDeviceUUID())
        self._serial = self._sesame.productModel.deviceModel()
        self._battery = status.getBatteryPercentage()
        self._is_locked = status.isInLockRange()
        self._responsive = True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_DEVICE_ID: self._device_id,
            ATTR_SERIAL_NO: self._serial,
            ATTR_BATTERY_LEVEL: self._battery,
        }
