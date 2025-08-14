from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/merchants", tags=["Merchants"])

@router.get("/")
async def get_merchants(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of merchants"""
    return {"merchants": [], "message": "Merchant management coming soon"}