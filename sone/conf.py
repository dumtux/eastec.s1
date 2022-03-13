import os
from pathlib import Path

from . import __version__

_CONF_PATH = Path.home() / '.eastec-sone'
if not os.path.exists(_CONF_PATH):
    os.mkdir(_CONF_PATH)

TOKEN_FILE_PATH = _CONF_PATH / 'token'
KV_FILE_PATH = str(_CONF_PATH / 'kv.vedis')
UART_EN_PIN = 12
UART_PORT = '/dev/serial0'
UART_BAUDRATE = 4800

DASHBOARD_PASSWORD = "PASSWORD"

PUSH_TEAMID = "6KUC472N2V"
PUSH_KEYID = "2YVY9SX98C"
PUSH_BUNDLEID = "com.healtech.foundspace"
PUSH_ENDPOINT_DEV = "https://api.sandbox.push.apple.com:443"
PUSH_ENDPOINT_PROD = "https://api.push.apple.com:443"
PUSH_URLPATH = "/3/device/"
try:
    with open(_CONF_PATH / 'found-space-push-key.p8') as fp:
        PUSH_SECRET_KEY = fp.read()
except FileNotFoundError:
    PUSH_SECRET_KEY = """-----BEGIN PRIVATE KEY-----
................................................................
................................................................
................................................................
........
-----END PRIVATE KEY-----"""

TEMP_DELTA = 3

REED_IN = 27
LED_R_1 = 6
LED_G_1 = 5
LED_B_1 = 4
LED_MONO_1 = 7
LED_MONO_2 = 8
LED_R_2 = 11
LED_G_2 = 10
LED_B_2 = 9

PWM_FREQ = 200

DEFAULT_STATUS = {
    "state": "standby",
    "sauna_id": "string",
    "sysinfo": {
        "model_name": "unknown",
        "firmware_version": __version__,
        "time_since_sys_boot": "unknown",
        "time_since_app_start": "unknown",
    },
    "target_temperature": 30,
    "current_temperature": 0,
    "timer": 60,
    "lights": [
        {
            "name": "RGB_1",
            "state": False,
            "color": {
                "r": 255,
                "g": 255,
                "b": 255
            },
        },
        {
            "name": "RGB_2",
            "state": False,
            "color": {
                "r": 255,
                "g": 255,
                "b": 255
            },
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
                "name": "RGB_1",
                "state": False,
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
            },
            {
                "name": "RGB_2",
                "state": False,
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
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
                "name": "RGB_1",
                "state": False,
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
            },
            {
                "name": "RGB_2",
                "state": False,
                "color": {
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
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

DEPLOY_TOKEN = """-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
"""

SSH_CONFIG = """
 Host github-eastec.s1
            HostName github.com
            AddKeysToAgent yes
            PreferredAuthentications publickey
            IdentityFile /root/.ssh/id_eastec.s1
"""
