"""
Search images for tagged objects via a local Tagbox instance.

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
from homeassistant.const import (CONF_IP_ADDRESS, CONF_PORT)

_LOGGER = logging.getLogger(__name__)

CLASSIFIER = 'tagbox'
CONF_TAGS = 'tags'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_TAGS, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
})


def encode_image(image):
    """base64 encode an image stream."""
    base64_img = base64.b64encode(image).decode('ascii')
    return {"base64": base64_img}


def process_tags(tags_data):
    """Process tags data, returning the tag and rounded confidence."""
    processed_tags = {
        tag['tag'].lower(): round(tag['confidence'], 2)
        for tag in tags_data
        }
    return processed_tags


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(TagClassifyEntity(
            config[CONF_IP_ADDRESS],
            config[CONF_PORT],
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
            config[CONF_TAGS],
        ))
    add_devices(entities)


class TagClassifyEntity(ImageProcessingEntity):
    """Perform a tag search via a Tagbox."""

    def __init__(self, ip, port, camera_entity, name, tags):
        """Init with the IP and PORT"""
        super().__init__()
        self._url = "http://{}:{}/{}/check".format(ip, port, CLASSIFIER)
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format(
                CLASSIFIER, camera_name)
        self._default_tags = {tag: 0.0 for tag in tags}
        self._tags = self._default_tags
        self._state = None

    def process_image(self, image):
        """Process an image."""
        response = {}
        try:
            response = requests.post(
                self._url,
                json=encode_image(image),
                timeout=9
                ).json()
        except requests.exceptions.ConnectionError:
            _LOGGER.error("ConnectionError: Is %s running?", CLASSIFIER)
            response['success'] = False

        if response['success']:
            self._tags, self._state = self.process_response(response)
        else:
            self._state = "Request_failed"
            self._tags = self._default_tags

    def process_response(self, response):
        """Process response data, returning the processed tags and state."""
        tags = self._default_tags.copy()
        tags.update(process_tags(response['tags']))

        if response['custom_tags']:
            tags.update(process_tags(response['custom_tags']))
        # Default tags have probability 0.0 and cause an exception.
        try:
            state = max(tags.keys(), key=(lambda k: tags[k]))
        except:
            state = "no_tags_identified"
        return tags, state

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return other details about the sensor state."""
        attr = self._tags.copy()
        return attr
