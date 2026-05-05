import logging

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_DATA,
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
        self._url = url.rstrip("/")
        self.session = session
        self.token = token

    def __send(self, data):
        try:
            headers = {}

            if self.token is not None:
                headers["x-api-key"] = self.token

            _LOGGER.debug("Sending WAPI payload: %s", data)

            response = requests.post(
                f"{self._url}/{self.session}",
                json=data,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()
            _LOGGER.info("WAPI message sent successfully")

        except requests.exceptions.RequestException as ex:
            response_text = ""

            if getattr(ex, "response", None) is not None:
                response_text = ex.response.text

            _LOGGER.error(
                "Error sending notification using wapi: %s | response: %s",
                ex,
                response_text,
            )

    def send_message(self, message="", **kwargs):
        title = kwargs.get(ATTR_TITLE) or ""
        chat_id = kwargs.get(ATTR_TARGET)
        data = kwargs.get(ATTR_DATA) or {}

        if isinstance(chat_id, list):
            chat_id = chat_id[0] if chat_id else None

        if not chat_id:
            _LOGGER.error("No target/chatId provided for WAPI notification")
            return

        chat_id = str(chat_id).strip().replace(" ", "")

        media_urls = (
            data.get("media_url", "").splitlines()
            if data.get("media_url")
            else []
        )

        message = "" if message == " " else message
        ascaption = data.get("ascaption", False)

        def format_text(title, message):
            if title and message:
                return f"*{title}*\n{message}"
            if title:
                return f"*{title}*"
            return message or ""

        if ascaption and len(media_urls) > 1:
            _LOGGER.warning(
                "Multiple media URLs provided, but 'ascaption' is true. "
                "Only the first URL will have a caption."
            )

        if not media_urls:
            self.__send(
                {
                    "content": format_text(title, message),
                    "chatId": chat_id,
                    "contentType": "string",
                }
            )
            return

        if ascaption:
            self.__send(
                {
                    "chatId": chat_id,
                    "contentType": "MessageMediaFromURL",
                    "content": media_urls[0],
                    "options": {"caption": format_text(title, message)},
                }
            )
            media_urls = media_urls[1:]

        elif title or message:
            self.__send(
                {
                    "content": format_text(title, message),
                    "chatId": chat_id,
                    "contentType": "string",
                }
            )

        for url in media_urls:
            self.__send(
                {
                    "chatId": chat_id,
                    "contentType": "MessageMediaFromURL",
                    "content": url,
                }
            )
