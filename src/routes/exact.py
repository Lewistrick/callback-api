import requests
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from src.config import settings
from src.routes.api import get_token_dict

router = APIRouter(prefix="/api/exact", tags=["Exact endpoints"])


@router.get("/division")
async def division(token: str = Depends(get_token_dict)):
    div_url = settings.exact_apiurl + "/Me?$select=CurrentDivision"
    headers = {"authorization": f"Bearer {token}"}

    resp = requests.get(div_url, headers=headers)

    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.content)

    return resp.json()
