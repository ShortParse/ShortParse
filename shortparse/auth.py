import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"

_cached_token = None
_token_expires_at = 0.0


def get_access_token() -> str:
    global _cached_token, _token_expires_at

    if _cached_token and time.time() < _token_expires_at - 60:
        return _cached_token

    client_id = os.getenv("WARCRAFTLOGS_CLIENT_ID")
    client_secret = os.getenv("WARCRAFTLOGS_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing WARCRAFTLOGS_CLIENT_ID or WARCRAFTLOGS_CLIENT_SECRET in .env"
        )

    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=30,
    )

    response.raise_for_status()
    payload = response.json()

    _cached_token = payload["access_token"]
    expires_in = payload.get("expires_in", 3600)
    _token_expires_at = time.time() + expires_in

    return _cached_token