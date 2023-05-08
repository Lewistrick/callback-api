from datetime import datetime, timedelta
from typing import Any, Callable

import requests
from fastapi import Request, Response, status
from fastapi.exceptions import HTTPException
from loguru import logger

from src.config import settings
from src.exact_oauth import expected_oauth_response_keys


def get_auth_headers(req: Request, resp: Response):
    logger.debug("Getting authentication headers as dictionary...")
    return get_token_dict(req.cookies, set_cookie=resp.set_cookie)


def get_token_dict(
    cookies: dict[str, Any],
    set_cookie: Callable[[str, Any], None],
) -> dict[str, str]:
    """Get the Exact token as a dictionary.

    Args:
        cookies: a dictionary that may or may not contain the following keys:
            - exact_access_token: an access token (may or may not be expired)
            - exact_token_expiry: when the token expires (#seconds after 1970-01-01)
            - exact_refresh_token: a token to refresh the access token on expiry
        set_cookie: a function that takes 'key' and 'value' arguments
            and sets the cookie `key` to `value`

    Returns a dictionary with these keys:
        access_token: the access token (use it in the auth header for Exact endpoints)
        token_type: the token type (always 'Bearer')
        expires_in: the amount of seconds after issuance when the token expires
        refresh_token: the code to use to refresh an expired access token
    """
    # Check if a non-expired access token exists
    access_token = cookies.get("exact_access_token")
    refresh_token = cookies.get("exact_refresh_token")
    token_expiry = cookies.get("exact_token_expiry", 0)
    if (
        access_token
        and refresh_token
        and float(token_expiry) > datetime.utcnow().timestamp()
    ):
        logger.success("Found unexpired access token")
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": token_expiry,
            "refresh_token": refresh_token,
        }

    # Prepare data for requesting an access token
    data = {
        "client_id": settings.exact_client_id,
        "client_secret": settings.exact_client_secret,
    }

    # If an access token exists and is expired, request a new token
    if access_token and refresh_token:
        logger.debug("Requesting new access token by *refresh token*")
        data["refresh_token"] = refresh_token
        data["grant_type"] = "refresh_token"

    # Otherwise, this is the first time a token will be requested
    else:
        logger.debug("Creating access token *from code*")
        auth_code = cookies.get("exact_auth_code")
        if not auth_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="First, go to /api/auth to login and get an authorization code.",
            )
        data["redirect_uri"] = settings.exact_redirect_url
        data["code"] = auth_code
        data["grant_type"] = "authorization_code"

    # Perform the request
    exact_resp = requests.post(settings.exact_tokenurl, data=data)
    new_data = exact_resp.json()

    # Sometimes, a request for a new access token using the refresh token fails.
    # In that case, 'delete' the refresh token (just from the temp dict) and try again
    if not exact_resp.ok and data["grant_type"] == "refresh_token":
        del cookies["exact_refresh_token"]
        logger.warning("Retrying because refresh token was invalid")
        return get_token_dict(cookies=cookies, set_cookie=set_cookie)

    raise_for_unexpected_response(exact_resp, new_data)

    if set_cookie:
        # Set the cookies to the values from the response
        access_token = new_data.get("access_token")
        expires_in = float(new_data.get("expires_in", 0))
        expiry = (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
        set_cookie(key="exact_access_token", value=access_token)
        set_cookie(key="exact_token_expiry", value=expiry)
        set_cookie(key="exact_refresh_token", value=new_data.get("refresh_token"))

    return new_data


def raise_for_unexpected_response(resp: requests.Response, data: dict[str, str]):
    if not resp.ok:
        scode = resp.status_code
        etext = resp.text
        logger.error(f"Could not request OAuth2 token: ({scode} - {etext})")
        raise HTTPException(
            status_code=scode,
            detail=f"Unexpected --> could not request OAuth2 token: {etext}",
        )

    # Check the response
    if any(k not in data for k in expected_oauth_response_keys):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unexpected response from Exact!"
                f"\n - Expected keys: {expected_oauth_response_keys}"
                f"\n - Received keys: {set(data.keys())}"
            ),
        )
