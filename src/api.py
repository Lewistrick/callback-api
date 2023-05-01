from urllib.parse import parse_qs

import requests
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from src.config import settings

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/")
async def home(req: Request):
    return {
        "message": "go to one of these URLs:",
        "URLs": [router.url_path_for(endpoint) for endpoint in ("contact", "privacy")],
    }


@router.get("/callback")
async def callback(req: Request):
    return JSONResponse(dict(req.query_params))


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


@router.get("/auth")
async def auth(req: Request):
    logger.debug(f"Trying to authenticate on {settings.exact_authurl}")
    resp = requests.get(
        settings.exact_authurl,
        params={
            "client_id": settings.exact_client_id,
            "redirect_uri": router.url_path_for("callback"),
            "response_type": "code",
            "force_login": "0",
        },
    )
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    logger.debug(f"Response:\n{resp.text}")

    return HTMLResponse(resp.content)


@router.post("/auth")
async def post_auth(req: Request):
    result: bytes = await req.body()
    params = parse_qs(result)

    # params is a {bytes: list[bytes]} mapping with two elements
    # - a user (the username specified)
    # - a verification token

    return params
