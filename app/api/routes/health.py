from fastapi import APIRouter

from config.settings import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict:
    """
    Basic application health check.
    """

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
def readiness_check() -> dict:
    """
    Readiness check for dependent services.
    """

    return {
        "status": "ready",
        "database": "configured",
        "rag": "configured",
        "presidio": "configured",
        "fraud_detection": settings.FRAUD_DETECTION_ENABLED,
        "mcp": settings.MCP_ENABLED,
    }