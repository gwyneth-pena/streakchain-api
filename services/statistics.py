from schemas.habits import HabitGet
from sqlalchemy.orm import Session
from models.habit_logs import HabitLog
from models.habits import Habit
from datetime import date, timedelta
from services.habits import get_habits_by_user_id

def get_habit_with_max_streak(user_id: int, start_date: date, end_date: date, db: Session):
    payload = HabitGet(log_start_date=start_date, log_end_date=end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload,user_id, db)

    max_streak = 0
    max_streak_habit = None

    all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    for habit in habits:
        streaks = 0

        for log in habit.logs:
            if log.log_date in all_dates:
                streaks += 1
            else:
                break
        
        if streaks > max_streak:
            max_streak = streaks
            max_streak_habit = habit.name
    
    return {
        'habit_with_max_streak': max_streak_habit,
        'max_streak': max_streak
    }


def get_total_logs(user_id: int, start_date: date, end_date: date, db: Session):
    payload = HabitGet(log_start_date=start_date, log_end_date=end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload,user_id, db)

    total_logs = 0

    for habit in habits:
        total_logs += len(habit.logs)
    
    return total_logs


def get_completion_rates(user_id: int, start_date: date, end_date: date, db: Session):
    payload = HabitGet(log_start_date=start_date, log_end_date=end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload,user_id, db)

    totals_per_habit = {}

    total_logs = get_total_logs(user_id, start_date, end_date, db)
    total_frequency = 0
    total_percentage = 0

    for habit in habits:
        total_logs_in_habit = len(habit.logs)
        percentage_per_habit = total_logs_in_habit / habit.frequency
        totals_per_habit[habit.name] = round(percentage_per_habit * 100, 2)

        total_frequency += habit.frequency

    total_percentage = round(total_logs / total_frequency * 100, 2)

    return {
        'percentages_per_habit': totals_per_habit,
        'total_percentage': total_percentage,
    }
