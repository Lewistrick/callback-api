import requests
import xmltodict
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from loguru import logger

from src.config import settings
from src.routes.api import get_auth_headers

router = APIRouter(prefix="/api/exact", tags=["Exact"])


@router.get("/division")
async def division(auth_headers: str = Depends(get_auth_headers)) -> int:
    logger.debug("Requesting division")
    div_url = settings.exact_apiurl + "/Me?$select=UserID,CurrentDivision,UserName"
    token = auth_headers["access_token"]
    headers = {"authorization": f"Bearer {token}"}

    resp = requests.get(div_url, headers=headers)

    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.content)

    parsed_resp = xmltodict.parse(resp.text)
    division_number = (
        parsed_resp.get("feed")
        .get("entry")
        .get("content")
        .get("m:properties")
        .get("d:CurrentDivision")
        .get("#text")
    )

    div_id = int(division_number)

    return div_id
