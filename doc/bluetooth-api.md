# Bluetooth API for the SOne device status control


## Protocol

We will use *Radio frequency communication* (RFCOMM) protocol for the communication between SOne device and a mobile phone.

> RFCOMM provides a simple reliable data stream to the user, similar to TCP. It is used directly by many telephony related profiles as a carrier for AT commands, as well as being a transport layer for OBEX over Bluetooth.
>
>Many Bluetooth applications use RFCOMM because of its widespread support and publicly available API on most operating systems. Additionally, applications that used a serial port to communicate can be quickly ported to use RFCOMM.
>
> *-- [List of Bluetooth protocols](https://en.wikipedia.org/wiki/List_of_Bluetooth_protocols) by Wikipedia --*


## Libraries used

We will use the [BlueDot](https://bluedot.readthedocs.io/en/latest/) library for implementing API functions on the SOne device side. Note that the BlueDot library is used for device-side only.

For more details, read the [BlueDot - Bluetooth Comm API](https://bluedot.readthedocs.io/en/latest/btcommapi.html) section.


## Converting the REST API to the Bluetooth API

An REST API endpoint has some key properties.
* endpoint
* URL parameter
* query
* body
* response

We assume that the Bluetooth RFCOMM client instance of the mobile application will send a stringified JSON data of the following format.

```json
{
    "method": "GET",
    "endpoint": "/sauna/{sauna_id}/status",
    "parameters": {"sauna_id": sauna_id},
    "description": "get status",
    "body": null
}
```

The Bluetooth RFCOMM server instance running on the SOne device will return the required data, also in a stringified JSON format.


## Example application

As a reference for the mobile app developers, we built a small example application.
It has a Bluetooth RFCOMM client and REST API facade interface.

After cloning this repository,

```sh
cd software
python3 -m venv env
pip install fastapi uvicorn
uvicorn sone.bt_app:app
```

, then visit <http://localhost:8000/docs>.
