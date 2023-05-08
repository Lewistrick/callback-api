import fastapi
import uvicorn
from beanie import init_beanie
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import api, exact
from src.schemas.user import User
from src.usersdb import auth_backend, fastapi_users, google_oauth_client, user_db

app = fastapi.FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
    exclude=["set_cookie"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(exact.router)

# The routes below are used for Google auth. Note that the register router is NOT
# included because there will be a very small curated list of users that may use this.
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_oauth_router(
        oauth_client=google_oauth_client,
        backend=auth_backend,
        state_secret=settings.google_oauth_client_secret,
    ),
    prefix="/auth/google",
    tags=["Auth"],
)


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=user_db,
        document_models=[User],
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.internal_url,
        port=settings.internal_port,
        reload=True,
    )
