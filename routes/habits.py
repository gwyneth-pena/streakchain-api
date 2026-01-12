from datetime import date
from typing import Optional
from db import get_db
from fastapi import APIRouter, Depends, Query, Request
from schemas.habits import HabitCreate, HabitGet, HabitUpdate
from services.habits import get_habits_by_user_id, patch_habit, remove_habit, save_habit
from sqlalchemy.orm import Session
from utils.decorators import jwt_required
from utils.shared import validation_error

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
def get_habits(request: Request, db: Session = Depends(get_db), start_date: Optional[date] = Query(None), end_date: Optional[date] = Query(None)):
    user_id = request.state.user_id
    payload = HabitGet(start_date=start_date, end_date=end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload,user_id, db)

    return habits


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