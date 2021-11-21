# SOne - iHealth Sauna Control System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Test](https://github.com/hotteshen/eastec.s1/actions/workflows/python-package.yml/badge.svg)


## Overview

**SOne** is a collection of the human interface device and software, server side dashboard and API softwares.
**KFive** is the power control module of sauna heaters and lights. which is controlled by *SOne*.

  - built with an Linux-based SBC
  - User interface on touchscreen
  - communicating with Cloud server and mobile app
  - controlling the KFive

When talking about hardwares, *SOne" means the human interface device powered by Linux SBC.
When talking about softwaer, *SOne" refers this whole project.


## Development

* Linux or MacOS is recommended for development. At the moment, Windows is not supported.
* Python version greater than 3.8 is recomended.

Clone the repository.
```sh
git clone https://github.com/hotteshen/eastec.s1 && cd eastec.s1
```

Create a vertual environment and install dependencies.
```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Running as device vs running as server.

The device-side software and server side software shares many common data structure and patterns.
Thus, both softwares are implemented in this same repository, as a single Python package named `sone`.

With the above virtual environment is activated,
```sh
# show help
python -m sone --help

# show help of device mode command
python -m sone device --help

# show help of server mode command
python -m sone cloud --help

# run server at the port 8888
python -m sone cloud --port 8888

# run device at the port 8000, bind with the server running at port 8000
python -m sone device --port 8000 --cloud-url http://localhost:8888
```

By default, server port is set as 8001, and device looks for it when no `--cloud-url` is given.
Thus, server and device can be run on two different terminals with these simple commands
```sh
# on terminal A, activate virtualenv
python -m sone cloud  # this will run the server at the default port 8001
# This is equivalent to
# python -m sone cloud --host 0.0.0.0 --port 8001

# on another terminal B, activate virtualenv
python -m sone device  # this will run the device app at the default device port 8000, connect to the default development server port 8001
# This is equivalent to
# python -m sone device --host 0.0.0.0 --port 8000 --cloud-url http://localhost:8001
```

Most of the softwares parts are tested with unit tests and functional tests.
To run all tests, run `pytest` command, With the above virtual environment is activated,
```sh
pytest
```


## Deployment

The SOne server software can be deployed on GCP.
The SOne server is a stateful server. It preservers SOne device websocket connections on server side.
In other words, SOne server is **not a stateless server*.
Thus when deploying SOne to the cloud platforms, need to **restrickt the server instance as only one**.

For more details, refer the [`app.yaml`](./app.yaml)


---

* Created on 6 Aug 2021
* Last modified on 21 Nov 2021
