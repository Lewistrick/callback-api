import uuid

import motor.motor_asyncio
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase
from httpx_oauth.clients.google import GoogleOAuth2

from src.config import settings
from src.schemas.user import User, UserManager

client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_connection_string)
user_db = client["users"]

google_oauth_client = GoogleOAuth2(
    client_id=settings.google_oauth_client_id,
    client_secret=settings.google_oauth_client_secret,
)


async def get_user_db():
    yield BeanieUserDatabase(User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.jwt_secret, lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="api/jwt-login")

auth_backend = AuthenticationBackend(
    name="google_oauth",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
