# data_processing/best_efforts.py

import json
import pandas as pd
import datetime

from utils.name_utils import process_names

# Constants for keys
ATHLETE_ID = 'athlete_id'
ATHLETE_DATA = 'data'
FIRST_NAME = 'firstname'
PROFILE_PIC = 'profile'
DISTANCE = 'distance'
ELAPSED_TIME = 'elapsed_time'
START_DATE = 'start_date_local'
BEST_EFFORTS = 'best_efforts'

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

def process_best_efforts(athlete_data, activity_data):
    """
    Process athlete and activity data to calculate best efforts for each athlete
    from the 'best_efforts' field in the activity data and return only the fastest segment
    per athlete for each segment.

    Parameters:
    athlete_data (list of dict): A list of dictionaries containing athlete information.
                                  Each dictionary should include 'athlete_id' and 'data'
                                  (which contains the athlete's first name and profile picture).
    activity_data (list of dict): A list of dictionaries containing activity information.
                                   Each dictionary should include 'data' with details like 
                                   distance, start date, best efforts, and athlete ID.

    Returns:
    pd.DataFrame: A DataFrame containing the fastest segment per athlete for each segment, 
                  including profile picture, athlete name, segment name, distance, 
                  elapsed time, and pace.
    """
    
    # Extract athlete information into a dictionary
    athlete_names = process_names(athlete_data)

    athletes = {
        athlete[ATHLETE_ID]: {
            'Profile_pic': json.loads(athlete[ATHLETE_DATA]).get(PROFILE_PIC),
            'Atleet': athlete_names.get(athlete[ATHLETE_ID]),
        }
        for athlete in athlete_data
    }

    best_efforts = []
    
    for activity in activity_data:
        data = json.loads(activity['data'])

        # Check if 'best_efforts' exists and is not empty
        if BEST_EFFORTS in data and data[BEST_EFFORTS]:
            athlete_id = data.get('athlete', {}).get('id')
            athlete_info = athletes.get(athlete_id)
            
            # Skip activity if athlete info is not found
            if not athlete_info:
                continue
            
            for effort in data[BEST_EFFORTS]:
                # Extract best effort details
                best_efforts.append({
                    'Profile_pic': athlete_info['Profile_pic'],
                    'Atleet': athlete_info['Atleet'],
                    'Segment': effort.get('name'),
                    'Distance_km': effort.get(DISTANCE) / 1000,  # Convert meters to kilometers
                    'Tijd': format_time(effort.get(ELAPSED_TIME)),
                    'Sort_Time': effort.get(ELAPSED_TIME),  # Use this to sort (raw seconds)
                    'Tempo': pace_from_distance_time(effort.get(DISTANCE), effort.get(ELAPSED_TIME)),
                    'Datum': effort.get('start_date_local'),
                    'Activiteit': data.get('name'),
                })

    # Create DataFrame from best efforts
    df = pd.DataFrame(best_efforts)

    # Group by athlete and segment and select the fastest effort per segment
    df_sorted = df.sort_values(by='Sort_Time').groupby(['Atleet', 'Segment']).head(1)

    # Reset the index to start from 1
    df_sorted.reset_index(drop=True, inplace=True)
    df_sorted.index += 1

    return df_sorted
