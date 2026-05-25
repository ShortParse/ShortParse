from datetime import datetime, timedelta, UTC

import requests
from sqlalchemy.orm import Session

from shortparse.db_models import LinkedAccount
from shortparse.settings import WCL_CLIENT_ID, WCL_CLIENT_SECRET

WCL_TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def get_user_wcl_account(db: Session, user_id):
    """
    Returns the user's linked Warcraft Logs account, if one exists.

    This does not refresh tokens by itself.
    """
    return (
        db.query(LinkedAccount)
        .filter(
            LinkedAccount.user_id == user_id,
            LinkedAccount.provider == "warcraftlogs",
        )
        .first()
    )


def refresh_wcl_token(db: Session, linked_account: LinkedAccount) -> LinkedAccount:
    """
    Refreshes a Warcraft Logs OAuth token using the stored refresh token.
    """
    if not linked_account.refresh_token:
        raise RuntimeError("Warcraft Logs account has no refresh token. User must reconnect.")

    response = requests.post(
        WCL_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": linked_account.refresh_token,
            "client_id": WCL_CLIENT_ID,
            "client_secret": WCL_CLIENT_SECRET,
        },
        timeout=15,
    )

    response.raise_for_status()
    token_data = response.json()

    linked_account.access_token = token_data["access_token"]
    linked_account.refresh_token = token_data.get(
        "refresh_token",
        linked_account.refresh_token,
    )
    linked_account.expires_at = utc_now() + timedelta(
        seconds=token_data.get("expires_in", 3600)
    )
    linked_account.updated_at = utc_now()

    db.commit()
    db.refresh(linked_account)

    return linked_account


def get_valid_wcl_account(db: Session, user_id) -> LinkedAccount | None:
    """
    Returns a linked Warcraft Logs account with a valid access token.

    If the token is expired, this attempts to refresh it.
    If no account is linked, returns None.
    """
    linked_account = get_user_wcl_account(db, user_id)

    if not linked_account:
        return None

    if linked_account.expires_at and linked_account.expires_at <= utc_now():
        linked_account = refresh_wcl_token(db, linked_account)

    return linked_account