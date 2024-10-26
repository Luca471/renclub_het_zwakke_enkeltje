# utils/time_utils.py

import datetime

def weeks_since(start_year, start_week_number):
    """
    Calculate the number of weeks since a specified year and week number.
    
    Parameters:
    start_year (int): The year to track from.
    start_week_number (int): The week number to track from (ISO week number).
    
    Returns:
    int: The number of weeks since the specified year and week.
    """
    # Get the current date
    current_date = datetime.datetime.now()
    
    # Get the current week number and year
    current_week_number = current_date.isocalendar()[1]
    current_year = current_date.isocalendar()[0]
    
    # Calculate the total weeks since the start year and week
    total_weeks_since = (current_year - start_year) * 52 + (current_week_number - start_week_number)

    # Adjust for cases where the start week is later in the year than the current week
    if current_year == start_year:
        total_weeks_since = current_week_number - start_week_number
    
    return total_weeks_since