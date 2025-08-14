from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/")
async def get_documents(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of global documents"""
    return {"documents": [], "message": "Document management coming soon"}

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new document"""
    return {"message": "Document upload coming soon", "filename": file.filename}