# data_processing/ranking.py

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
MOVING_TIME = 'moving_time'
START_DATE = 'start_date_local'
ACTIVITY_TYPE = 'type'
RUN_TYPE = 'Run'
LAST_ACTIVITY = 'Laatste activiteit'
DEFAULT_LAST_ACTIVITY = None

def process_ranking(athlete_data, activity_data):
    """
    Process athlete and activity data to calculate total kilometers, number of activities,
    and the date of the last activity for each athlete.

    Parameters:
    athlete_data (list of dict): A list of dictionaries, where each dictionary contains 
                                  athlete information, including 'athlete_id' and 'data' 
                                  (with the athlete's firstname).
    activity_data (list of dict): A list of dictionaries, where each dictionary contains 
                                   activity information, including 'data' (with details like 
                                   distance, start date, and athlete id).

    Returns:
    pd.DataFrame: A DataFrame containing the processed ranking data for athletes.
    """
    athlete_names = process_names(athlete_data)
    
    athletes = {
        athlete.get(ATHLETE_ID): {
            'Profile_pic': json.loads(athlete.get(ATHLETE_DATA)).get(PROFILE_PIC),
            'Atleet': athlete_names.get(athlete.get(ATHLETE_ID)),
            'Kilometers': 0,  # Keep as 'Kilometers' here for compatibility
            'Activiteiten': 0,
            LAST_ACTIVITY: DEFAULT_LAST_ACTIVITY
        } for athlete in athlete_data
    }

    for activity in activity_data:
        data = json.loads(activity[ATHLETE_DATA])
        athlete_id = data.get('athlete', {}).get('id')
        distance = data.get(DISTANCE)
        start_date = data.get(START_DATE)

        # Parse start date if it exists
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")

        # Update athlete data for running activities
        if athlete_id in athletes and data.get(ACTIVITY_TYPE) == RUN_TYPE:
            athletes[athlete_id]['Kilometers'] += distance
            athletes[athlete_id]['Activiteiten'] += 1
            
            # Update last activity date
            last_activity = athletes[athlete_id][LAST_ACTIVITY]
            if last_activity == DEFAULT_LAST_ACTIVITY or (start_date and start_date > last_activity):
                athletes[athlete_id][LAST_ACTIVITY] = start_date

    # Create df
    df = pd.DataFrame(athletes.values())

    # Sort by 'Kilometers' in descending order
    df = df.sort_values(by='Kilometers', ascending=False)

    # Round Kilometers values and rename the column to 'KM'
    df['Kilometers'] = [round(val / 1000, 1) for val in df['Kilometers']]
    df.rename(columns={'Kilometers': 'KM', 'Activiteiten': 'Act.'}, inplace=True)

    # Add a 'Ranking' column for the index instead of setting it as index
    df.reset_index(drop=True, inplace=True)
    df.index += 1
    df.insert(0, '', df.index)  # Insert as the first column

    return df
