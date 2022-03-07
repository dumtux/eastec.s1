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
	"model_name": "unknown",
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
