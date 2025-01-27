# Import standard libraries
import datetime
import json

# Import third-party libraries
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import streamlit as st
import altair as alt

# Import local configuration
from config import START_YEAR, START_WEEK, TOTAL_WEEKS, TOTAL_KMS, EXCLUDE_IDS

# Import local utility functions
from utils import weeks_since, get_all_dynamodb_items
from data_processing import process_ranking, process_activities, process_best_efforts
from visualisation.plotting import create_progress_chart
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
    ranking_df = process_ranking(athlete_data, activity_data, EXCLUDE_IDS)
    activity_df = process_activities(athlete_data, activity_data, EXCLUDE_IDS)
    best_efforts_df = process_best_efforts(athlete_data, activity_data, EXCLUDE_IDS)

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
    st.write(f'{len(ranking_df)} mannen, 6 maanden, 1 challenge.')
    st.write(f'Week {weeks_count}/{TOTAL_WEEKS}')
    st.write(f"{round(total_kms_execute, 1)}/{TOTAL_KMS} km")

    st.bar_chart(bar_df, x="Eenheid", y="Waarde", stack=True, color='Kleur', horizontal=True, x_label='', y_label='')

    # calculate the amount of km's that should be ran by now
    target_km_per_week = TOTAL_KMS / TOTAL_WEEKS

    # calculate the amount of km's that we're behind this week
    km_behind = target_km_per_week * weeks_count - total_kms_execute

    if km_behind > 0:
        st.write(f"We lopen deze week {round(km_behind, 1)} km achter op schema.")

        with st.expander("Meer details tonen"):
            # Calculate km's per week needed to reach the goal
            new_km_per_week = (TOTAL_KMS - total_kms_execute) / (TOTAL_WEEKS - weeks_count)
            st.write(f"We moeten gemiddeld {round(new_km_per_week, 1)} km/w i.p.v. de oorspronkelijke {round(target_km_per_week, 1)} km/w lopen om de doelstelling te behalen.")

            # Calculate KM's per week needed to reach the goal averaged per person
            new_km_per_week_per_person = new_km_per_week / ranking_df.shape[0]
            st.write(f"Dit komt neer op {round(new_km_per_week_per_person, 1)} km/w per persoon.")

    # Display ranking and activities with mobile-friendly adjustments
    st.write("Ranking")
    number_of_rows = ranking_df.shape[0]
    st.dataframe(ranking_df, height=((number_of_rows + 1) * 35 + 3), use_container_width=True, hide_index=True, column_config={
        "Profile_pic": st.column_config.ImageColumn(""),
        "Laatste activiteit": st.column_config.DatetimeColumn("Laatste activiteit", format='DD-MM-YYYY'),
    })

    st.write("Activiteiten")
    st.dataframe(activity_df, use_container_width=True, hide_index=True, column_config={
        "Profile_pic": st.column_config.ImageColumn(""),
        "Datum": st.column_config.DatetimeColumn("Datum", format='DD-MM-YYYY HH:MM'),
    })

    # Selectbox for 'Afstand' with default value '5km'
    afstand_options = ['All'] + list(best_efforts_df['Segment'].unique())

    selected_afstand = st.selectbox(
        "Afstand:",
        options=afstand_options,
        index=afstand_options.index('5K'),
        key='afstand'
    )

    # Selectbox for 'Atleet' with default 'All'
    atleet_options = ['All'] + list(best_efforts_df['Atleet'].unique())

    selected_atleet = st.selectbox(
        "Atleet:",
        options=atleet_options,
        index=atleet_options.index('All'),  # Default to 'All'
        key='atleet'
    )
    
    # Apply filters based on selected 'Afstand' and 'Atleet'
    if selected_afstand == 'All' and selected_atleet == 'All':
        # No filtering applied (all data)
        filtered_df = best_efforts_df
    elif selected_afstand == 'All':
        # Filter only by Atleet if Afstand is 'All'
        filtered_df = best_efforts_df[best_efforts_df['Atleet'] == selected_atleet]
    elif selected_atleet == 'All':
        # Filter only by Afstand if Atleet is 'All'
        filtered_df = best_efforts_df[best_efforts_df['Segment'] == selected_afstand]
    else:
        # Filter by both Afstand and Atleet
        filtered_df = best_efforts_df[
            (best_efforts_df['Segment'] == selected_afstand) &
            (best_efforts_df['Atleet'] == selected_atleet)
        ]

    filtered_df = filtered_df[["Profile_pic", "Atleet", "Segment", "Tijd", "Tempo", "Activiteit", "Datum"]]
    filtered_df = filtered_df.rename(columns={'Segment': 'Afstand'})
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df.index += 1
    
    # Display filtered DataFrame
    st.write("Best efforts")
    st.dataframe(filtered_df, use_container_width=True, column_config={
        "Profile_pic": st.column_config.ImageColumn(""),
        "Datum": st.column_config.DatetimeColumn("Datum", format='DD-MM-YYYY HH:MM'),
    })

    # Generate and display the progress chart
    line_chart = create_progress_chart(activity_df, weeks_count, TOTAL_WEEKS, TOTAL_KMS, START_YEAR, START_WEEK)
    st.altair_chart(line_chart, use_container_width=True)

if __name__ == "__main__":
    main()