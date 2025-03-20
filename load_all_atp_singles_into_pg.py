import os
import pandas as pd
from sqlalchemy import create_engine
import tomllib

# Stacking season csv files and loading into PG admin 

# Load secrets file
with open('secrets.toml', 'rb') as f:
    secrets = tomllib.load(f)

pg_secrets = secrets["pgadmin"]
user = pg_secrets["user"]
password = pg_secrets["pass"]
host = pg_secrets["host"]
database = pg_secrets["database"]

atp_matches_filepath = secrets["local_file_paths"]["atp_singles"]

# Create connection to PostgreSQL
engine = create_engine(f"postgresql://{user}:{password}@{host}/{database}")

# Create list of files
files = os.listdir(f"{atp_matches_filepath}")

# Load and stack all CSV files
print("Stacking season data...")
df_list = [pd.read_csv(f"{atp_matches_filepath}\\{filename}") for filename in files]
df_all = pd.concat(df_list, ignore_index=True)
print("Season data stacked")

# Upload to PostgreSQL
print("Uploading all atp matches to sql database...")
df_all.to_sql("atp_matches_singles", engine, if_exists="replace", index=False)
print("All matches uploaded")