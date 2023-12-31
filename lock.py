from homeassistant.components.lock import LockEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, APPLICATION_NAME
from pysesame3.auth import CognitoAuth
from pysesame3.chsesame2 import CHSesame2
from pysesame3.helper import CHProductModel, CHSesame2MechStatus
from typing import Any

CONF_API_KEY = "api_key"
CONF_UUID = "device_uuid"
CONF_CLIENT_SECRET = "client_secret"

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the lock."""
    api_key = entry.data.get(CONF_API_KEY)
    device_uuid = entry.data.get(CONF_UUID)
    secret_key = entry.data.get(CONF_CLIENT_SECRET)
    auth = CognitoAuth(apikey=api_key)
    lock = await hass.async_add_executor_job(lambda: SesameLock(CHSesame2(authenticator=auth, device_uuid=device_uuid, secret_key=secret_key)))

    async_add_entities([lock], True)

class SesameLock(LockEntity):
    def __init__(self, device):
        """Initialize the lock."""

        status = device.mechStatus
        self._device = device
     
        self._is_locked = status.isInLockRange()
        self._battery_level = int(str(status.getBatteryPercentage()).strip('%'))

        self._device_id = device.deviceId
        self._device_model = device.productModel
        self._battery_voltage = status.getBatteryVoltage(),
        self._position = status.getPosition()
        self._is_in_lock_range = status.isInLockRange()
        self._is_in_unlock_range = status.isInUnlockRange()

        self._device.subscribeMechStatus(self._update_callback)

    @property
    def name(self):
        """Return the name of the lock."""
        return self._device.deviceId

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device.deviceId

    @property
    def is_locked(self):
        """Return True if the lock is locked."""
        return self._is_locked

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attrs = super().device_state_attributes or {}
        attrs[ATTR_BATTERY_LEVEL] = self._battery_level
        return attrs
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        return {
            ATTR_BATTERY_LEVEL: self._battery_level,
            'device_uuid': self._device_id,
            'device_model': self._device_model,
            'battery_voltage': self._battery_voltage,
            'position': self._position,
            'is_in_lock_range': self._is_in_lock_range,
            '_is_in_unlock_range': self._is_in_unlock_range,
        }
    
    async def async_lock(self, **kwargs):
        """Lock the device."""
        await self.hass.async_add_executor_job(self._device.lock, APPLICATION_NAME)
        self._is_locked = True
        self.async_schedule_update_ha_state()

    async def async_unlock(self, **kwargs):
        """Unlock the device."""
        await self.hass.async_add_executor_job(self._device.unlock, APPLICATION_NAME)
        self._is_locked = False
        self.async_schedule_update_ha_state()

    def _update_callback(self, device: CHSesame2, status: CHSesame2MechStatus):
        """Handle device updates."""
        self._is_locked = status.isInLockRange()
        self._battery_level = int(str(status.getBatteryPercentage()).strip('%'))

        self._device_id = device.deviceId
        self._device_model = device.productModel
        self._battery_voltage = status.getBatteryVoltage(),
        self._position = status.getPosition()
        self._is_in_lock_range = status.isInLockRange()
        self._is_in_unlock_range = status.isInUnlockRange()

        self.async_schedule_update_ha_state()
