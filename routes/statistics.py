from services.statistics import get_completion_rates, get_habit_with_max_streak, get_total_logs
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
    return {
        "habit_with_max_streak": get_habit_with_max_streak(user_id, start_date, end_date, db),
        "total_logs": get_total_logs(user_id, start_date, end_date, db),
        "completion_rates": get_completion_rates(user_id, start_date, end_date, db)
    }
