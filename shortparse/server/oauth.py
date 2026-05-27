import os
import requests
from urllib.parse import urlparse
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
    PATREON_CLIENT_ID,
    PATREON_CLIENT_SECRET,
    PATREON_REDIRECT_URI,
    PATREON_CAMPAIGN_ID,
)

from shortparse.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_dynamic_redirect_uri(request: Request, provider: str, default_uri: str) -> str:
    """
    Dynamically constructs the OAuth redirect URI based on the incoming request's scheme and host.
    This ensures that subdomains (e.g., www vs. dev) and SSL termination work seamlessly.
    """
    try:
        parsed = urlparse(default_uri)
        path = parsed.path if parsed.path else f"/api/auth/{provider}/callback"
        
        # Determine protocol (respect reverse proxy headers)
        proto = request.headers.get("x-forwarded-proto") or request.url.scheme
        
        # Determine host (respect reverse proxy headers)
        host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
        
        if host:
            return f"{proto}://{host}{path}"
    except Exception as e:
        logger.warning("Error generating dynamic redirect URI for %s: %s. Falling back to default.", provider, e)
    
    return default_uri

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
def warcraftlogs_login(request: Request):
    if not WCL_CLIENT_ID or not WCL_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Warcraft Logs OAuth client credentials are not configured in settings.",
        )

    redirect_uri = get_dynamic_redirect_uri(request, "warcraftlogs", WCL_REDIRECT_URI)
    authorize_url = (
        f"{WCL_AUTHORIZE_URL}"
        f"?client_id={WCL_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
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

    redirect_uri = get_dynamic_redirect_uri(request, "warcraftlogs", WCL_REDIRECT_URI)
    try:
        token_response = requests.post(
            WCL_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
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

    patron_account = db.query(LinkedAccount).filter(
        LinkedAccount.user_id == user.id,
        LinkedAccount.provider == "patreon",
    ).first()

    return {
        "id": str(user.id),
        "username": user.username,
        "is_premium": user.is_premium,
        "premium_tier": user.premium_tier,
        "discord_webhook_url": user.discord_webhook_url,
        "is_patreon_linked": patron_account is not None,
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


# ==============================================================================
# Patreon OAuth 2.0 Integration (API v2)
# ==============================================================================

PATREON_AUTHORIZE_URL = "https://www.patreon.com/oauth2/authorize"
PATREON_TOKEN_URL = "https://www.patreon.com/api/oauth2/token"
PATREON_API_URL = "https://www.patreon.com/api/oauth2/v2"


def refresh_patreon_token(db: Session, account: LinkedAccount) -> str:
    """Helper to refresh expired Patreon tokens securely."""
    if not PATREON_CLIENT_ID or not PATREON_CLIENT_SECRET:
        raise RuntimeError("Patreon client credentials not configured.")

    try:
        response = requests.post(
            PATREON_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": account.refresh_token,
                "client_id": PATREON_CLIENT_ID,
                "client_secret": PATREON_CLIENT_SECRET,
            },
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()
    except Exception as e:
        raise RuntimeError(f"Patreon token refresh failed: {str(e)}")

    account.access_token = token_data["access_token"]
    if "refresh_token" in token_data:
        account.refresh_token = token_data["refresh_token"]
    expires_in = token_data.get("expires_in", 2678400)
    account.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    account.updated_at = datetime.utcnow()
    db.commit()

    return account.access_token


@router.get("/patreon/login")
def patreon_login(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in with Warcraft Logs before connecting Patreon.",
        )

    if not PATREON_CLIENT_ID or not PATREON_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Patreon OAuth client credentials are not configured in settings.",
        )

    redirect_uri = get_dynamic_redirect_uri(request, "patreon", PATREON_REDIRECT_URI)
    authorize_url = (
        f"{PATREON_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={PATREON_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=identity identity.memberships"
    )

    return RedirectResponse(url=authorize_url)


@router.get("/patreon/callback")
def patreon_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User session expired or not authenticated.",
        )

    if error:
        raise HTTPException(status_code=400, detail=f"OAuth authorization failed: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing OAuth authorization code.")

    redirect_uri = get_dynamic_redirect_uri(request, "patreon", PATREON_REDIRECT_URI)
    try:
        token_response = requests.post(
            PATREON_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": PATREON_CLIENT_ID,
                "client_secret": PATREON_CLIENT_SECRET,
            },
            timeout=15,
        )
        token_response.raise_for_status()
        token_data = token_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange token with Patreon: {str(e)}",
        )

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 2678400)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Query Patreon API v2 for identity and memberships
    identity_url = (
        f"{PATREON_API_URL}/identity"
        f"?include=memberships.currently_entitled_tiers,memberships.campaign"
        f"&fields[user]=full_name,thumb_url"
        f"&fields[member]=patron_status,currently_entitled_amount_cents"
        f"&fields[tier]=title,amount_cents"
    )

    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "ShortParse - Campaign Integration v2"
        }
        user_response = requests.get(identity_url, headers=headers, timeout=15)
        user_response.raise_for_status()
        user_info = user_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch user details from Patreon API: {str(e)}",
        )

    patron_data = user_info.get("data", {})
    patron_id = str(patron_data.get("id"))

    # Determine premium status against Campaign ID
    is_premium = False
    premium_tier = None

    included = user_info.get("included", [])
    memberships = []
    tiers_lookup = {}

    for item in included:
        item_type = item.get("type")
        item_id = item.get("id")
        if item_type == "tier":
            tiers_lookup[item_id] = item.get("attributes", {}).get("title")
        elif item_type == "member":
            memberships.append(item)

    for member in memberships:
        relationships = member.get("relationships", {})
        campaign_rel = relationships.get("campaign", {}).get("data", {})
        tiers_rel = relationships.get("currently_entitled_tiers", {}).get("data", [])

        campaign_id = campaign_rel.get("id")

        if campaign_id == PATREON_CAMPAIGN_ID:
            status = member.get("attributes", {}).get("patron_status")
            if status == "active_patron":
                is_premium = True
                active_tier_names = []
                for t in tiers_rel:
                    t_id = t.get("id")
                    if t_id in tiers_lookup:
                        active_tier_names.append(tiers_lookup[t_id])

                if active_tier_names:
                    premium_tier = ", ".join(active_tier_names)
                else:
                    premium_tier = "Premium Patron"
                break

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_premium = is_premium
    user.premium_tier = premium_tier

    linked_account = db.query(LinkedAccount).filter(
        LinkedAccount.user_id == user.id,
        LinkedAccount.provider == "patreon",
    ).first()

    if linked_account:
        linked_account.provider_user_id = patron_id
        linked_account.access_token = access_token
        linked_account.refresh_token = refresh_token
        linked_account.expires_at = expires_at
        linked_account.updated_at = datetime.utcnow()
    else:
        linked_account = LinkedAccount(
            user_id=user.id,
            provider="patreon",
            provider_user_id=patron_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(linked_account)

    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "/")
    return RedirectResponse(url=f"{frontend_url.rstrip('/')}/")


@router.post("/patreon/sync")
def patreon_sync(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    account = db.query(LinkedAccount).filter(
        LinkedAccount.user_id == user_id,
        LinkedAccount.provider == "patreon",
    ).first()

    if not account:
        raise HTTPException(
            status_code=400,
            detail="You do not have a linked Patreon account.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    access_token = account.access_token
    if not account.expires_at or account.expires_at <= datetime.utcnow() + timedelta(days=1):
        try:
            access_token = refresh_patreon_token(db, account)
        except Exception as e:
            user.is_premium = False
            user.premium_tier = None
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Patreon credentials expired and could not be refreshed: {str(e)}",
            )

    identity_url = (
        f"{PATREON_API_URL}/identity"
        f"?include=memberships.currently_entitled_tiers,memberships.campaign"
        f"&fields[user]=full_name,thumb_url"
        f"&fields[member]=patron_status,currently_entitled_amount_cents"
        f"&fields[tier]=title,amount_cents"
    )

    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "ShortParse - Campaign Integration v2"
        }
        user_response = requests.get(identity_url, headers=headers, timeout=15)

        if user_response.status_code == 401:
            try:
                access_token = refresh_patreon_token(db, account)
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": "ShortParse - Campaign Integration v2"
                }
                user_response = requests.get(identity_url, headers=headers, timeout=15)
            except Exception:
                pass

        user_response.raise_for_status()
        user_info = user_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch user details from Patreon API: {str(e)}",
        )

    is_premium = False
    premium_tier = None

    included = user_info.get("included", [])
    memberships = []
    tiers_lookup = {}

    for item in included:
        item_type = item.get("type")
        item_id = item.get("id")
        if item_type == "tier":
            tiers_lookup[item_id] = item.get("attributes", {}).get("title")
        elif item_type == "member":
            memberships.append(item)

    for member in memberships:
        relationships = member.get("relationships", {})
        campaign_rel = relationships.get("campaign", {}).get("data", {})
        tiers_rel = relationships.get("currently_entitled_tiers", {}).get("data", [])

        campaign_id = campaign_rel.get("id")

        if campaign_id == PATREON_CAMPAIGN_ID:
            status = member.get("attributes", {}).get("patron_status")
            if status == "active_patron":
                is_premium = True
                active_tier_names = []
                for t in tiers_rel:
                    t_id = t.get("id")
                    if t_id in tiers_lookup:
                        active_tier_names.append(tiers_lookup[t_id])

                if active_tier_names:
                    premium_tier = ", ".join(active_tier_names)
                else:
                    premium_tier = "Premium Patron"
                break

    user.is_premium = is_premium
    user.premium_tier = premium_tier
    db.commit()

    return {
        "status": "success",
        "is_premium": user.is_premium,
        "premium_tier": user.premium_tier,
    }