

from datetime import date, timedelta
from typing import Optional
from fastapi import Depends
from sqlalchemy import and_, func
from db import get_db
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

    if payload.log_start_date and payload.log_end_date:
        filters.append(func.date(HabitLog.log_date) >= payload.log_start_date)
        filters.append(func.date(HabitLog.log_date) <= payload.log_end_date)
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


def get_habits_with_streaks(user_id: int, log_start_date: Optional[date], log_end_date: Optional[date], db: Session = Depends(get_db)):
    payload = HabitGet(log_start_date=log_start_date, log_end_date=log_end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload,user_id, db)
    return habits


def prepare_habits_for_xlsx(habits: list, log_start_date: date, log_end_date: date):
    output = []

    d1 = log_start_date
    d2 = log_end_date
    num_days = (d2 - d1).days + 1

    days = [d1 + timedelta(days=x) for x in range(num_days)]

    header = ["Habits"] + [f"{d.day}\n({d.strftime('%a')})" for d in days] + ["Achieved", "Goal"]

    output.append(header)

    for habit in habits:
        log_dates = [log.log_date for log in habit.logs]

        row = [
            habit.name,
            *["★" if d in log_dates else "" for d in days],
            len(log_dates),
            habit.frequency
        ]

        output.append(row)

    return output