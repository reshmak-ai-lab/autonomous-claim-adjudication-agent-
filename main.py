#from fastapi import FastAPI

from config.settings import settings

from app.api.routes.claims import router as claims_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.policies import router as policies_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Autonomous Claim Adjudication & "
        "Fraud Detection Agent"
    ),
)


app.include_router(health_router)
app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(policies_router)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }