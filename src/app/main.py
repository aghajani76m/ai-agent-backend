import time

from fastapi import FastAPI, Depends
from elasticsearch import Elasticsearch

from app.core.config import settings
from app.core.dependencies import get_es_client
from app.db.create_indices import create_indices
from app.api.v1.routers.agents import router as agents_router
from app.api.v1.routers.conversations import router as conv_router
from app.api.v1.routers.files import router as files_router
from app.api.v1.routers.resume import router as resume_router

app = FastAPI(
    title="AI Agent Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/health", tags=["health"])
def health(es: Elasticsearch = Depends(get_es_client)):
    """
    Health check: verifies Elasticsearch connectivity.
    """
    es_info = es.info()
    return {
        "status": "ok",
        "elasticsearch": {
            "cluster_name": es_info["cluster_name"],
            "version": es_info["version"]["number"]
        }
    }

# mount our v1 routers
app.include_router(agents_router, prefix="/api/v1")
app.include_router(conv_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")

@app.on_event("startup")
def on_startup():
    """
    Wait a few seconds for ES to be reachable, then create indices.
    """
    time.sleep(5)
    es = get_es_client()
    create_indices(es)


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=9500, 
        log_level=logging.INFO if os.getenv("RUNNING_MODE")=="deploy" else logging.INFO, 
        workers=2 if os.getenv("RUNNING_MODE")=="deploy" else 1, 
        reload=True if os.getenv("RUNNING_MODE")=="deploy" else True
    )    