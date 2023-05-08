from urllib.parse import urlencode

from fastapi import APIRouter, Depends, FastAPI, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from src.auth import get_auth_headers, get_token_dict
from src.config import settings

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/")
async def home(req: Request):
    return {
        "message": "go to one of these URLs:",
        "URLs": [router.url_path_for(endpoint) for endpoint in ("contact", "privacy")],
    }


@router.get("/auth")
async def authorize(req: Request, state: str = "-"):
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
            detail="param 'state' not given",
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
async def token(req: Request, resp: Response, token_dict=Depends(get_auth_headers)):
    token_dict: dict[str, str] = get_token_dict(req.cookies, set_cookie=resp.set_cookie)
    return JSONResponse(content=token_dict)
