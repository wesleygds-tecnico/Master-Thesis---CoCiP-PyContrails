# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script merges two datasets to enrich a summary file with additional information
#     from a main dataset, specifically adding the 'icao24' (aircraft identifier) and 
#     'time' (flight date) columns to the summary file for further analysis or visualization.
#
# Inputs:
#     1. summary CSV (`df1`): Contains CoCiP summary outputs, indexed by 'flight_id'.
#        Path: "Results\\SAF_analysis\\summary\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"
#     
#     2. main CSV (`df2`): Contains detailed CoCiP outputs, including 'flight_id', 'icao24', and 'time'.
#        Path: "Results\\SAF_analysis\\main\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_main.csv"
#
# Outputs:
#     - A new summary CSV enriched with 'icao24' and 'time' columns.
#       Output Path: "Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"
#
# Additional Comments:
#     - The script removes duplicate entries in the main dataset by 'flight_id' to prevent
#       multiple matches during the merge.
#     - The 'time' column is converted to date format (YYYY-MM-DD), removing time-of-day info.
#     - This step is crucial for aggregating data by aircraft and date in later analysis (e.g., emissions by aircraft type per day).
#     - It assumes that both input files are clean and properly formatted.
# =========================================================================================================================================


import pandas as pd

# Load both CSV files
df1 = pd.read_csv("Results\\SAF_analysis\\summary\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv", low_memory=False)   # This file has 'flight_id'
df2 = pd.read_csv("Results\\SAF_analysis\\main\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_main.csv", low_memory=False)  # This file has 'flight_id' and 'icao24'

df2_dedup = df2.drop_duplicates(subset='flight_id')

# Merge df1 with df2 on 'flight_id', adding the 'icao24' column
df1_updated = df1.merge(df2_dedup[['flight_id', 'icao24']], on='flight_id', how='left')

# Merge df1 with df2 on 'flight_id', adding the 'icao24' column
df1_updated = df1_updated .merge(df2_dedup[['flight_id', 'time']], on='flight_id', how='left')

# Ensure 'time' has only year-month-day (strip hours/minutes/seconds)
df1_updated['time'] = pd.to_datetime(df1_updated['time']).dt.date  # Converts to date object

# Save the updated first file (optionally overwrite or use a new file)
df1_updated.to_csv("Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv", index=False)