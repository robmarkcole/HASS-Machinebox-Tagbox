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
CONF_SPECIAL_TAGS = 'special_tags'
TIMEOUT = 9

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_SPECIAL_TAGS, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
})


def encode_image(image):
    """base64 encode an image stream."""
    base64_img = base64.b64encode(image).decode('ascii')
    return base64_img


def format_tags(tags):
    """Return the formatted name and rounded confidence of tags."""
    return {entry['tag'].lower(): round(entry['confidence'], 2)
            for entry in tags}


def parse_tags(tags, api_tags):
    """Update the tags with the new data from the API."""
    tags.update(format_tags(api_tags['tags']))
    if api_tags['custom_tags']:
        tags.update(format_tags(api_tags['custom_tags']))
    try:
        state = max(tags.keys(), key=(lambda k: tags[k]))
    except:
        state = None
        _LOGGER.warning("%s found no tags in the image", CLASSIFIER)
    return tags, state


def post_image(url, image):
    """Post an image to the classifier."""
    try:
        response = requests.post(
            url,
            json={"base64": encode_image(image)},
            timeout=TIMEOUT
            )
        return response
    except requests.exceptions.ConnectionError:
        _LOGGER.error("ConnectionError: Is %s running?", CLASSIFIER)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(TagClassifyEntity(
            config[CONF_IP_ADDRESS],
            config[CONF_PORT],
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
            config[CONF_SPECIAL_TAGS],
        ))
    add_devices(entities)


class TagClassifyEntity(ImageProcessingEntity):
    """Perform a tag search via a Tagbox."""

    def __init__(self, ip, port, camera_entity, name, special_tags):
        """Init with the IP and PORT"""
        super().__init__()
        self._url_check = "http://{}:{}/{}/check".format(ip, port, CLASSIFIER)
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "{} {}".format(
                CLASSIFIER, camera_name)
        self._special_tags = {tag: 0.0 for tag in special_tags}
        self._tags = self._special_tags
        self._state = None

    def process_image(self, image):
        """Process an image."""
        response = post_image(self._url_check, image)
        if response is not None:
            response_json = response.json()
            if response_json['success']:
                self._tags, self._state = parse_tags(self._tags, response_json)
        else:
            self._state = None
            self._tags = self._special_tags

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
        return {
            'tags': self._tags,
            }
