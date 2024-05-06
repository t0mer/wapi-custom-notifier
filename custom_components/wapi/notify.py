import logging
import re

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_TARGET,
    ATTR_TITLE,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)

CONF_URL = "url"
CONFIG_SESSION = "session"
CONFIG_TOKEN = "token"
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONFIG_SESSION): cv.string,
        vol.Optional(CONFIG_TOKEN): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)


def get_service(hass, config, discovery_info=None):
    """Get the custom notifier service."""
    url = config.get(CONF_URL)
    session = config.get(CONFIG_SESSION)
    token = config.get(CONFIG_TOKEN)
    return MatterNotificationService(url, session, token)


class MatterNotificationService(BaseNotificationService):
    def __init__(self, url, session, token=None):
        self._url = url
        self.session = session
        self.token = token

    def __send(self, data):
        try:
            if self.token is None:
                response = requests.post(self._url + "/" + self.session, json=data)
            else:
                headers = {"x-api-key": self.token}
                response = requests.post(
                    self._url + "/" + self.session, json=data, headers=headers
                )
            _LOGGER.info("Message sent")
            response.raise_for_status()
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error sending notification using wapi: %s", ex)

    def send_message(self, message="", **kwargs):
        title = kwargs.get(ATTR_TITLE)
        chatId = kwargs.get(ATTR_TARGET)

        found_url = None
        url_matches = re.search("(?P<url>https?://[^\s]+)", message)
        if url_matches:
            found_url = url_matches.group("url")

        data = {
            "content": "*" + title + "* \n" + message,
            "chatId": chatId,
            "contentType": "string",
        }
        self.send(data)

        if found_url:
            media_data = {
                "content": found_url,
                "chatId": chatId,
                "contentType": "MessageMediaFromURL"
            }
            self.send(media_data)






