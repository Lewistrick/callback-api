from urllib.parse import parse_qs

import requests
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from src.config import settings

router = APIRouter(prefix="/api", tags=["API"])

# Global variable to store the username and password (token)
EXACT_AUTH = ("", "")


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

    # Show the HTML with the login form; this does a POST request to this function
    return HTMLResponse(resp.content)


@router.post("/auth")
async def auth_post(req: Request):
    result: bytes = await req.body()
    logger.info(result.decode())
    params = parse_qs(result.decode())

    # params is a {str: list[str]} mapping with two elements
    # - 'UserNameField' (the username/email specified)
    # - '__RequestVerificationToken' (the Exact auth token)
    # both of these have length 1

    username = params["UserNameField"][0]
    password = params["__RequestVerificationToken"][0]

    global EXACT_AUTH
    EXACT_AUTH = (username, password)
    return EXACT_AUTH
