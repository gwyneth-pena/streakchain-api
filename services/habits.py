

from sqlalchemy import and_, func
from models.habit_logs import HabitLog
from models.habits import Habit
from schemas.habits import HabitCreate, HabitGet, HabitUpdate
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from utils.shared import validation_error


def save_habit(payload: HabitCreate, db: Session):
    habit = Habit(**payload.model_dump(exclude_unset=True))
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def get_habits_by_user_id(payload: HabitGet, user_id: int, db: Session):
    options = []

    filters = []

    if payload.start_date and payload.end_date:
        filters.append(func.date(HabitLog.created_at) >= payload.start_date)
        filters.append(func.date(HabitLog.created_at) <= payload.end_date)
        options.append(
            selectinload(Habit.logs)
        )

    
    if len(filters) > 0:
        options.append(
            with_loader_criteria(
                HabitLog,
                and_(*filters),
                include_aliases=True
            )
        )

    habits = (db.query(Habit).options(*options)
                .filter(Habit.user_id == user_id)
                .order_by(Habit.created_at.asc())
                .all()
            )
    
    return habits


def patch_habit(payload: HabitUpdate, db: Session):
    habit = db.query(Habit).filter(Habit.id == payload.id, Habit.user_id == payload.user_id).first()

    if habit is None:
        validation_error("habit", "Habit not found.", "habit", 404)
    
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)

    return habit


def remove_habit(id: int, user_id: int, db: Session):
    habit = db.query(Habit).filter(Habit.id == id, Habit.user_id == user_id).first()

    if habit is None:
        validation_error("habit", "Habit not found.", "habit", 404)

    db.delete(habit)
    db.commit()

    return True
