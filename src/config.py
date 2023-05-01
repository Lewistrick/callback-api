from pydantic import BaseSettings


class Settings(BaseSettings):
    # This is where the app runs
    internal_url: str = "0.0.0.0"
    internal_port: int = 8000

    # Exact credentials
    exact_apiurl: str = "https://start.exactonline.nl/api/v1/current"
    exact_app_name: str
    exact_redirect_url: str
    exact_client_id: str
    exact_webhook_secret: str
    exact_client_secret: str


settings = Settings()
