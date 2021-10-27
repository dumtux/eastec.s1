# requirements
#     pyjwt
#     requests

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography import x509


def check_token(token):
    n_decoded = jwt.get_unverified_header(token)
    kid_claim = n_decoded["kid"]

    response = requests.get("https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com")
    x509_key = response.json()[kid_claim]
    key = x509.load_pem_x509_certificate(x509_key.encode('utf-8'),  backend=default_backend())
    public_key = key.public_key()

    decoded_token = jwt.decode(token, public_key, ["RS256"], options=None, audience="smart-sauna-e7ed6")
    print(f"Decoded token : {decoded_token}")

check_token("TOKEN")
