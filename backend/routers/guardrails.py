from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/guardrails", tags=["Guardrails"])

@router.get("/")
async def get_guardrails(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of guardrails"""
    return {"guardrails": [], "message": "Guardrails management coming soon"}