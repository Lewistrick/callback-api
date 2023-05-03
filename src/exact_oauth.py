from fastapi.security import OAuth2AuthorizationCodeBearer

from src.config import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/auth",
    tokenUrl="/api/token",
    refreshUrl=settings.exact_tokenurl,
    scheme_name="Exact OAuth2",
    description="This API uses OAuth2 from Exact Online",
)

expected_oauth_response_keys = {
    "access_token",
    "token_type",
    "expires_in",
    "refresh_token",
}
