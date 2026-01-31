import calendar
from datetime import date
from typing import Optional
from db import get_db
from fastapi import APIRouter, Depends, Query, Request
from schemas.habits import HabitCreate, HabitUpdate
from services.habits import get_habits_with_streaks, patch_habit, prepare_habits_for_xlsx, remove_habit, save_habit
from sqlalchemy.orm import Session
from utils.decorators import jwt_required
from utils.shared import generate_xlsx, validation_error

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("")
@jwt_required
def create_habit(payload: HabitCreate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    payload.user_id = user_id
    habit = save_habit(payload, db)

    return habit


@router.get('')
@jwt_required
def get_habits(request: Request, db: Session = Depends(get_db), log_start_date: Optional[date] = Query(None), log_end_date: Optional[date] = Query(None)):
    user_id = request.state.user_id
    return get_habits_with_streaks(user_id, log_start_date, log_end_date, db)


@router.get('/download-streaks')
@jwt_required
def download_habits_streaks(request: Request, db: Session = Depends(get_db), month: int = Query(...), year: int = Query(...)):
    user_id = request.state.user_id
    
    if not (1 <= month <= 12):
        validation_error("month", "Invalid month.", "month", status=400)
    if year < 1 or year > 9999:
        validation_error("year", "Invalid year.", "year", status=400)

    log_start_date = date(year, month, 1)
    log_end_date = date(year, month, calendar.monthrange(year, month)[1])
    habits =  get_habits_with_streaks(user_id, log_start_date, log_end_date, db)
    csv_data = prepare_habits_for_xlsx(habits, log_start_date, log_end_date)
    return generate_xlsx(csv_data, f"habits_with_streaks_{str(month).zfill(2)}_{year}")
    

@router.patch('/{habit_id}')
@jwt_required
def update_habit(habit_id: int, payload: HabitUpdate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    payload.user_id = user_id
    payload.id = habit_id
    habit = patch_habit(payload, db)

    return habit


@router.delete('/{habit_id}')
@jwt_required
def delete_habit(habit_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    if not user_id:
        validation_error("jwt", "JWT cookie not found.", "jwt", 401)

    res = remove_habit(habit_id, user_id, db)

    if not res:
        validation_error("habit", "Habit not found.", "habit", 404)

    return {"message": "Habit deleted successfully."}