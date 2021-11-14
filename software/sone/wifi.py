from typing import List

from pywifi import PyWiFi

from .logger import Logger


logger = Logger.instance()
wifi = PyWiFi()
interface = None

try:
    interface_list = wifi.interfaces()
    for _interface in interface_list:
        if _interface.name() == 'wlan0':
            interface = _interface
except FileNotFoundError:
    logger.error("No WiFi device found. Maybe you're running this app on a computer with no WiFi device for development?")


def list_networks() -> List[str]:
    if interface == None:
        return []
    interface.scan()
    return [profile.ssid for profile in interface.scan_results() if len(profile.ssid) > 0]  # omit empty string ssid
