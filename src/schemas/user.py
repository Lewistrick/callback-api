import uuid

from beanie import Document
from fastapi_users import BaseUserManager, schemas
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser
from fastapi_users_db_beanie import ObjectIDIDMixin
from pydantic import Field

from src.config import settings


class OAuthAccount(BaseOAuthAccount):
    """An account that binds a user to an OAuth model, e.g. a Google account.

    OAuthAccount is not a Beanie document but a Pydantic model that we'll embed inside
    the User document, through the oauth_accounts array.
    """

    pass


class User(BeanieBaseUser, Document):
    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)


class UserManager(ObjectIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    # This link provides methods for events, such as successful login or registration:
    # https://fastapi-users.github.io/fastapi-users/11.0/configuration/user-manager/


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
