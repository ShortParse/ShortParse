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
        "discord_webhook_url": user.discord_webhook_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"status": "success", "message": "Successfully logged out."}


from pydantic import BaseModel

class SettingsUpdateRequest(BaseModel):
    discord_webhook_url: str | None = None


@router.post("/settings")
def update_user_settings(
    request: Request,
    payload: SettingsUpdateRequest,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Authenticated user not found.")

    webhook_url = payload.discord_webhook_url
    if webhook_url:
        webhook_url = webhook_url.strip()
        if not (webhook_url.startswith("https://discord.com/api/webhooks/") or webhook_url.startswith("https://discordapp.com/api/webhooks/")):
            raise HTTPException(status_code=400, detail="Invalid Discord Webhook URL format.")
    else:
        webhook_url = None

    user.discord_webhook_url = webhook_url
    db.commit()

    return {
        "status": "success",
        "message": "Settings updated successfully.",
        "discord_webhook_url": user.discord_webhook_url,
    }


@router.post("/settings/test-discord")
def test_discord_webhook(
    request: Request,
    payload: SettingsUpdateRequest,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    webhook_url = payload.discord_webhook_url
    if webhook_url:
        webhook_url = webhook_url.strip()
    else:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            webhook_url = user.discord_webhook_url

    if not webhook_url:
        raise HTTPException(status_code=400, detail="No Discord Webhook URL provided or configured.")

    if not (webhook_url.startswith("https://discord.com/api/webhooks/") or webhook_url.startswith("https://discordapp.com/api/webhooks/")):
        raise HTTPException(status_code=400, detail="Invalid Discord Webhook URL format.")

    test_embed = {
        "username": "ShortParse",
        "avatar_url": "https://raw.githubusercontent.com/ShortParse/ShortParse-Web/main/images/apple-touch-icon.png",
        "embeds": [
            {
                "title": "🛡️ ShortParse Webhook Connection Test",
                "description": "This message confirms that your ShortParse Discord Webhook integration is **online and working perfectly!**",
                "color": 3718392,
                "fields": [
                    {
                        "name": "Connection Status",
                        "value": "🟢 Active & Ready",
                        "inline": True
                    },
                    {
                        "name": "Integration Type",
                        "value": "Raid summary embeds",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "ShortParse - Automated Warcraft Logs Reviews"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=test_embed, timeout=10)
        if response.status_code not in (200, 204):
            raise RuntimeError(f"Discord API returned status {response.status_code}: {response.text}")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to post test message to Discord: {str(e)}",
        )

    return {"status": "success", "message": "Test message sent successfully!"}


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