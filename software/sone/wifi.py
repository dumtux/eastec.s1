from typing import List

from fastapi import HTTPException
from netifaces import ifaddresses
from pywifi import PyWiFi

from .logger import Logger


NO_WIFI_DEVICE_DESC = "No WiFi device found. Maybe you're running this app on a computer with no WiFi device for development?"

logger = Logger.instance()
wifi = PyWiFi()
interface = None

try:
    interface_list = wifi.interfaces()
    for _interface in interface_list:
        if _interface.name() == 'wlan0':  # on Raspberry CM4, the default WiFi device name is 'wlan0'
            interface = _interface
except FileNotFoundError:  # on desktop computer without WiFi device
    logger.error(NO_WIFI_DEVICE_DESC)


def list_networks() -> List[str]:
    if interface == None:
        raise HTTPException(status_code=422, detail=NO_WIFI_DEVICE_DESC)
    interface.scan()
    return [profile.ssid for profile in interface.scan_results() if len(profile.ssid) > 0]  # omit empty string ssid


def connect_wifi(ssid: str, key: str) -> str:
    'connect to the give WiFi network, return the IP address'
    if interface == None:
        raise HTTPException(status_code=422, detail=NO_WIFI_DEVICE_DESC)
    profile = None
    for _profile in interface.scan_results():
        if _profile.ssid == ssid:
            profile = _profile
    if profile == None:
        raise HTTPException(status_code=422, detail=f"Cannot find the network '{ssid}'")

    profile.key = key
    interface.connect(profile)

    return ifaddresses('wlan0')[2][0]['addr']  # return the allocated IP address
