from pathlib import Path

from pydantic import BaseSettings

from src.schemas.google_oauth import GoogleOAuth


class Settings(BaseSettings):
    # This is where the app runs
    internal_url: str = "0.0.0.0"
    internal_port: int = 8000

    # App settings.
    cors_allow_origins: list[str] = ["localhost:8000", "https://start.exactonline.nl"]

    # User-auth settings.
    google_oauth_json: Path
    jwt_secret: str
    reset_password_token_secret: str
    verification_token_secret: str

    # Mongo settings. Used for storing users.
    mongo_connection_string: str = "mongodb://localhost:27017"

    # Exact settings. Make sure to match them with what you see in your Exact app.
    exact_authurl: str = "https://start.exactonline.nl/api/oauth2/auth"
    exact_tokenurl: str = "https://start.exactonline.nl/api/oauth2/token"
    exact_apiurl: str = "https://start.exactonline.nl/api/v1/current"
    exact_app_name: str
    exact_redirect_url: str
    exact_client_id: str
    exact_webhook_secret: str
    exact_client_secret: str

    class Config:
        env_file = ".env"

    @property
    def google_oauth_client_id(self):
        google_oauth = self.get_google_oauth
        return google_oauth.web.client_id

    @property
    def google_oauth_client_secret(self):
        google_oauth = self.get_google_oauth
        return google_oauth.web.client_secret

    @property
    def get_google_oauth(self) -> GoogleOAuth:
        return GoogleOAuth.from_json(self.google_oauth_json)


settings = Settings()
