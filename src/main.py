import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import api, exact

app = fastapi.FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
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

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.internal_url,
        port=settings.internal_port,
        reload=True,
    )
