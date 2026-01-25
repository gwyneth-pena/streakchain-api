from collections import defaultdict
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Date, Integer, cast, exists, func
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


def get_logs_per_year(year: int,user_id: int, db: Session):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    logs = ( 
        db.query( 
            Habit.id.label('habit_id'),
            Habit.name.label('habit_name'),
            func.cast(func.extract("month", HabitLog.log_date), Integer).label('month'),
            func.count(HabitLog.id).label('logs_count'),
            Habit.frequency.label('habit_frequency')
        )
        .join(HabitLog.habit)
        .filter(
            Habit.user_id == user_id,
            HabitLog.log_date >= start_date,
            HabitLog.log_date <= end_date
        )
        .group_by(
            Habit.id,
            Habit.name,
            func.cast(func.extract("month", HabitLog.log_date), Integer),
            Habit.frequency
        )
        .all()
    )

    result = defaultdict(dict)

    for log in logs:
        result[log.month][log.habit_id] = {
            'habit_name': log.habit_name,
            'logs_count': log.logs_count,
            'habit_frequency': log.habit_frequency
        }

    result = dict(result)
    
    return result