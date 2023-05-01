import os

import fastapi
import uvicorn
from dotenv import load_dotenv

import src.api as api

app = fastapi.FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")
app.include_router(api.router)

load_dotenv()

if __name__ == "__main__":
    # logger.debug(f"Environment: {os.environ}")
    uvicorn.run(
        "src.main:app",
        host=os.getenv("INTERNAL_HOST"),
        port=int(os.getenv("INTERNAL_PORT")),
    )
