import asyncio
from typing import List

from fastapi import HTTPException
from netifaces import ifaddresses
from pywifi import const, PyWiFi, Profile

from .utils import Logger


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


async def connect_wifi(ssid: str, key: str) -> bool:
    'connect to the give WiFi network, return True on success.'
    if interface == None:
        raise HTTPException(status_code=422, detail=NO_WIFI_DEVICE_DESC)
    if ssid not in [profile.ssid for profile in interface.scan_results() if len(profile.ssid) > 0]:
        raise HTTPException(status_code=422, detail=f"Cannot find the network '{ssid}'")

    interface.disconnect()
    while interface.status() != const.IFACE_DISCONNECTED:
        await asyncio.sleep(0.1)
    interface.remove_all_network_profiles()

    profile = Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = key

    interface.remove_all_network_profiles()
    tmp_profile = interface.add_network_profile(profile)

    interface.connect(tmp_profile)
    # while interface.status() != const.IFACE_CONNECTING:
        # await asyncio.sleep(0.1)
    for i in range(8):
        await asyncio.sleep(1)
        if interface.status() == const.IFACE_CONNECTED:
            break

    if interface.status() == const.IFACE_CONNECTED:
        return True

    raise HTTPException(status_code=400, detail=f"Cannot connect to {ssid}, is passcode correct?")


def wifi_ip_addr() -> str:
    try:
        return ifaddresses('wlan0')[2][0]['addr']
    except ValueError:
        raise HTTPException(status_code=422, detail=NO_WIFI_DEVICE_DESC)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"No IP address allocated to 'wlan0'.")


def is_wifi_connected() -> bool:
    return interface.status() == const.IFACE_CONNECTED


async def connect_status() -> bool:
    if interface == None:
        return False
        raise HTTPException(status_code=422, detail=NO_WIFI_DEVICE_DESC)

    if interface.status() == const.IFACE_CONNECTED:
        return True
    else:
        return False
