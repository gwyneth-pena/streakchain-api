from db import get_db
from fastapi import APIRouter, Depends, Request
from schemas.habits import HabitCreate
from services.habits import save_habit
from sqlalchemy.orm import Session
from utils.decorators import jwt_required

router = APIRouter(prefix="/habits", tags=["habits"])

@router.post("/create")
@jwt_required
def create_habit(payload: HabitCreate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    payload.user_id = user_id
    habit = save_habit(payload, db)
    return habit
