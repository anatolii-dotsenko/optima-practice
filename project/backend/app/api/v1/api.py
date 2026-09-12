"""API v1 router composition."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, menu, orders

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(menu.router, prefix="/menu", tags=["Menu & Catalog"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders & Pre-orders"])
