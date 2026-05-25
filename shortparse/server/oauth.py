import os
import requests
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from shortparse.database import get_db
from shortparse.db_models import User, LinkedAccount
from shortparse.settings import (
    WCL_CLIENT_ID,
    WCL_CLIENT_SECRET,
    WCL_REDIRECT_URI,
)

from shortparse.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

WCL_AUTHORIZE_URL = "https://www.warcraftlogs.com/oauth/authorize"
WCL_TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"
WCL_GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/user"


def get_wcl_user_info(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    query = """
    query {
        userData {
            currentUser {
                id
                name
            }
        }
    }
    """

    response = requests.post(
        WCL_GRAPHQL_URL,
        json={"query": query},
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()

    payload = response.json()

    if "errors" in payload:
        raise RuntimeError(f"WarcraftLogs API returned errors: {payload['errors']}")

    user_data = payload.get("data", {}).get("userData", {}).get("currentUser")

    if not user_data:
        raise RuntimeError("WarcraftLogs currentUser was not found in the response")

    return user_data


@router.get("/warcraftlogs/login")
def warcraftlogs_login():
    if not WCL_CLIENT_ID or not WCL_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Warcraft Logs OAuth client credentials are not configured in settings.",
        )

    authorize_url = (
        f"{WCL_AUTHORIZE_URL}"
        f"?client_id={WCL_CLIENT_ID}"
        f"&redirect_uri={WCL_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=view-user-profile view-private-reports"
    )

    return RedirectResponse(url=authorize_url)


@router.get("/warcraftlogs/callback")
def warcraftlogs_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth authorization failed: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth authorization code.")

    try:
        token_response = requests.post(
            WCL_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": WCL_REDIRECT_URI,
                "client_id": WCL_CLIENT_ID,
                "client_secret": WCL_CLIENT_SECRET,
            },
            timeout=15,
        )
        token_response.raise_for_status()
        token_data = token_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange token with Warcraft Logs: {str(e)}",
        )

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    try:
        wcl_user = get_wcl_user_info(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch user profile details from Warcraft Logs: {str(e)}",
        )

    wcl_id = str(wcl_user["id"])
    wcl_username = wcl_user["name"]

    linked_account = db.query(LinkedAccount).filter(
        LinkedAccount.provider == "warcraftlogs",
        LinkedAccount.provider_user_id == wcl_id,
    ).first()

    if linked_account:
        user = linked_account.user
        linked_account.access_token = access_token
        linked_account.refresh_token = refresh_token
        linked_account.expires_at = expires_at
        linked_account.updated_at = datetime.utcnow()

        if user.username != wcl_username:
            user.username = wcl_username
    else:
        user = User(username=wcl_username, is_premium=False)
        db.add(user)
        db.flush()

        linked_account = LinkedAccount(
            user_id=user.id,
            provider="warcraftlogs",
            provider_user_id=wcl_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(linked_account)

    db.commit()

    request.session["user_id"] = str(user.id)
    request.session["username"] = user.username

    frontend_url = os.getenv("FRONTEND_URL", "/")
    return RedirectResponse(url=frontend_url)


@router.get("/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Authenticated session user not found in database.",
        )

    return {
        "id": str(user.id),
        "username": user.username,
        "is_premium": user.is_premium,
        "premium_tier": user.premium_tier,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": "success", "message": "Successfully logged out."}


@router.get("/guilds")
def get_guilds(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    from shortparse.server.auth_helpers import get_valid_wcl_account
    from shortparse.client import WarcraftLogsClient

    account = get_valid_wcl_account(db, user_id)
    if not account:
        raise HTTPException(
            status_code=400,
            detail="User does not have a linked Warcraft Logs account.",
        )

    try:
        client = WarcraftLogsClient(
            access_token=account.access_token,
            use_user_endpoint=True,
        )
        guilds = client.get_user_guilds()
        return {"guilds": guilds}
    except Exception as e:
        logger.exception("Failed to fetch guilds from Warcraft Logs API")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch guilds from Warcraft Logs API: {str(e)}",
        )


@router.get("/guilds/{guild_id}/reports")
def get_guild_reports(
    guild_id: int,
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    from shortparse.server.auth_helpers import get_valid_wcl_account
    from shortparse.client import WarcraftLogsClient

    account = get_valid_wcl_account(db, user_id)
    if not account:
        raise HTTPException(
            status_code=400,
            detail="User does not have a linked Warcraft Logs account.",
        )

    try:
        client = WarcraftLogsClient(
            access_token=account.access_token,
            use_user_endpoint=True,
        )
        reports = client.get_guild_reports(guild_id, limit=limit)
        return {"reports": reports}
    except Exception as e:
        logger.exception("Failed to fetch guild reports from Warcraft Logs API")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch guild reports from Warcraft Logs API: {str(e)}",
        )