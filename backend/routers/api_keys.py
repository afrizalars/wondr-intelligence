from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

@router.get("/")
async def get_api_keys(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of API keys for current user"""
    return {"api_keys": [], "message": "API key management coming soon"}