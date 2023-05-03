from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from src.config import settings
from src.exact_oauth import expected_oauth_response_keys

router = APIRouter(prefix="/api", tags=["API"])
creds = {}  # store credentials here


@router.get("/")
async def home(req: Request):
    return {
        "message": "go to one of these URLs:",
        "URLs": [router.url_path_for(endpoint) for endpoint in ("contact", "privacy")],
    }


@router.get("/auth")
async def authorize(req: Request):
    params = {
        "client_id": settings.exact_client_id,
        "redirect_uri": settings.exact_redirect_url,
        "response_type": "code",
        "force_login": "0",
    }

    app: FastAPI = req.app
    app_state = req.query_params.get("state")
    if app_state:
        app.state._state["app_state"] = app_state
    else:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            details="param 'state' not given",
        )

    for k, v in req.query_params.items():
        if k not in params:
            params[k] = v

    auth_url = f"{settings.exact_authurl}?{urlencode(params)}"
    logger.debug(f"Redirecting to Exact for auth: {settings.exact_authurl}")
    logger.debug(f"Exact auth URL params: {params}")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(resp: Response, req: Request):
    req_state = req.query_params.get("state")
    app: FastAPI = req.app
    app_state = app.state._state.get("app_state")

    if not app_state:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "App is stateless!",
        )

    if not req_state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request has no state!",
        )

    if req_state != app_state:
        logger.warning(f"Wrong request state: {req_state}")
        logger.warning(f"{app_state=}")
        breakpoint()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Couldn't verify app state!",
        )

    code = req.query_params.get("code")
    resp.set_cookie(key="exact_auth_code", value=code)
    return {"message": "exact_auth_code set in cookie"}


@router.get("/contact")
async def contact(req: Request):
    return {"developer": "e.wilts@ncim.nl"}


@router.get("/privacy")
async def privacy(req: Request):
    return JSONResponse(
        {
            "data collected": "none",
            "data collection method": "contract scraping",
            "app purpose": "decrease manual data entry",
            "data retention/deletion": "see your contract",
            "method to revoke": "see /contact",
        }
    )


@router.get("/test")
async def test(req: Request):
    logger.info("Got here!")
    response_dict = dict(req.query_params)
    logger.debug(f"Got response! {response_dict}")
    return JSONResponse(response_dict)


@router.post("/token")
async def token(req: Request, resp: Response):
    # Check if a non-expired access token exists
    access_token = req.cookies.get("exact_access_token")
    token_expiry = req.cookies.get("exact_token_expiry", 0)
    if access_token and float(token_expiry) > datetime.utcnow().timestamp():
        return JSONResponse(content={"token": access_token})

    # Prepare data for requesting an access token
    data = {
        "client_id": settings.exact_client_id,
        "client_secret": settings.exact_client_secret,
        "redirect_uri": settings.exact_redirect_url,
    }

    # If an access token exists and is expired, request a new token
    if access_token and (refresh_token := req.cookies.get("exact_refresh_token")):
        data["code"] = refresh_token
        data["grant_type"] = "refresh_token"

    # Otherwise, this is the first time a token will be requested
    else:
        data["code"] = req.cookies.get("exact_auth_code")
        data["grant_type"] = "authorization_code"

    exact_resp = requests.post(settings.exact_tokenurl, data=data)

    if not exact_resp.ok:
        scode = exact_resp.status_code
        etext = exact_resp.text
        logger.error(f"Could not request OAuth2 token: ({scode} - {etext})")
        raise HTTPException(
            status_code=scode,
            detail=f"Could not request OAuth2 token: {etext}",
        )

    new_data: dict[str, str] = exact_resp.json()
    if any(k not in new_data for k in expected_oauth_response_keys):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unexpected response from Exact!"
                f"\n - Expected keys: {expected_oauth_response_keys}"
                f"\n - Received keys: {set(new_data.keys())}"
            ),
        )

    # Set the cookies to the values from the response
    access_token = new_data.get("access_token")
    expires_in = float(new_data.get("expires_in", 0))
    expiry = (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
    resp.set_cookie(key="exact_access_token", value=access_token)
    resp.set_cookie(key="exact_token_expiry", value=expiry)
    resp.set_cookie(kye="exact_refresh_token", value=new_data.get("refresh_token"))

    return JSONResponse(content={"token": access_token})
