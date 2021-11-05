import jwt
import httpx
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from fastapi import HTTPException, Header


async def verify_token(token: str = Header("Authorization")):
    if not _verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized token.")


def _verify_token(token: str) -> bool:
    try:
        n_decoded = jwt.get_unverified_header(token)
        kid_claim = n_decoded["kid"]
        response = httpx.get("https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com")
        x509_key = response.json()[kid_claim]
        key = x509.load_pem_x509_certificate(x509_key.encode('utf-8'),  backend=default_backend())
        public_key = key.public_key()
        decoded_token = jwt.decode(token, public_key, ["RS256"], options=None, audience="smart-sauna-e7ed6")
        return True
    except jwt.exceptions.ExpiredSignatureError:
        return False
    except jwt.exceptions.DecodeError:
        return False


