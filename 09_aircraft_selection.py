# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script enriches flight trajectory data with aircraft information by merging
#     aircraft type and wingspan data from two reference databases based on the aircraft's ICAO24 and ICAO codes.
#     It reads flight data CSV files, merges the additional aircraft details, fills missing values with defaults,
#     and saves the enhanced dataset for further analysis.
# 
# Inputs:
#     - aircraft_database_icao24.csv : CSV file mapping 'icao24' codes to aircraft ICAO types.
#     - ps-aircraft-params-20240524.csv : CSV file providing wingspan measurements for aircraft ICAO types.
#     - One or more flight trajectory CSV files containing flight records including 'icao24' and 'time' columns.
# 
# Outputs:
#     - Processed CSV files saved in the output directory with appended aircraft type and wingspan columns.
#       These files have "_with_aircraft_info.csv" suffix added to the original filenames.
# 
# Additional Comments:
#     - The script cleans column names in input dataframes to ensure consistency.
#     - Missing aircraft type and wingspan values are filled with defaults (A320 and 34.10 meters wingspan).
#     - The time column in flight data is converted to datetime for potential time-based processing.
#     - Designed to process multiple input files, currently with one file specified in the input_files list.
#     - Output directory creation is ensured if it doesn't exist.
#     - Uses tqdm for progress visualization when processing multiple files.
# =========================================================================================================================================

import os
import pandas as pd
from tqdm import tqdm

# Paths to input files
aircraft_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\aircraft_database_icao24.csv"
wingspan_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\ps-aircraft-params-20240524.csv"

# Load the aircraft database (icao24 -> aircraft_type)
acft_df = pd.read_csv(aircraft_db_path, low_memory=False)
# Clean column names: strip spaces and remove special characters
acft_df.columns = acft_df.columns.str.strip()  # Remove spaces
acft_df.columns = acft_df.columns.str.replace("'", "", regex=True)  # Remove quotes

# Print to verify
acft_df = acft_df[['icao24', 'ICAO']]  # Keep only relevant columns

# Load the wingspan database (ICAO -> wingspan)
wingspan_df = pd.read_csv(wingspan_db_path, low_memory=False)

# Clean column names: strip spaces and remove special characters
wingspan_df.columns = wingspan_df.columns.str.strip()  # Remove spaces
wingspan_df.columns = wingspan_df.columns.str.replace("'", "", regex=True)  # Remove quotes

# Print updated column names to check
print("Updated column names in wingspan_df:", wingspan_df.columns.tolist())

wingspan_df = wingspan_df[['ICAO', 'span_m']]  # Keep only relevant columns
wingspan_df.rename(columns={'span_m': 'wingspan'}, inplace=True)

# Remove leading/trailing spaces in column names
acft_df.columns = acft_df.columns.str.strip()
wingspan_df.columns = wingspan_df.columns.str.strip()

# List of input files
input_files = [
    "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\01_January\\raw_data\\2025_01_01-2025_01_07_filtered_checked.csv",
]

# Output directory
output_dir = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\01_January"
os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists

# Process each file
for input_file in tqdm(input_files, desc="Processing flights", unit="flight"):
    # Read the input flight data
    df = pd.read_csv(input_file, low_memory=False)

    # Convert time column to datetime format
    df['time'] = pd.to_datetime(df["time"], format="mixed", errors="coerce")

    # Merge to get aircraft_type from icao24
    df = df.merge(acft_df, on="icao24", how="left")

    # Merge to get wingspan from ICAO
    df = df.merge(wingspan_df, on="ICAO", how="left")

    # Rename "ICAO" to "aircraft_type" before merging
    df.rename(columns={"ICAO": "aircraft_type"}, inplace=True)

    # Set default values for missing aircraft_type and wingspan
    df['aircraft_type'] = df['aircraft_type'].fillna("A320")  # Default to A320
    df['wingspan'] = df['wingspan'].fillna(34.10)  # Default to A320 wingspan (in meters)

    # Save the modified file
    output_file = os.path.join(output_dir, os.path.basename(input_file).replace("_filtered_checked.csv", "_with_aircraft_info.csv"))
    df.to_csv(output_file, index=False)

    print(f"Processed file saved: {output_file}")