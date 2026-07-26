from schemas.habits import HabitGet
from sqlalchemy.orm import Session
from models.habit_logs import HabitLog
from models.habits import Habit
from datetime import date, timedelta
from services.habits import get_habits_by_user_id

def get_statistics(user_id: int, start_date: date, end_date: date, db: Session):
    payload = HabitGet(log_start_date=start_date, log_end_date=end_date, user_id=user_id)
    habits = get_habits_by_user_id(payload, user_id, db)

    # Date range setup
    all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    # Tracking variables
    max_streak = 0
    max_streak_habits = []
    init_max_streak_habits = []
    total_logs = 0
    total_frequency = 0
    totals_per_habit = {}

    for habit in habits:
        # 1. Total logs calculation
        logs_count = len(habit.logs)
        total_logs += logs_count
        total_frequency += habit.frequency

        # 2. Completion rate per habit calculation
        if habit.frequency > 0:
            percentage_per_habit = logs_count / habit.frequency
            totals_per_habit[habit.name] = round(percentage_per_habit * 100, 2)
        else:
            totals_per_habit[habit.name] = 0.0

        # 3. Max consecutive streaks calculation
        streaks = 0
        habit.logs.sort(key=lambda x: x.log_date)
        for i in range(1, len(all_dates)):
            if habit.logs[i].log_date == all_dates[i]:
                streaks += 1
            else:
                break
        
        if streaks > max_streak:
            max_streak = streaks

        init_max_streak_habits.append({
            "habit_name": habit.name,
            "streaks": streaks
        })
        

    max_streak_habits = [habit["habit_name"] for habit in init_max_streak_habits if habit["streaks"] == max_streak]
    # Total completion percentage calculation
    total_percentage = round((total_logs / total_frequency) * 100, 2) if total_frequency > 0 else 0.0

    return {
        "habit_with_max_streak": {
            "habit_with_max_streak": ', '.join(max_streak_habits) if max_streak_habits else None,
            "max_streak": max_streak
        },
        "total_logs": total_logs,
        "completion_rates": {
            "percentages_per_habit": totals_per_habit,
            "total_percentage": total_percentage,
        }
    }