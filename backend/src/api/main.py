from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.config.settings import (
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)
from backend.src.utils.logging_config import setup_logging, logger

setup_logging()

app = FastAPI(
    title="Chest X-Ray Abnormality Detection API",
    description="Backend API for image filter processing and disease detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

logger.info("FastAPI application initialized")
logger.info(f"CORS enabled for origins: {CORS_ORIGINS}")


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")


@app.get("/")
async def root():
    return {
        "message": "Chest X-Ray Abnormality Detection API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    from datetime import datetime

    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}


from backend.src.api.routes import filters, detection

app.include_router(filters.router, tags=["Image Filters"])
logger.info("Registered filters router")

app.include_router(detection.router, tags=["Disease Detection"])
logger.info("Registered detection router")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    from backend.src.config.settings import API_HOST, API_PORT, API_RELOAD

    logger.info(f"Starting server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "backend.src.api.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
    )
