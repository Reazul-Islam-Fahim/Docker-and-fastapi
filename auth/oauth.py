from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from models.users.users import Users
from auth.security import hash_password
from sqlalchemy import select

oauth = OAuth()

# Google OAuth Config
oauth.register(
    name='google',
    client_id='388066712413-jomsaokksgn0152vr081kqqm9flsim9p.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

# Facebook OAuth Config
oauth.register(
    name='facebook',
    client_id='FACEBOOK_CLIENT_ID',
    client_secret='FACEBOOK_CLIENT_SECRET',
    access_token_url='https://graph.facebook.com/v9.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v9.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v9.0/',
    userinfo_endpoint='https://graph.facebook.com/me?fields=id,name,email',
    client_kwargs={'scope': 'email'},
)

# Apple OAuth Config
# Apple’s OAuth is a bit more complex (JWT client secret needed)
oauth.register(
    name='apple',
    client_id='APPLE_CLIENT_ID',
    client_secret='APPLE_CLIENT_SECRET',  # For Apple, usually a JWT; see below for more info
    authorize_url='https://appleid.apple.com/auth/authorize',
    access_token_url='https://appleid.apple.com/auth/token',
    api_base_url='https://appleid.apple.com',
    client_kwargs={'scope': 'name email', 'response_mode': 'form_post', 'response_type': 'code id_token'},
)

async def get_or_create_user(db: AsyncSession, email: str, name: str = "") -> Users:
    result = await db.execute(select(Users).where(Users.email == email))
    user = result.scalar_one_or_none()
    if not user:
        user = Users(
            name=name,
            email=email,
            password=hash_password("oauth_dummy_password"),
            is_verified=True,
            role="user",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


