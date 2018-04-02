"""
Component that will search images for tagged objects via a local
machinebox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.tagbox
"""
import base64
import requests
import logging
import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME)

_LOGGER = logging.getLogger(__name__)

CONF_ENDPOINT = 'endpoint'
ROUNDING_DECIMALS = 3

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENDPOINT): cv.string
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(Tagbox(
            camera.get(CONF_NAME),
            config[CONF_ENDPOINT],
            camera[CONF_ENTITY_ID],
        ))
    add_devices(entities)


class Tagbox(ImageProcessingEntity):
    """Perform a tag search via a Tagbox."""

    def __init__(self, name, endpoint, camera_entity):
        """Init with the API key and model id"""
        super().__init__()
        if name:  # Since name is optional.
            self._name = name
        else:
            self._name = "Tagbox {0}".format(
                split_entity_id(camera_entity)[1])
        self._camera = camera_entity
        self._url = "http://{}/tagbox/check".format(endpoint)
        self._state = None
        self._attributes = {}

    def process_image(self, image):
        """Process an image."""
        response = requests.post(
            self._url,
            json=self.encode_image(image)
            ).json()

        if response['success']:
            tags = {
                tag['tag']: round(tag['confidence'], ROUNDING_DECIMALS)
                for tag in response['tags']
                }
            if response['custom_tags']:
                custom_tags = {
                    tag['tag']: round(tag['confidence'], ROUNDING_DECIMALS)
                    for tag in response['custom_tags']}
                tags.update(custom_tags)
            self._attributes = tags
            self._state = max(tags.keys(), key=(lambda k: tags[k]))
        else:
            self._state = "Request_failed"
            self._attributes = {}

    def encode_image(self, image):
        """base64 encode an image stream."""
        base64_img = base64.b64encode(image).decode('ascii')
        return {"base64": base64_img}

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        return self._attributes

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
