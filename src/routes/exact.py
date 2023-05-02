import requests
from fastapi import APIRouter, Header
from fastapi.exceptions import HTTPException
from rich import inspect

from src.config import settings
from src.routes import api

router = APIRouter(prefix="/api/exact", tags=["Exact endpoints"])


@router.get("/projects")
async def get_projects(creds: tuple[str, str] = Header(None)):
    if all(api.EXACT_AUTH):
        creds = api.EXACT_AUTH
    elif not creds:
        raise HTTPException(
            status_code=400,
            detail="Token niet gevonden. Zet in de header of doe GET /api/auth",
        )

    _, token = creds
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(settings.exact_apiurl + "/projects", headers=headers)
    inspect(resp)
    return resp.json()
