import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from tuya_connector import (
    TuyaOpenAPI,
)

DOMAIN = 'tuya_doorbell_open'

API_ENDPOINT = "https://openapi.tuyaeu.com"

ACCESS_ID = "ACCESS_ID"
ACCESS_KEY = "ACCESS_KEY"

DEVICE_ID = "button"
ICON = 'icon'

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(ACCESS_ID): cv.string,
    vol.Required(ACCESS_KEY): cv.string,
    vol.Optional(ICON): cv.string,
})


async def async_setup_platform(
        hass,
        config,
        async_add_entities,
        discovery_info=None,
) -> None:
    button = TuyaDoorBellOpen(config.get(ACCESS_ID),
                              config.get(ACCESS_KEY),
                              config.get(DEVICE_ID)
                              )

    async_add_entities([button], update_before_add=False)


class TuyaDoorBellOpen(ButtonEntity):
    def __init__(self, access_id, access_key, device_id):
        self.access_id = access_id
        self.access_key = access_key
        self.device_id = device_id

        self._unique_id = self._name.lower().replace(' ', '_')

        self.openapi = TuyaOpenAPI(API_ENDPOINT, self.access_id, self.access_key)
        self.openapi.connect()

        _LOGGER.debug(f'Start button {self._unique_id}')

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attrs = {
            'friendly_name': self._name,
            'unique_id': self._unique_id,
            "manufacturer": "tuya_api",
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
        response = self.openapi.post(
            f"/v2.0/cloud/thing/{self.device_id}/shadow/properties/issue", {
                "properties": {
                    "accessory_lock": True
                }
            }
        )
