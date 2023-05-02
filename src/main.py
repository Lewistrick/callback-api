import fastapi
import uvicorn
from dotenv import load_dotenv

from src.config import settings
from src.routes import api, exact

app = fastapi.FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")
app.include_router(api.router)
app.include_router(exact.router)

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.internal_url,
        port=settings.internal_port,
        reload=True,
    )
