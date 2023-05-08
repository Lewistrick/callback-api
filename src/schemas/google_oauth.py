import json
from pathlib import Path

from pydantic import BaseModel


class GoogleOAuthWeb(BaseModel):
    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str


class GoogleOAuth(BaseModel):
    web: GoogleOAuthWeb

    @classmethod
    def from_json(cls, jsonfile: Path):
        with jsonfile.open() as handle:
            data = json.load(handle)
        return cls(**data)
