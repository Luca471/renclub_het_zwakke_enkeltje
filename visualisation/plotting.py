import altair as alt
import pandas as pd

def create_progress_chart(activity_df, weeks_count, TOTAL_WEEKS, TOTAL_KMS, START_YEAR, START_WEEK):
    """
    Create an Altair line chart to visualize the progress of the running challenge.

    Parameters:
    activity_df (pd.DataFrame): A DataFrame containing the activity data.
    weeks_count (int): The current week count.
    TOTAL_WEEKS (int): The total number of weeks in the challenge.
    TOTAL_KMS (int): The total number of kilometers in the challenge.
    START_YEAR (int): The starting year of the challenge.
    START_WEEK (int): The starting week of the challenge.

    Returns:
    alt.Chart: An Altair line chart showing the progress of the challenge.
    """

    # Process cumulative distances per week
    activity_df['Datum'] = pd.to_datetime(activity_df['Datum'])
    activity_df['Week_Number'] = activity_df['Datum'].dt.isocalendar().week
    activity_df['Year'] = activity_df['Datum'].dt.isocalendar().year
    activity_df = activity_df[activity_df['Year'] >= START_YEAR]

    def calculate_weeks_since(row):
        activity_year = row['Year']
        activity_week = row['Week_Number']
        weeks_since_start = (activity_year - START_YEAR) * 52 + (activity_week - START_WEEK)
        if activity_year == START_YEAR:
            weeks_since_start = activity_week - START_WEEK
        return weeks_since_start  # Week count starts from 0

    activity_df['Weeks_Since_Start'] = activity_df.apply(calculate_weeks_since, axis=1)

    # Group by week and sum distances
    weekly_km = activity_df.groupby('Weeks_Since_Start')['KM'].sum().reset_index()

    # Ensure all weeks are represented up to TOTAL_WEEKS
    weeks = pd.DataFrame({'Weeks_Since_Start': range(0, TOTAL_WEEKS + 1)})

    # Merge to include all weeks
    weekly_km = weeks.merge(weekly_km, on='Weeks_Since_Start', how='left')

    # Fill missing values with zero
    weekly_km['KM'] = weekly_km['KM'].fillna(0)

    # Compute cumulative sum
    weekly_km['Cumulative_KM'] = weekly_km['KM'].cumsum()

    # Limit actual progress to current week
    weekly_km_actual = weekly_km[weekly_km['Weeks_Since_Start'] <= weeks_count]

    # Create goal line data
    weekly_km['Goal_KM'] = (weekly_km['Weeks_Since_Start'] / TOTAL_WEEKS) * TOTAL_KMS

    # Prepare data for plotting
    plot_data_actual = weekly_km_actual[['Weeks_Since_Start', 'Cumulative_KM']].copy()
    plot_data_actual['Type'] = 'Werkelijke kilometers'
    plot_data_actual.rename(columns={'Cumulative_KM': 'Kilometers'}, inplace=True)

    plot_data_goal = weekly_km[['Weeks_Since_Start', 'Goal_KM']].copy()
    plot_data_goal['Type'] = 'Doel kilometers'
    plot_data_goal.rename(columns={'Goal_KM': 'Kilometers'}, inplace=True)

    # Combine the data
    plot_data = pd.concat([plot_data_actual, plot_data_goal], ignore_index=True)

    # Define color scale
    color_scale = alt.Scale(
        domain=['Werkelijke kilometers', 'Doel kilometers'],
        range=['#1f77b4', '#ff7f0e']  # Blue for actual, orange for goal
    )

    # Create the base chart
    base = alt.Chart(plot_data).encode(
        x=alt.X('Weeks_Since_Start:Q', title='Week', scale=alt.Scale(domain=[0, TOTAL_WEEKS])),
        y=alt.Y('Kilometers:Q', title='Kilometers', scale=alt.Scale(domain=[0, TOTAL_KMS])),
        color=alt.Color('Type:N', scale=color_scale, legend=alt.Legend(title='Legenda'))
    )

    # Create line for actual progress (solid line)
    line_actual = base.transform_filter(
        alt.datum.Type == 'Werkelijke kilometers'
    ).mark_line()

    # Create line for goal progress (dotted line)
    line_goal = base.transform_filter(
        alt.datum.Type == 'Doel kilometers'
    ).mark_line(
        strokeDash=[5, 5]  # Dotted line
    )

    # Combine the charts
    line_chart = alt.layer(line_actual, line_goal).properties(
        title='Voortgang grafiekje'
    )

    return line_chart