DEFAULT_STATUS = {
    "state": "standby",
    "sauna_id": "string",
    "firmware_version": 0,
    "target_temperature": 100,
    "current_temperature": 0,
    "target_timer": 60,
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
