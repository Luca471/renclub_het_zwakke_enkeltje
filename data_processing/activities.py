# data_processing/activities.py

import json
import pandas as pd

from utils.name_utils import process_names

# Constants for keys
ATHLETE_ID = 'athlete_id'
ATHLETE_DATA = 'data'
FIRST_NAME = 'firstname'
PROFILE_PIC = 'profile'
DISTANCE = 'distance'
ELAPSED_TIME = 'elapsed_time'
START_DATE = 'start_date_local'

def pace_from_distance_time(distance_meters, time_seconds):
    """
    Calculate the pace in minutes and seconds per kilometer.
    
    Parameters:
    distance_meters (float): Distance in meters.
    time_seconds (float): Time in seconds.
    
    Returns:
    str: Pace in minutes and seconds format (min:sec).
    """
    # Convert distance to kilometers
    distance_km = distance_meters / 1000
    
    # Convert time to minutes
    time_minutes = time_seconds / 60
    
    # Calculate pace in minutes per kilometer
    pace_min = time_minutes / distance_km
    
    # Separate into minutes and seconds
    minutes = int(pace_min)
    seconds = (pace_min - minutes) * 60
    
    return f"{minutes}:{int(seconds):02d} /km"

def format_time(seconds):
    """
    Format a number of seconds into a human-readable string.
    
    Parameters:
    seconds (int): The total number of seconds to format.

    Returns:
    str: A formatted string representing hours and minutes or minutes and seconds.
    """
    if seconds < 0:
        return "Invalid time"  # Handle negative input

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours}u {minutes}m"  # Hour format
    else:
        return f"{minutes}m {remaining_seconds}s"  # Minutes format

def process_activities(athlete_data, activity_data, EXCLUDE_IDS):
    """
    Process athlete and activity data to calculate total kilometers, number of activities,
    and the date of the last activity for each athlete.

    Parameters:
    athlete_data (list of dict): A list of dictionaries containing athlete information.
                                  Each dictionary should include 'athlete_id' and 'data'
                                  (which contains the athlete's first name and profile picture).
    activity_data (list of dict): A list of dictionaries containing activity information.
                                   Each dictionary should include 'data' with details like 
                                   distance, start date, and athlete ID.

    Returns:
    pd.DataFrame: A DataFrame containing the processed activity data for athletes, 
                  including profile picture, athlete name, activity name, date, 
                  distance in kilometers, and elapsed time.
    """
    
    # Extract athlete information into a dictionary
    athlete_names = process_names(athlete_data)

    athletes = {
        athlete[ATHLETE_ID]: {
            'Profile_pic': json.loads(athlete[ATHLETE_DATA]).get(PROFILE_PIC),
            'Atleet': athlete_names.get(athlete[ATHLETE_ID]),
        }
        for athlete in athlete_data if athlete.get(ATHLETE_ID) not in EXCLUDE_IDS
    }

    activities = []
    for activity in activity_data:
        data = json.loads(activity['data'])

        if data.get('type') == 'Run':
        
            athlete_id = data.get('athlete', {}).get('id')
            athlete_info = athletes.get(athlete_id)
            
            # Skip activity if athlete info is not found
            if not athlete_info:
                continue

            activities.append({
                'Profile_pic': athlete_info['Profile_pic'],
                'Atleet': athlete_info['Atleet'],
                'KM': data.get(DISTANCE),
                'Tempo': pace_from_distance_time(data.get(DISTANCE), data.get(ELAPSED_TIME)),
                'Tijd': format_time(data.get(ELAPSED_TIME)),
                'Datum': data.get(START_DATE),
                'Activiteit': data.get('name'),
            })

    # Create DataFrame from activities
    df = pd.DataFrame(activities)

    # Sort by 'Datum' in descending order
    df = df.sort_values(by='Datum', ascending=False)

    # Convert distance from meters to kilometers and round
    df['KM'] = df['KM'].apply(lambda x: round(x / 1000, 1) if x is not None else 0)

    # Reset the index to start from 1
    df.reset_index(drop=True, inplace=True)
    df.index += 1

    return df
