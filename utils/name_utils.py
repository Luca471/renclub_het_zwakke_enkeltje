import json

ATHLETE_ID = 'athlete_id'
ATHLETE_DATA = 'data'
FIRST_NAME = 'firstname'
LAST_NAME = 'lastname'

def process_names(athlete_data):
    names = {}

    for athlete in athlete_data:
        athlete_info = json.loads(athlete.get(ATHLETE_DATA))
        athlete_id = athlete.get(ATHLETE_ID)
        first_name = athlete_info.get(FIRST_NAME)
        last_name = athlete_info.get(LAST_NAME)
        # only first letter of last name
        last_name = last_name[0]

        names[athlete_id] = f"{first_name} {last_name}"

    return names
