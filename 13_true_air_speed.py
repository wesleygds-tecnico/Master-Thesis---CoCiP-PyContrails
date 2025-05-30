# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes flight trajectory data to calculate the True Airspeed (TAS) of aircraft flights using 
#     meteorological data from ERA5 reanalysis. It integrates aircraft positional and altitude data with interpolated 
#     wind data (eastward and northward wind components) at corresponding pressure levels and times to compute TAS.
# 
# Inputs:
#     - CSV files in a specified folder containing flight data with columns including 'time', 'latitude', 'longitude', 
#       'altitude' (in feet), 'flight_id', 'groundspeed', and 'heading'.
#     - ERA5 meteorological data obtained via the pycontrails ERA5 interface for specified pressure levels and time bounds.
# 
# Outputs:
#     - A CSV file containing original flight data enriched with interpolated wind components (u_wind, v_wind) and 
#       the calculated true airspeed ('true_airspeed') per flight, saved to a specified output path.
# 
# Additional comments:
#     - The pressure levels used for ERA5 data selection cover a typical range relevant for commercial flight altitudes.
#     - The altitude in feet is converted to pressure altitude in hPa using the barometric formula for interpolation.
#     - Interpolation of wind components uses nearest neighbor selection on time, lat, lon, and pressure level.
#     - The script handles missing or problematic data gracefully by setting wind values to NaN.
#     - True airspeed is calculated by vector subtraction of wind components from groundspeed vectors, considering heading.
#     - The script writes results incrementally to a CSV file, ensuring the header is only written once.
#     - It assumes that ERA5 data files are cached or will be downloaded on-demand via pycontrails.
#     - Before running, adjust input and output folder paths as per the user's directory structure.
# =========================================================================================================================================


import os
import xarray as xr
import pandas as pd
import numpy as np
from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip

# Pressure levels for ERA5 (for example)
pressure_levels = (900, 875, 850, 825, 800, 775, 750, 700, 650, 600, 550,
                    500, 450, 400, 350, 300, 250, 225, 200, 175, 150, 125,
                    100)
# 1000/975/950/925/900/875/850/825/800/775/750/700/650/600/550/500/450/400/350/300/250/225/200/175/150/125/100/70/50/30/20/10/7/5/3/2/1
# Determine the time bounds based on the minimum and maximum times for the specific flight
time_bounds = (
    '2025-01-01 00:00:00',  # Start time
    '2025-01-09 00:00:00'   # End time with buffer
)

print('time_bounds: \n', time_bounds)

print('Cocip.met_variables: \n', Cocip.met_variables)
print('Cocip.optional_met_variables: \n', Cocip.optional_met_variables)

# Create ERA5 objects for the flight
era5pl = ERA5(
    time=time_bounds,
    variables=Cocip.met_variables + Cocip.optional_met_variables,
    pressure_levels=pressure_levels,
)

era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

# Download data from ERA5 (or open from cache)
met = era5pl.open_metdataset()  # This already returns an xarray dataset

# Convert MetDataset to xarray.Dataset
met_xr = met.data  # Extracts xarray.Dataset from MetDataset

# Define input and output folder paths
input_folder = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\Opensky\\analysis_LA\\Flightradar24"
output_file = os.path.join("C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5",
                            "2025_01_01-2025_01_07_LA_flight_id_TAS.csv")

# List all CSV files in the folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

# Create or overwrite the output file at the beginning
open(output_file, 'w').close()
first_write = True  # To write the header only once

# Initialize an empty list to store DataFrames
df_list = []

for file in csv_files:
    input_path = os.path.join(input_folder, file)
    
    print(f"Processing: {file}")

    # Read the CSV file
    df = pd.read_csv(input_path, low_memory=False)

    # Convert time column to datetime format
    df["time"] = pd.to_datetime(df["time"], format="mixed", errors="coerce")
    df["time"] = df["time"].dt.tz_localize(None)

    # Convert altitude to pressure level
    #df["altitude_m"] = df["altitude"] * 0.3048  
    df["pressure_hPa"] = 1013.25 * (1 - (df["altitude"] / 44330)) ** 5.255  

    # Convert DataFrame to xarray for interpolation
    df_xr = df.set_index("time").to_xarray()

    # Assume `met_xr` is available as an xarray.Dataset
    # Perform wind interpolation

    # Process data per flight_id
    for flight_id, sub_df in df.groupby("flight_id"):
        u_wind_list = []
        v_wind_list = []

        for _, row in sub_df.iterrows():
            try:
                u_wind = met_xr["eastward_wind"].sel(
                    time=row["time"], latitude=row["latitude"], longitude=row["longitude"],
                    level=row["pressure_hPa"], method="nearest"
                ).values
                v_wind = met_xr["northward_wind"].sel(
                    time=row["time"], latitude=row["latitude"], longitude=row["longitude"],
                    level=row["pressure_hPa"], method="nearest"
                ).values
            except Exception as e:
                u_wind, v_wind = np.nan, np.nan  # Handle errors gracefully

            u_wind_list.append(u_wind)
            v_wind_list.append(v_wind)

        sub_df["u_wind"] = u_wind_list
        sub_df["v_wind"] = v_wind_list

        if "groundspeed" not in sub_df.columns or "heading" not in sub_df.columns:
            raise ValueError("Missing 'groundspeed' or 'heading' column in flight data.")

        sub_df["heading_rad"] = np.radians(sub_df["heading"])
        sub_df["GS_x"] = sub_df["groundspeed"] * np.sin(sub_df["heading_rad"])
        sub_df["GS_y"] = sub_df["groundspeed"] * np.cos(sub_df["heading_rad"])

        TAS_values = ((sub_df["GS_x"] - sub_df["u_wind"])**2 + (sub_df["GS_y"] - sub_df["v_wind"])**2).astype(np.float64)
        sub_df["true_airspeed"] = np.sqrt(TAS_values)

        # Append to CSV
        sub_df.to_csv(output_file, mode='a', index=False, header=first_write)
        first_write = False  # After first write, don't write the header again