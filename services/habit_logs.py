from sqlalchemy.exc import IntegrityError
from sqlalchemy import exists
from sqlalchemy.orm import Session
from models.habit_logs import HabitLog
from models.habits import Habit
from schemas.habit_logs import HabitLogCreate
from utils.shared import validation_error 

def save_habit_log(payload: HabitLogCreate, db: Session):
    habit_exists = (
        db.query((
            exists().where(Habit.id == payload.habit_id, Habit.user_id == payload.user_id)
        ))
        .scalar()
    )

    if habit_exists is False:
        validation_error("habit", "Habit not found.", "habit", 404)


    habit_log = HabitLog(habit_id=payload.habit_id, 
                         log_date=payload.log_date
                        )
    
    db.add(habit_log)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        validation_error(
            "habit_log",
            f"Habit log for {payload.log_date} already exists.",
            "habit_log",
            400
        )

    db.refresh(habit_log)

    return habit_log


def remove_habit_log(habit_log_id: int, user_id: int, db: Session):
    habit_log = (db.query(HabitLog)
                    .join(Habit)
                    .filter(HabitLog.id == habit_log_id, Habit.user_id == user_id)
                    .first()
                )

    if habit_log is None:
        validation_error("habit_log", "Habit log not found.", "habit_log", 404)

    db.delete(habit_log)
    db.commit()

    return True