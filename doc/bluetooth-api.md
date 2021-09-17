# Bluetooth API for the SOne device status control

**The contents of this document are provisional. It may be changed during the integration of BT API and GUI Application.**


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
    "parameters": {"sauna_id": "sauna_id"},
    "description": "get status",
    "body": null
}
```

The Bluetooth RFCOMM server instance running on the SOne device will return the required data, also in a stringified JSON format.


## Example application

As a reference for the mobile app developers, we built a small example application.
It has a Bluetooth RFCOMM client and REST API facade interface.

After cloning this repository, install Python dependencies and run the facade server.

```sh
cd software
python3 -m venv env
pip install fastapi uvicorn
uvicorn sone.bt_app:app
```

Open <http://localhost:8000/docs> and test the API.


## API Reference (by examples)

### Get Sauna Status

* Get the Sauna status of the given `sauna_id`.
* Return data wrapping the response of `/sauna/{sauna_id}/status` GET endpoint.

#### Example request

```json
{
    "method": "GET",
    "endpoint": "/sauna/{sauna_id}/status",
    "parameters": {"sauna_id": "foo_sauna"},
    "description": "Get Sauna Status",
    "body": null
}
```

#### Example response

```json
{
    "response_code": "200",
    "body": {
        "state": "string",
        "sauna_id": "string",
        "firmware_version": 0,
        // ...
    }
}
```

```json
{
    "response_code": "404",
    "body": {
        "detail": "Sauna ID does nto exist."
    }
}
```

### Update Sauna Status

* Update a Sauna state of the given `sauna_id`.
* Return data wrapping the response of `/sauna/{sauna_id}/status` PUT endpoint.

#### Example request

```json
{
    "method": "PUT",
    "endpoint": "/sauna/{sauna_id}/status",
    "parameters": {"sauna_id": "sauna_id"},
    "description": "Update Sauna Status",
    "body": {
        "state": "string"
    }
}
```

#### Example response

(same format as of *Get Sauna Status*, with the state updated)

### Get Sauna Schedules

* Get the Sauna schedules list of the given `sauna_id`.
* Return data wrapping the response of `/sauna/{sauna_id}/schedules` GET endpoint.

#### Example request

```json
{
    "method": "GET",
    "endpoint": "/sauna/{sauna_id}/schedules",
    "parameters": {"sauna_id": "sauna_id"},
    "description": "Get Sauna Schedules",
    "body": null
}
```

#### Example response

```json
{
    "response_code": "200",
    "body": [
        {
            "id": "string",
            "user": "string",
            "sauna": "string",
            "frequency": "string",
            // ...
        },
        //...
    ]
}
```

```json
{
    "response_code": "404",
    "body": {
        "detail": "Sauna ID does nto exist."
    }
}
```

### Add Sauna Schedules

* Add multiple Sauna schedules to the schedule list of the given `sauna_id`.
* Return data wrapping the response of `/sauna/{sauna_id}/schedules` POST endpoint.

#### Example request

```json
{
    "method": "POST",
    "endpoint": "/sauna/{sauna_id}/schedules",
    "parameters": {"sauna_id": "sauna_id"},
    "description": "Add Sauna Schedules",
    "body": [
        // enumerate of schedules here
    ]
}
```

#### Example response

(same format as of *Get Sauna Schedules*, with the new schedules added)

### Delete Sauna Schedule

* Delete a schedule of the given `schedule_id` from the schedule list of the given `sauna_id`.
* Return data wrapping the response of `/sauna/{sauna_id}/schedules/{schedule_id}` DELETE endpoint.

#### Example request

```json
{
    "method": "DELETE",
    "endpoint": "/sauna/{sauna_id}/schedules",
    "parameters": {"sauna_id": "sauna_id"},
    "description": "Delete Sauna Schedule",
    "body": null
}
```
#### Example response

(same format as of *Get Sauna Schedules*, with the given schedule deleted)


---

* Created on 15 Sep 2021
* Last modified on 18 Sep 2021
