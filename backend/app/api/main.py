from fastapi import APIRouter

from app.api.routes import generator, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(generator.router, prefix="/generator", tags=["generator"])
