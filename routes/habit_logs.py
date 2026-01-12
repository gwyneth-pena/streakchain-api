from fastapi import APIRouter, Depends, Request
from db import get_db
from sqlalchemy.orm import Session
from schemas.habit_logs import HabitLogCreate
from services.habit_logs import remove_habit_log, save_habit_log
from utils.decorators import jwt_required
from utils.shared import validation_error


router = APIRouter(prefix="/habit-logs", tags=["habit-logs"])


@router.post("")
@jwt_required
def create_habit_log(payload: HabitLogCreate, request: Request, session: Session = Depends(get_db)):
    payload.user_id = request.state.user_id
    habit_log = save_habit_log(payload, session)

    return habit_log


@router.delete('/{habit_log_id}')
@jwt_required
def delete_habit_log(habit_log_id: int, request: Request, session: Session = Depends(get_db)):
    user_id = request.state.user_id
    
    res = remove_habit_log(habit_log_id, user_id, session)

    if not res:
        validation_error("habit_log", "Habit log not found.", "habit_log", 404)

    return {"message": "Habit log deleted successfully."}