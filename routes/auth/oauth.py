from fastapi import APIRouter, Depends, Request, HTTPException
from authlib.integrations.starlette_client import OAuthError
from auth.oauth import get_or_create_user, oauth
from database.db import get_db
from auth.security import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])

@router.get("/login/{provider}")
async def login(request: Request, provider: str):
    if not oauth.exists(provider):
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")

    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await oauth[provider].authorize_redirect(request, redirect_uri)



# @router.route("/callback/{provider}", methods=["GET", "POST"])
@router.get("/callback/{provider}")
@router.post("/callback/{provider}")
async def auth_callback(request: Request, provider: str, db: AsyncSession = Depends(get_db)):
    if provider not in oauth:
        raise HTTPException(status_code=400, detail="Unsupported OAuth provider")
    try:
        if provider == "apple":
            # Apple sends form POST, handle accordingly
            token = await oauth.apple.authorize_access_token(request)
            # You get id_token as JWT from Apple
            user_info = token.get('id_token_claims')
            # 'email' and 'sub' are available in id_token_claims
            email = user_info.get("email")
            name = user_info.get("name") or ""
        else:
            token = await oauth[provider].authorize_access_token(request)
            if provider == "google":
                user_info = await oauth.google.parse_id_token(request, token)
                email = user_info.get("email")
                name = user_info.get("name") or ""
            elif provider == "facebook":
                user_info_resp = await oauth.facebook.get('me?fields=id,name,email', token=token)
                user_info = user_info_resp.json()
                email = user_info.get("email")
                name = user_info.get("name") or ""

        if not email:
            raise HTTPException(status_code=400, detail="Could not retrieve email from OAuth provider")

        user = await get_or_create_user(db, email, name)

        access_token = create_access_token(data={"email": user.email})

        return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.email, "name": user.name}}

    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error}")
