from services.statistics import get_statistics as get_stats
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Request
from db import get_db
from datetime import date
from utils.decorators import jwt_required

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get('')
@jwt_required
def get_statistics( start_date: date, end_date: date, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    return get_stats(user_id, start_date, end_date, db)