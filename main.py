import os
from urllib.parse import quote_plus

import fastapi
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger

app = fastapi.FastAPI()

load_dotenv()


@app.get("/")
def home(req: Request):
    return {"message": "go to /contact or /privacy to read more"}


@app.get("/callback")
def callback(req: Request):
    return JSONResponse(dict(req.query_params))


@app.get("/contact")
def contact(req: Request):
    return {
        "contact": "s.coufreur@ncim.nl",
        "developer": "e.wilts@ncim.nl",
    }


@app.get("/privacy")
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


@app.get("/testauth")
def testauth(req: Request):
    authurl = os.getenv("EXACT_APIURL") + "/oauth2/auth"
    params = {
        "client_id": os.getenv("EXACT_CLIENT_ID"),
        "redirect_uri": "https://localhost/callback",
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


if __name__ == "__main__":
    logger.debug(f"Environment: {os.environ}")
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE"),
        reload=True,
    )
