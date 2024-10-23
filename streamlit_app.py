import pandas as pd
import streamlit as st
import datetime
import boto3
from botocore.exceptions import ClientError
import json

aws_access_key_id = st.secrets["aws_access_key_id"]
aws_secret_access_key = st.secrets["aws_secret_access_key"]

def get_all_dynamodb_items(table):
    items = []
    try:
        response = table.scan()
        items.extend(response.get('Items', []))

        # Handle pagination in case there are more items to retrieve
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

    except ClientError as e:
        print(f"Failed to get items from DynamoDB: {e.response['Error']['Message']}")

    return items


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

# Initialize a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='eu-central-1'
)

# Initialize the DynamoDB resource
dynamodb = session.resource('dynamodb')

table = dynamodb.Table('athlete_credentials') 
athletes = get_all_dynamodb_items(table)

table = dynamodb.Table('activities') 
activities = get_all_dynamodb_items(table)

athletes = {athlete.get('athlete_id'): {'Atleet': json.loads(athlete.get('data')).get('firstname'), 'Kilometers': 0, 'Activiteiten': 0, 'Laatste activiteit': '-'} for athlete in athletes}

table = dynamodb.Table('activities') 
activities = get_all_dynamodb_items(table)

for activity in activities:
    data = json.loads(activity['data'])
    athlete_id = data.get('athlete').get('id')
    distance = data.get('distance')
    time = data.get('moving_time')
    start_date = data.get('start_date_local')
    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    
    if athlete_id in athletes and data.get("type") == "Run":
        athletes[athlete_id]['Kilometers'] += distance
        athletes[athlete_id]['Activiteiten'] += 1
        if athletes[athlete_id].get("Laatste activiteit"):
            if athletes[athlete_id].get("Laatste activiteit") == '-' or athletes[athlete_id].get("Laatste activiteit") < start_date:
                athletes[athlete_id]["Laatste activiteit"] = start_date
        else:
            athletes[athlete_id]["Laatste activiteit"] = start_date


df = pd.DataFrame(athletes.values())
total_kms_execute = sum(df['Kilometers'])
if total_kms_execute > 0:
    total_kms_execute = round(total_kms_execute/1000,2)

df['Kilometers'] = [str(round(val/1000,1)).replace('.',',') for val in df['Kilometers']]
df["Laatste activiteit"] = [val.strftime("%d-%m-%Y") if val != '-' else val for val in df["Laatste activiteit"]]

# Constants
start_year = 2024  
start_week = 42 
total_weeks = 26
total_kms = 2000

weeks_count = weeks_since(start_year, start_week)

# Set the app title 
st.title('Renclub het zwakke enkeltje') 
# Add a welcome message 
st.write('14 mannen, 6 maanden, 1 challenge.') 
st.write(f'Week {weeks_count}/{total_weeks}')

st.write(f"{str(total_kms_execute).replace('.',',')}/{total_kms} km")

bar_data = {
    'Waarde': [total_kms_execute, total_kms-total_kms_execute],
    'Eenheid': ["KMs", "KMs"],
    'Kleur': ['#3BCEAC', '#6DABF2']
}

bar_df = pd.DataFrame(bar_data)

st.bar_chart(bar_df, x="Eenheid", y="Waarde", stack = True, color='Kleur', horizontal=True, x_label='', y_label='')

st.write("Ranking")

st.dataframe(
    df,
    hide_index=False
)