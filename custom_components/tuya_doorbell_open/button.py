import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from tuya_connector import TuyaOpenAPI

from .const import *

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(ACCESS_ID): cv.string,
    vol.Required(ACCESS_KEY): cv.string,
    vol.Required(DEVICE_ID): cv.string,
    vol.Optional(ICON, default="mdi:gesture-tap-button"): cv.string,
    vol.Optional(CONF_NAME, default="dorrbell"): cv.string,
})


async def async_setup_platform(
        hass,
        config,
        async_add_entities,
        discovery_info=None,
) -> None:
    button = TuyaDoorBellOpen(config.get(ACCESS_ID),
                              config.get(ACCESS_KEY),
                              config.get(DEVICE_ID),
                              name=config.get(CONF_NAME),
                              icon=config.get(ICON)
                              )

    async_add_entities([button], update_before_add=False)


class TuyaDoorBellOpen(ButtonEntity):
    def __init__(self, access_id, access_key, device_id, name='dorrbell', icon=None):
        self.access_id = access_id
        self.access_key = access_key
        self.device_id = device_id

        self._name = name
        self._icon = icon

        self.no_domain_ = self._name.startswith("!")
        if self.no_domain_:
            self._name = self.name[1:]

        self._unique_id = self._name.lower().replace(' ', '_')

        _LOGGER.debug(f'Init {self._unique_id}')

    @property
    def icon(self):
        """Icon of the entity."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
            "manufacturer": "tuya_doorbell_api",
        }
        return attrs

    @property
    def name(self):
        if self.no_domain_:
            return self._name
        else:
            return super().name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    def press(self) -> None:
        openapi = TuyaOpenAPI(API_ENDPOINT, self.access_id, self.access_key)
        openapi.connect()
        response = openapi.post(
            f"/v2.0/cloud/thing/{self.device_id}/shadow/properties/issue", {
                "properties": {
                    "accessory_lock": True
                }
            }
        )
        _LOGGER.debug(f'Press button {self._unique_id}')
