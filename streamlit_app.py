# Import standard libraries
import datetime
import json

# Import third-party libraries
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import streamlit as st

# Import local configuration
from config import START_YEAR, START_WEEK, TOTAL_WEEKS, TOTAL_KMS

# Import local utility functions
from utils import weeks_since, get_all_dynamodb_items
from data_processing import process_ranking, process_activities
from visualisation.css import add_custom_css

aws_access_key_id = st.secrets["aws_access_key_id"]
aws_secret_access_key = st.secrets["aws_secret_access_key"]

def main():
    # Initialize a session with AWS credentials
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name='eu-central-1'
    )

    dynamodb = session.resource('dynamodb')

    # Retrieve data from DynamoDB tables
    table = dynamodb.Table('athlete_credentials') 
    athlete_data = get_all_dynamodb_items(table)

    table = dynamodb.Table('activities') 
    activity_data = get_all_dynamodb_items(table)

    # Process data for ranking and activities
    ranking_df = process_ranking(athlete_data, activity_data)
    activity_df = process_activities(athlete_data, activity_data)
    total_kms_execute = sum(ranking_df['KM'])
    weeks_count = weeks_since(START_YEAR, START_WEEK)

    bar_data = {
        'Waarde': [total_kms_execute, TOTAL_KMS - total_kms_execute],
        'Eenheid': ["KMs", "KMs"],
        'Kleur': ['#3BCEAC', '#6DABF2']
    }
    bar_df = pd.DataFrame(bar_data)

    # Set Streamlit layout to "wide" for better mobile responsiveness
    st.set_page_config(layout="wide")

    # Add custom CSS
    add_custom_css()

    # Display main content
    st.title('Renclub het zwakke enkeltje')
    st.write('14 mannen, 6 maanden, 1 challenge.')
    st.write(f'Week {weeks_count}/{TOTAL_WEEKS}')
    st.write(f"{round(total_kms_execute, 1)}/{TOTAL_KMS} km")
    st.bar_chart(bar_df, x="Eenheid", y="Waarde", stack=True, color='Kleur', horizontal=True, x_label='', y_label='')

    # Display ranking and activities with mobile-friendly adjustments
    st.write("Ranking")
    st.dataframe(ranking_df, use_container_width=True, hide_index=True, column_config={
        "Profile_pic": st.column_config.ImageColumn(""),
        "Laatste activiteit": st.column_config.DatetimeColumn("Laatste activiteit", format='DD-MM-YYYY'),
    })

    st.write("Activiteiten")
    st.dataframe(activity_df, use_container_width=True, hide_index=True, column_config={
        "Profile_pic": st.column_config.ImageColumn(""),
        "Datum": st.column_config.DatetimeColumn("Datum", format='DD-MM-YYYY HH:MM'),
    })

if __name__ == "__main__":
    main()
