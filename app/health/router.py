from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core import deps

router = APIRouter()

@router.get("/health/db")
def health_db(db: Session = Depends(deps.get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "db_connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )
