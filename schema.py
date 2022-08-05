import voluptuous as vol
from voluptuous import Any

DEFAULT_DISCOVERY = False
DEFAULT_DISCOVERY_PREFIX = "homeassistant"
DEFAULT_AVAILABILITY_TOPIC = "home-assistant/cover/availabilty"
DEFAULT_PAYLOAD_AVAILABLE = "online"
DEFAULT_PAYLOAD_NOT_AVAILABLE ="offline"
DEFAULT_STATE_MODE = "normally_open"
DEFAULT_INVERT_RELAY = False
DEFAULT_POLL_DELAY = 0
DEFAULT_PRESS_TIME = 0.2
DEFAULT_READ_DELAY = 0.5
DEFAULT_SWITCH_DEBOUNCE = 300

CONFIG_SCHEMA = vol.Schema(
    {
    "logging": vol.Schema(
        {
            vol.Required("log_level"): Any('DEBUG', 'INFO', 'WARNING','ERROR', 'CRITICAL'),
            vol.Required("show_timestamp"): bool
        }),
    "mqtt": vol.Schema(
        {
            vol.Required("host"): str,
            vol.Required("port"): int,
            vol.Required("user"): str,
            vol.Required("password"): str,
            vol.Optional("discovery", default = DEFAULT_DISCOVERY): Any(bool, None),
            vol.Optional("discovery_prefix", default = DEFAULT_DISCOVERY_PREFIX): Any(str, None),
            vol.Optional("availability_topic", default = DEFAULT_AVAILABILITY_TOPIC): Any(str, None),
            vol.Optional("payload_available", default = DEFAULT_PAYLOAD_AVAILABLE): Any(str,None),
            vol.Optional("payload_not_available", default = DEFAULT_PAYLOAD_NOT_AVAILABLE ): Any(str, None)


        }
    ),
    "doors": [vol.Schema(
        {
            vol.Required("id"): str,
            vol.Optional("uuid"): Any(str, None),
            vol.Optional("name"): Any(str, None), 
            vol.Required("relay"): int,
            vol.Required("state"): int,
            vol.Optional("open"): int,
            vol.Optional("state_mode", default = DEFAULT_STATE_MODE): Any(None, 'normally_closed', 'normally_open'),
            vol.Optional("invert_relay", default = DEFAULT_INVERT_RELAY): bool,
            vol.Optional("state_topic"): str,
            vol.Required("command_topic"): str,
            vol.Optional("poll_delay", default=DEFAULT_POLL_DELAY): int,
            vol.Optional("press_time", default=DEFAULT_PRESS_TIME): float,
            vol.Optional("read_delay", default=DEFAULT_READ_DELAY): float,
            vol.Optional("switch_debounce", default=DEFAULT_SWITCH_DEBOUNCE): int

        }
    )]
    })

