import os
import pandas as pd
from sqlalchemy import create_engine
import tomllib
import numpy as np
import plotly.express as px

# Stacking season csv files and loading into PG admin 

# Load secrets file
with open('secrets.toml', 'rb') as f:
    secrets = tomllib.load(f)

pg_secrets = secrets["pgadmin"]
user = pg_secrets["user"]
password = pg_secrets["pass"]
host = pg_secrets["host"]
database = pg_secrets["database"]

# Create connection to PostgreSQL
print("Connecting to database")
engine = create_engine(f"postgresql://{user}:{password}@{host}/{database}")

# Read the SQL script from the file.  
with open('all_hard_court_matches.sql', 'r') as sql_file:
    sql_query = sql_file.read()

# Pass the SQL query to pd.read_sql. Relevant data selected and aggregated for hard court matches
print("Executing query: Selecting hard court matches and aggregating stats")
hard_court_df = pd.read_sql(sql_query, engine)

# Filter out nonsense height values
df = hard_court_df[hard_court_df['ht'] >= 100]

# Create height groups to sort out outlier issues

ht_grp_df = df.assign(
    ht_group = np.select(
        [
            # Group heights
            df["ht"].isin([173, 174]),
            df["ht"].isin([175, 176]),
            df["ht"].isin([180, 181]),  
            df["ht"].between(182, 183),
            df["ht"].isin([185, 186]),
            df["ht"].isin([188, 189]),  
            df["ht"].isin([190, 191]),  
            df["ht"].isin([193, 194]),  
            df["ht"].between(196, 198),  
            df["ht"].between(201, 203),  
            df["ht"].between(208, 211),  
        ],
        [
            # Assign groups new height
            173,
            175,
            180,  
            182,
            185,
            188,  
            190,  
            193,  
            196,  
            201,  
            208,  
        ],
        default=df["ht"]  # Keep all other heights unchanged
    )
)

# Copy df for Z-score analysis
z_score_df = ht_grp_df.copy()

# Find outliers using Z-score
print("Calculating outliers")
z_score_df['mean'] = z_score_df['ht_group'].map(z_score_df.groupby('ht_group')['ace_percentage'].mean())
z_score_df['std'] = z_score_df['ht_group'].map(z_score_df.groupby('ht_group')['ace_percentage'].std())
z_score_df['z_score'] = (z_score_df['ace_percentage']-z_score_df['mean'])/z_score_df['std']

# Define threshold
upper_threshold = 1.75
lower_threshold = -1.75

# Flag outliers
z_score_df["is_outlier"] = np.select(
    [
        z_score_df['z_score'] > upper_threshold,  
        z_score_df['z_score'] < lower_threshold  
    ],
    [
        "High Outlier",  
        "Low Outlier"  
    ],
    default="Normal"  
)

# Select colours
blue = px.colors.qualitative.Plotly[0]
red = px.colors.qualitative.Plotly[1]
green = px.colors.qualitative.Plotly[2]

# Create interactive scatter plot
fig1 = px.scatter(z_score_df, 
                 x="ht", 
                 y="ace_percentage", 
                 color="is_outlier",
                 hover_data=["name", "total_matches"],  # Add more columns if needed
                 title="Ace Percentage vs Height",
                 labels={"ht": "Height (cm)", "ace_percentage": "Ace Percentage"},
                 color_discrete_map={
                    "Normal": blue,
                    "High Outlier": red,
                    "Low Outlier": green})

# Show figure
print("Display fig1")
fig1.show()

# Filter for high volume of matches
print("Filter for high volume of matches")
z_score_df_filtered = z_score_df[z_score_df['total_matches']>=100]

# Create interactive scatter plot
fig2 = px.scatter(z_score_df_filtered, 
                 x="ht", 
                 y="ace_percentage", 
                 color="is_outlier",
                 hover_data=["name", "total_matches"],  # Add more columns if needed
                 title="Ace Percentage vs Height",
                 labels={"ht": "Height (cm)", "ace_percentage": "Ace Percentage"},
                 color_discrete_map={
                    "Normal": blue,
                    "High Outlier": red,
                    "Low Outlier": green})

# Show figure
print("Display fig2")
fig2.show()