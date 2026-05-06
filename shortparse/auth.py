import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"


def get_access_token() -> str:
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
    return response.json()["access_token"]