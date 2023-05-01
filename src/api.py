import os
from urllib.parse import quote_plus

import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/")
def home(req: Request):
    return {
        "message": "go to one of these URLs:",
        "URLs": [router.url_path_for(endpoint) for endpoint in ("contact", "privacy")],
    }


@router.get("/callback")
def callback(req: Request):
    return JSONResponse(dict(req.query_params))


@router.get("/contact")
def contact(req: Request):
    return {"developer": "e.wilts@ncim.nl"}


@router.get("/privacy")
def privacy(req: Request):
    return JSONResponse(
        {
            "data collected": "none",
            "data collection method": "contract scraping",
            "app purpose": "decrease manual data entry",
            "data retention/deletion": "see your contract",
            "method to revoke": "see /contact",
        }
    )


@router.get("/testauth")
def testauth(req: Request):
    authurl = os.getenv("EXACT_APIURL") + "/oauth2/auth"
    params = {
        "client_id": os.getenv("EXACT_CLIENT_ID"),
        "redirect_uri": router.url_path_for("callback"),
        "response_type": "token",
        "force_login": "1",
    }

    req_url = authurl + "?"
    for k, v in params.items():
        print(f"quoting {v}")
        qv = quote_plus(v)
        print(f"result: {qv}")
        req_url += f"{k}={qv}&"

    req_url = req_url[:-1]  # remove the last ampersand
    print(req_url)

    resp = requests.get(req_url)
    print(resp.text)
    return resp.text
