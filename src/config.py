from pydantic import BaseSettings


class Settings(BaseSettings):
    # This is where the app runs
    internal_url: str = "0.0.0.0"
    internal_port: int = 8000

    # App settings.
    cors_allow_origins: list[str] = ["localhost:8000", "https://start.exactonline.nl"]

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


settings = Settings()
