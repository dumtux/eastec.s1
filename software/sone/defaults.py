DEFAULT_STATUS = {
    "state": "standby",
    "sauna_id": "string",
    "firmware_version": 0,
    "target_temperature": 100,
    "current_temperature": 0,
    "target_timer": 60,
    "remaining_timer": 0,
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
        "identifier": "string",
        "state": "on",
        "mode": "low"
        }
    ],
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
            "identifier": "string",
            "state": "on",
            "mode": "low"
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
            "identifier": "string",
            "state": "on",
            "mode": "low"
            }
        ]
    }
}
