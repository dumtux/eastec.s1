import os
from pathlib import Path


_CONF_PATH = Path.home() / '.eastec-sone'
if not os.path.exists(_CONF_PATH):
    os.mkdir(_CONF_PATH)

DB_FILE_PATH = _CONF_PATH / 'db.json'
UART_EN_PIN = 12
UART_PORT = '/dev/serial0'
UART_BAUDRATE = 4800
