import os
from pathlib import Path

from . import __version__


_CONF_PATH = Path.home() / '.eastec-sone'
if not os.path.exists(_CONF_PATH):
    os.mkdir(_CONF_PATH)

DB_FILE_PATH = _CONF_PATH / 'db.json'
UART_EN_PIN = 12
UART_PORT = '/dev/serial0'
UART_BAUDRATE = 4800

DEFAULT_STATUS = {
    "state": "standby",
    "sauna_id": "string",
    "sysinfo": {
        "firmware_version": __version__,
        "time_since_sys_boot": "unknown",
        "time_since_app_start": "unknown",
    },
    "target_temperature": 30,
    "current_temperature": 0,
    "timer": 60,
    "lights": [
        {
        "identifier": "string",
        "state": "on",
        "color": {
            "r": 255,
            "g": 255,
            "b": 255
        },
        "brightness": 1
        }
    ],
    "heaters": [
        {
            "name": "A",
            "level": 0,
        },
        {
            "name": "B",
            "level": 0,
        },
        {
            "name": "C",
            "level": 0,
        }
    ],
    "program": {
        "name": "Default Program",
        "target_temperature": 50,
        "timer_duration": 30,
        "lights": [
            {
                "identifier": "string",
                "state": "on",
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
                "brightness": 1
            }
        ],
        "heaters": [
            {
                "name": "A",
                "level": 0,
            },
            {
                "name": "B",
                "level": 0,
            },
            {
                "name": "C",
                "level": 0,
            }
        ]
    }
}

DEFAULT_SCHEDULE = {
    "id": "df67888a21123f123123ee123",
    "user": "kemalenver@gmail.com",
    "sauna": "aUniqueIdForTheSauna",
    "first_fire_time": "2021-06-27T05:03:15+11:00",
    "frequency": "once",
    "program": {
        "name": "string",
        "target_temperature": 50,
        "timer_duration": 30,
        "lights": [
            {
                "identifier": "string",
                "state": "on",
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
                "brightness": 1
            }
        ],
        "heaters": [
            {
                "name": "A",
                "level": 0,
            },
            {
                "name": "B",
                "level": 0,
            },
            {
                "name": "C",
                "level": 0,
            }
        ]
    }
}
