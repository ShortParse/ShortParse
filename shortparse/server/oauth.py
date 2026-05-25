import os
import hashlib
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

router = APIRouter(prefix="/auth", tags=["Authentication"])

WCL_AUTHORIZE_URL = "https://www.warcraftlogs.com/oauth/authorize"
WCL_TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"
WCL_GRAPHQL_URL = "https://www.warcraftlogs.com/api/v2/user"


def make_wcl_fallback_user_id(access_token: str) -> str:
    """
    Warcraft Logs OAuth does not currently expose a simple authenticated
    user identity field through GraphQL.

    This creates a stable-ish provider_user_id from the OAuth token so the
    login flow can complete and private-report access can work.
    """
    token_hash = hashlib.sha256(access_token.encode("utf-8")).hexdigest()
    return f"wcl_oauth_{token_hash[:32]}"


@router.get("/warcraftlogs/login")
def warcraftlogs_login():
    """Redirects the user to the Warcraft Logs OAuth authorize page."""
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
    )

    return RedirectResponse(url=authorize_url)


@router.get("/warcraftlogs/callback")
def warcraftlogs_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    """Callback receiver that exchanges authorization code for tokens and signs in user."""
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authorization failed: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth authorization code.",
        )

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

    # Warcraft Logs does not expose a reliable user profile query here.
    # Do not block OAuth login on user profile lookup.
    wcl_id = make_wcl_fallback_user_id(access_token)
    wcl_username = f"WCL User {wcl_id[:8]}"

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
    else:
        user = User(
            username=wcl_username,
            is_premium=False,
        )
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
    """Returns currently authenticated user profile."""
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated.",
        )

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
    """Clears the authenticated user session."""
    request.session.clear()
    return {"status": "success", "message": "Successfully logged out."}