# ===============================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes and enriches raw aircraft trajectory data using aircraft parameters
#     and a physical model (PSFlight) from the PyContrails library. It adds estimated engine
#     efficiency, fuel flow, and aircraft mass to the flight data based on atmospheric and 
#     aircraft-specific information.
# 
# Inputs:
#     1. Aircraft Identification Database (icao24 → aircraft type)
#        File: aircraft_database_icao24.csv
#     
#     2. Aircraft Parameters Database (ICAO → wingspan, nvpm_ei_n)
#        File: ps-aircraft-params-20240524.csv
#     
#     3. Trajectory Data (OpenSky or Flightradar24 flight tracks)
#        File: 2025_01_01-2025_01_07_LA_flight_id_TAS.csv
# 
# Outputs:
#     - Processed CSV files with new columns:
#         - engine_efficiency
#         - fuel_flow
#         - aircraft_mass
#     - Files are saved with the same base name as the input file, with "_processed" appended.
# 
# Additional Comments:
#     - The script uses PyContrails' PSFlight model to estimate physical parameters.
#     - Default values are used for aircraft type ("A320") and wingspan (34.10 m) if missing.
#     - Atmospheric data is estimated using ISA assumptions for lower altitudes.
#     - This script is modular and can be extended to loop through multiple input files.
#     - Temporary placeholders for physical variables (Mach, TAS, etc.) are included but commented out.
#     - Ensure the required input files and paths exist before running.
#     - This script was written for a controlled experiment analyzing air traffic data around Los Angeles.
# 
# Requirements:
#     - Python 3.x
#     - Libraries: numpy, pandas, tqdm, ambiance, pycontrails
# ===============================================================================================================

import numpy as np
import pandas as pd
from tqdm import tqdm
import ambiance
from ambiance import Atmosphere
from pycontrails import Flight
from pycontrails.models.ps_model import PSFlight

# Paths to input files
aircraft_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\aircraft_database_icao24.csv"
wingspan_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\ps-aircraft-params-20240524.csv"
nvpm_ei_n_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\ps-aircraft-params-20240524.csv"

# Load the aircraft database (icao24 -> aircraft_type)
acft_df = pd.read_csv(aircraft_db_path, low_memory=False)
# Clean column names: strip spaces and remove special characters
acft_df.columns = acft_df.columns.str.strip()  # Remove spaces
acft_df.columns = acft_df.columns.str.replace("'", "", regex=True)  # Remove quotes

# Print to verify
acft_df = acft_df[['icao24', 'ICAO']]  # Keep only relevant columns
acft_df['icao24'] = acft_df['icao24'].astype(str)

# Load the wingspan database (ICAO -> wingspan)
wingspan_df = pd.read_csv(wingspan_db_path, low_memory=False)

# Clean column names: strip spaces and remove special characters
wingspan_df.columns = wingspan_df.columns.str.strip()  # Remove spaces
wingspan_df.columns = wingspan_df.columns.str.replace("'", "", regex=True)  # Remove quotes

# Print updated column names to check
print("Updated column names in wingspan_df:", wingspan_df.columns.tolist())

wingspan_df = wingspan_df[['ICAO', 'span_m', 'nvpm_ei_n']]  # Keep only relevant columns
wingspan_df['ICAO'] = wingspan_df['ICAO'].astype(str)
wingspan_df.rename(columns={'span_m': 'wingspan'}, inplace=True)

# nvPM

# Load the wingspan database (ICAO -> wingspan)
nvpm_ei_n_df = pd.read_csv(wingspan_db_path, low_memory=False)

# Clean column names: strip spaces and remove special characters
nvpm_ei_n_df.columns = nvpm_ei_n_df.columns.str.strip()  # Remove spaces
nvpm_ei_n_df.columns = nvpm_ei_n_df.columns.str.replace("'", "", regex=True)  # Remove quotes

# Print updated column names to check
print("Updated column names in wingspan_df:", wingspan_df.columns.tolist())

nvpm_ei_n_df = wingspan_df[['ICAO', 'nvpm_ei_n']]  # Keep only relevant columns
nvpm_ei_n_df['ICAO'] = wingspan_df['ICAO'].astype(str)
#nvpm_ei_n_df.rename(columns={'span_m': 'wingspan'}, inplace=True)


# Remove leading/trailing spaces in column names
acft_df.columns = acft_df.columns.str.strip()
wingspan_df.columns = wingspan_df.columns.str.strip()
nvpm_ei_n_df.columns = nvpm_ei_n_df.columns.str.strip()

# List of input files
input_files = {
    "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\Opensky\\analysis_LA\\Flightradar24\\2025_01_01-2025_01_07_LA_flight_id_TAS.csv",
}

# Output directory
output_dir = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\Opensky\\analysis_LA\\Flightradar24"

# List to store indices of outlier rows to be dropped
outlier_indices = []

# List to store flight_ids of outliers
outlier_flight_ids = []

# Ensure output directory exists
import os
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each file in the input_files list
#for input_file in tqdm(input_files, desc="Processing flights", unit="flight"):
for input_file in input_files:
    try:
        # Read the input file
        df = pd.read_csv(input_file, low_memory=False)

        df['time']      = pd.to_datetime(df["time"], format="mixed", errors="coerce")
        df['icao24']    = df['icao24'].astype(str)
        
        # df['altitude']  = df['altitude'] * 0.3048 # - Flight Radar 24

        # Merge to get aircraft_type from icao24
        df = df.merge(acft_df, on="icao24", how="left")

        # Merge to get wingspan from ICAO
        df = df.merge(wingspan_df, on="ICAO", how="left")

        # Rename "ICAO" to "aircraft_type" before merging
        df.rename(columns={"ICAO": "aircraft_type"}, inplace=True)

        # Set default values for missing aircraft_type and wingspan
        df['aircraft_type'] = df['aircraft_type'].fillna("A320")  # Default to A320
        df['wingspan'] = df['wingspan'].fillna(34.10)  # Default to A320 wingspan (in meters)

        # speed_of_sound_array    = Atmosphere(h = df['altitude'].to_numpy()).speed_of_sound - OpenSky
        # df['speed_of_sound']    = pd.Series(speed_of_sound_array, index=df.index) - OpenSky
        # df['true_airspeed']     = df['speed_of_sound'] * 0.82 - OpenSky
        # df['mach_number']       = 0.82               # constant and assumed properties - to be included into jason for easy and fast retrieve - OpenSky
        # df['nvpm_ei_n']         = 9.57e+14           # constant and assumed properties - to be included into jason for easy and fast retrieve

        # Create placeholder columns for new attributes
        # df['engine_efficiency'] = 0.4
        # df['fuel_flow']         = 1.632
        # df['aircraft_mass']     = 52290

        # Create placeholder columns for new attributes - NON Constant variables
        
        # df['engine_efficiency'] = np.nan
        # df['fuel_flow']         = np.nan
        # df['aircraft_mass']     = np.nan

        # Create a loop for every flight_id
        #for flight_id, flight_group in tqdm(df.groupby('flight_id'), desc="Processing flight IDs", unit="flight_id"):

        processed_flight_groups = []  # Store processed flight groups
        
        for flight_id, flight_group in df.groupby('flight_id'):
            
            # Extract the aircraft_type from the first row of the flight_group
            aircraft_type = flight_group["aircraft_type"].iloc[0]  

            # Load flight group into a Flight object
            attrs = {"flight_id": flight_id, "aircraft_type": aircraft_type}

            print('flight_group: ', flight_group)
            print('flight_id: ', flight_id)

            flight = Flight(flight_group, attrs=attrs)

            # Create PS Flight model and evaluate
            ps_model = PSFlight(
                fill_low_altitude_with_isa_temperature  =True,  # Estimate temperature using ISA
                fill_low_altitude_with_zero_wind        =True,  # Estimate airspeed by using groundspeed
            )
            
            # print('Estimate airspeed by using groundspeed \n')

            out = ps_model.eval(flight)  # Run the model and get the output

            # print('Run the model and get the output \n')
 
            # Ensure the outputs are correctly aligned with the index
            flight_group['engine_efficiency']   = pd.Series(out['engine_efficiency'], index=flight_group.index)
            flight_group['fuel_flow']           = pd.Series(out['fuel_flow'], index=flight_group.index)
            flight_group['aircraft_mass']       = pd.Series(out['aircraft_mass'], index=flight_group.index)

            #    Store processed flight group
            processed_flight_groups.append(flight_group)
            
        # Concatenate all processed flight groups back into a single DataFrame
        df = pd.concat(processed_flight_groups, ignore_index=True)

        df = df.dropna(how='any')  # Drops rows with at least one NaN value

        # Create output file path
        output_file = os.path.join(output_dir, os.path.basename(input_file).replace(".csv", "_processed.csv"))

        # Save the updated DataFrame to the output file
        df.to_csv(output_file, index=False)

        print(f"Processed and saved: {output_file}")

    except Exception as e:
        print(f"Error processing {input_file}: {e}")