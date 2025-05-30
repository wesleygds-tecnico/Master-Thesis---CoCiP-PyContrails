# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes aircraft trajectory data for a specific airline (AIC129) using the CoCiP (Contrail Cirrus Prediction) model from the PyContrails library.
#     It evaluates the formation and properties of contrails from flight segments based on meteorological data obtained from the ERA5 reanalysis dataset.
# 
# Inputs:
#     - A CSV file containing cleaned and preprocessed flight trajectory data:
#       "2024-01-01_2024-01-07_raw_data_AIC129_checked_processed.csv"
#     - ERA5 reanalysis meteorological datasets (pressure-level and single-level variables)
#     - Parameters for contrail modeling (e.g., humidity scaling factor)
# 
# Outputs:
#     - A processed CSV file:
#       "AIC129_2024-01-01_2024-01-07_raw_data_checked_processed_cocip.csv"
#       This file contains CoCiP-evaluated contrail data and radiative forcing estimates per flight segment.
# 
# Additional Comments:
#     - The script checks whether the output file already contains evaluated flights to avoid re-processing.
#     - It filters only new or previously unprocessed flights to improve efficiency.
#     - If CoCiP fails for a specific flight, the script records a placeholder with NaN values and tags it as an error.
#     - The script ensures compatibility with ERA5 data and uses a constant relative humidity scaling based on Teoh (2020, 2022).
#     - ERA5 data is automatically downloaded or loaded from the local cache.
#     - The model integration time step is set to 10 minutes.
#     - The script is designed to run efficiently with tqdm progress bars and memory cleanup between iterations.
# 
# Dependencies:
#     - os
#     - numpy
#     - pandas
#     - tqdm
#     - matplotlib
#     - pycontrails
# 
# Note:
#     - Make sure you have a valid ECMWF key set up for downloading ERA5 data if not cached.
#     - Adjust aircraft type or attributes as needed.
# =========================================================================================================================================

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from pycontrails import Flight
from matplotlib import pyplot as plt
from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip
from pycontrails.models.humidity_scaling import ConstantHumidityScaling

# Define the list of columns
columns = [
    "waypoint", "icao24", "latitude", "longitude", "altitude", "vertical_rate", 
    "groundspeed", "flight_id", "true_airspeed", "mach_number", "aircraft_mass", 
    "fuel_flow", "engine_efficiency", "nvpm_ei_n", "wingspan", "aircraft_type", 
    "time", "level", "air_pressure", "air_temperature", "specific_humidity", 
    "u_wind", "v_wind", "rhi", "segment_length", "sin_a", "cos_a", "G", 
    "T_sat_liquid", "rh", "rh_critical_sac", "sac", "T_critical_sac", "width", 
    "depth", "rhi_1", "air_temperature_1", "specific_humidity_1", "altitude_1", 
    "persistent_1", "rho_air_1", "iwc_1", "n_ice_per_m_1", "ef", "contrail_age", 
    "sdr_mean", "rsr_mean", "olr_mean", "rf_sw_mean", "rf_lw_mean", "rf_net_mean", "cocip"
]

# Path to the output .csv file
output_csv_file = "AIC129_2024-01-01_2024-01-07_raw_data_checked_processed_cocip.csv"

data =  pd.read_csv("C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\data\\traffic\\2024-01-01_2024-01-07_raw_data_AIC129_checked_processed.csv")

# Convert the timestamp column to datetime
data['time'] = pd.to_datetime(data['time'])

# Check if the file exists
if os.path.exists(output_csv_file):
    # Read the existing flight IDs from the CSV
    existing_flights_df = pd.read_csv(output_csv_file)
    existing_flight_ids = existing_flights_df["flight_id"].unique()  # Get unique flight IDs
    # print(f"Existing flight IDs: {existing_flight_ids}")
else:
    # If the file does not exist, initialize an empty list of flight IDs
    existing_flight_ids = []
    # print("No existing file found. Starting with an empty list of flight IDs.")
 
unique_flights_list = data['flight_id'].unique().tolist()

# Exclude flight IDs that are already in the CSV
filtered_flights_list = [flight_id for flight_id in unique_flights_list if flight_id not in existing_flight_ids]

# Initialize a flag to write the header only once
write_header = True

# Remove timezone info
time_bounds = (
    data["time"].min().tz_localize(None),  # Remove timezone info
    data["time"].max().tz_localize(None) + pd.Timedelta(hours=20)   # Remove timezone info
)

# pressure_levels = (1000, 950, 900, 850, 800, 750, 700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 200)
pressure_levels = (800, 750, 700, 650, 600, 550, 500, 450, 400,
                         350, 300, 250, 200, 150, 100, 50)
 
era5pl = ERA5(
    time            =   time_bounds,
    variables       =   Cocip.met_variables + Cocip.optional_met_variables,
    pressure_levels =   pressure_levels,
)
era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

# download data from ERA5 (or open from cache)
met = era5pl.open_metdataset()
rad = era5sl.open_metdataset()

# Loop through each unique flight ID
for flight_id in tqdm(filtered_flights_list, desc="Processing flights", unit="flight"):
    # Define attributes for the flight
    attrs = {
        "flight_id": flight_id,
        "aircraft_type": "A320",  # Modify as needed
    }
    
    # Filter the data for the current flight ID
    filtered_data = data[data['flight_id'] == flight_id]
    
    # Create a Flight object
    flight = Flight(filtered_data, attrs=attrs)
    
    params = {
        "dt_integration": np.timedelta64(10, "m"),
        # The humidity_scaling parameter is only used for ECMWF ERA5 data
        # based on Teoh 2020 and Teoh 2022 - https://acp.copernicus.org/preprints/acp-2022-169/acp-2022-169.pdf
        # Here we use an example of constantly scaling the humidity value by 0.99
        "humidity_scaling": ConstantHumidityScaling(rhi_adj=0.99),
    }

    # print("Assessing: ", flight_id)

    try:
        cocip           = Cocip(met=met, rad=rad, params=params)
        output_flight   = cocip.eval(source=flight)
        df              = output_flight.dataframe

    except Exception as e:
        # In case of an error, print the error and continue with the next iteration
        # print(f"Error processing flight {flight['flight_id']}: {e}")

        # Create a DataFrame with NaN values, except for the flight_id column
        new_line = {col: [np.nan] for col in columns}
        new_line["flight_id"] = [flight_id + "_ERROR"]  # Set the flight_id column

        # Create the new DataFrame
        new_df = pd.DataFrame(new_line)

        # Append the DataFrame to the same .csv file
        new_df.to_csv(output_csv_file, mode='a', header=write_header, index=False)
        # print("No-CoCiP added to output file: ", flight_id)

        # After the first iteration, ensure the header is not written again
        write_header = False

        # Optional: Delete variables to free up memory
        del new_line, new_df

        continue  # Continue to the next iteration of the loop        

    if hasattr(cocip.contrail, "head"):
        # Code to execute if 'cocip.contrail' has the 'head' attribute
        # print("cocip.contrail has the attribute 'head'")

        # Append the DataFrame to the same .csv file
        df.to_csv(output_csv_file, mode='a', header=write_header, index=False)
        # print("CoCiP added to output file: ", flight_id)

        # After the first iteration, ensure the header is not written again
        write_header = False

        del df, output_flight, cocip
    
    else:
        # Code to execute if 'cocip.contrail' does not have the 'head' attribute
        # print("cocip.contrail does not have the attribute 'head'")

        # Create a DataFrame with NaN values, except for the flight_id column
        new_line = {col: [np.nan] for col in columns}
        new_line["flight_id"] = [flight_id]  # Set the flight_id column

        # Create the new DataFrame
        new_df = pd.DataFrame(new_line)

        # Append the DataFrame to the same .csv file
        new_df.to_csv(output_csv_file, mode='a', header=write_header, index=False)
        # print("No-CoCiP added to output file: ", flight_id)

        # After the first iteration, ensure the header is not written again
        write_header = False

        # Optional: Delete variables to free up memory
        del new_line, new_df

        pass  # Skip this part of the code    