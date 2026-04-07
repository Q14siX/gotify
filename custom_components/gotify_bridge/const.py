"""Constants for the Gotify Bridge integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "gotify_bridge"

PLATFORMS = ["notify", "sensor", "binary_sensor", "event"]

CONF_MODE = "mode"
CONF_APP_TOKEN = "app_token"
CONF_CLIENT_TOKEN = "client_token"
CONF_ENABLE_WEBSOCKET = "enable_websocket"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MONITORED_APPLICATION_ID = "monitored_application_id"
CONF_MONITORED_APPLICATION_NAME = "monitored_application_name"

MODE_SEND_ONLY = "send_only"
MODE_RECEIVE_ONLY = "receive_only"
MODE_FULL = "full"

DEFAULT_NAME = "Gotify"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_ENABLE_WEBSOCKET = True
DEFAULT_VERIFY_SSL = True

SERVICE_SEND_MESSAGE = "send_message"
SERVICE_CLEAR_MESSAGES = "clear_messages"
SERVICE_DELETE_MESSAGE = "delete_message"
SERVICE_REFRESH = "refresh"

ATTR_ENTRY_ID = "entry_id"
ATTR_MESSAGE_ID = "message_id"
ATTR_MESSAGE = "message"
ATTR_TITLE = "title"
ATTR_PRIORITY = "priority"
ATTR_MARKDOWN = "markdown"
ATTR_CLICK_URL = "click_url"
ATTR_BIG_IMAGE_URL = "big_image_url"
ATTR_INTENT_URL = "intent_url"
ATTR_EXTRAS = "extras"

DEFAULT_PRIORITY = 5
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 3600

DEFAULT_UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

EVENT_MESSAGE_RECEIVED = f"{DOMAIN}_message_received"

DATA_ENTRIES = "entries"

CONF_VERIFY_SSL = "verify_ssl"
CONF_URL = "url"
CONF_NAME = "name"

MASKED = "**REDACTED**"
