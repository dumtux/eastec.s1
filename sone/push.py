import base64
import json
import os
import time

import OpenSSL
from OpenSSL import crypto

from .conf import (
    PUSH_TEAMID,
    PUSH_KEYID,
    PUSH_SECRET_KEY,
    PUSH_BUNDLEID,
    PUSH_ENDPOINT_DEV,
    PUSH_ENDPOINT_PROD,
    PUSH_URLPATH,
)
from .utils import Logger


def push(token: str, data: dict) -> None:
    data = json.dumps(data)
    url_dev = f"{PUSH_ENDPOINT_DEV}{PUSH_URLPATH}{token}"
    url_prod = f"{PUSH_ENDPOINT_PROD}{PUSH_URLPATH}{token}"

    header = '{ "alg": "ES256", "kid": "%s" }' % PUSH_KEYID
    header = base64.b64encode(header.encode()).decode()

    t = int(time.time())
    claims = '{ "iss": "%s", "iat": %d }' % (PUSH_TEAMID, t)
    claims = base64.b64encode(claims.encode()).decode()

    try:
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, PUSH_SECRET_KEY)
    except OpenSSL.crypto.Error:
        Logger.instance().error("Bad private key file. Skipped pushing notification for state change.")
        return
    sign = crypto.sign(pkey, f"{header}.{claims}".encode(), "sha256")
    sign = base64.b64encode(sign).decode()

    jwt = f"{header}.{claims}.{sign}"

    headers = dict()
    headers["Authorization"] = f"Bearer {jwt}"
    headers["apns-topic"] = PUSH_BUNDLEID
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    payload = data.replace('"', '\\"')
    cmd = f'curl -v --http2 --header "authorization: bearer {jwt}" --header "apns-topic: {PUSH_BUNDLEID}" --data "{payload}" {url_dev}'
    Logger.instance().log(cmd)
    os.system(cmd)
