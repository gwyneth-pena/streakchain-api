from fastapi import APIRouter, Depends, Request
from db import get_db
from sqlalchemy.orm import Session
from schemas.habit_logs import HabitLogCreate
from services.habit_logs import get_logs_per_year, prepare_yearly_streaks_for_xlsx, remove_habit_log, save_habit_log
from services.habits import get_habits_with_streaks
from utils.decorators import jwt_required
from utils.shared import generate_xlsx, validation_error


router = APIRouter(prefix="/habit-logs", tags=["habit-logs"])


@router.get('/{year}')
@jwt_required
def get_habit_logs_per_year(year: int, request: Request, session: Session = Depends(get_db)):
    user_id = request.state.user_id
    logs = get_logs_per_year(year, user_id, session)

    return logs


@router.get('/download-yearly-streaks/{year}')
@jwt_required
def download_yearly_streaks(year: int, request: Request, session: Session = Depends(get_db)):
    user_id = request.state.user_id
    if not (1 <= year <= 9999):
        validation_error("year", "Invalid year.", "year", status=400)

    habits = get_habits_with_streaks(user_id, None, None, session)
    logs = get_logs_per_year(year, user_id, session)
    csv_data = prepare_yearly_streaks_for_xlsx(habits, logs, year)
    return generate_xlsx(csv_data, f"habits_yearly_streaks_{str(year).zfill(4)}")


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