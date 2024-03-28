from datetime import datetime, timedelta
from .models import UserGames

def current_indian_time():
    time_difference_to_ist = timedelta(hours=5, minutes=30)
    current_utc_time = datetime.utcnow()
    current_time_in_india = current_utc_time + time_difference_to_ist
    current_time = current_time_in_india.strftime('%H:%M:%S')
    current_time = datetime.strptime(current_time, '%H:%M:%S').time()
    return current_time

def current_indian_date():
    time_difference_to_ist = timedelta(hours=5, minutes=30)
    current_utc_time = datetime.utcnow()
    current_time_in_india = current_utc_time + time_difference_to_ist
    current_date_in_india = current_time_in_india.date()
    current_date = current_date_in_india.strftime('%Y-%m-%d')
    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()    
    return current_date

def check_game_expired(game):
    date = current_indian_date()
    time = current_indian_time()
    
    print(type(game.booking_id.date), type(date))
    if game.booking_id.date < date or game.booking_id.date == date and game.booking_id.time < time:
        print('working')
        return True
    else:
        print('else working')
        return False