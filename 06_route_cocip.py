# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes historical aircraft trajectory data and computes contrail formation and radiative forcing estimates 
#     using the CoCiP (Contrail Cirrus Prediction) model from the PyContrails library. It automates the download of meteorological 
#     data from ECMWF ERA5, integrates the data with flight trajectory records, and outputs the estimated contrail data and summary 
#     statistics for post-analysis.
# 
# Inputs:
#     - Flight trajectory .csv files (with OpenSky or Flightradar24 format) located in a specified input directory.
#     - Each file must include flight trajectory data such as latitude, longitude, altitude, groundspeed, heading, timestamp, 
#       and a unique flight_id.
#     - ERA5 atmospheric datasets, automatically downloaded through the PyContrails API depending on the time range of each flight.
# 
# Outputs:
#     - `output_csv_file`: A CSV file containing detailed CoCiP results per flight waypoint. Saved as:
#         "2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_main.csv"
#     - `summary_output_csv_file`: A summary CSV file containing aggregated contrail and radiative forcing metrics per flight.
#         "2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_summary.csv"
# 
# Key Features and Comments:
#     - The script avoids reprocessing previously analyzed flights by checking the existing `output_csv_file`.
#     - Flight data is filtered and processed individually using the PyContrails `Flight` and `Cocip` classes.
#     - ERA5 meteorological data is fetched per flight based on its time bounds, with retry logic for robustness.
#     - CoCiP model is parameterized with a constant relative humidity scaling (rhi_adj = 0.99), based on Teoh et al., 2020/2022.
#     - If contrails are not generated or if an error occurs, the script still records the flight_id with NaNs for traceability.
#     - Designed to be efficient for batch processing of historical flights over extended periods (e.g., one week of data).
#     - The `tqdm` library is used to visualize progress in the terminal.
#     - Requires an internet connection to download ERA5 datasets unless cached.
# =========================================================================================================================================

import os
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from pycontrails import Flight
from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip
from pycontrails.models.humidity_scaling import ConstantHumidityScaling
from pycontrails.models.cocip import (contrail_flight_summary_statistics, flight_waypoint_summary_statistics)

# Define the list of columns
columns = [
    "waypoint", "icao24", "callsign", "latitude", "longitude", "altitude", "groundspeed", "heading", "flight_id",
    "pressure_hPa", "u_wind", "v_wind", "heading_rad", "GS_x", "GS_y", "true_airspeed", "aircraft_type", "wingspan", "nvpm_ei_n",
    "engine_efficiency", "fuel_flow", "aircraft_mass", "time", "level", "air_pressure", 
    "air_temperature", "specific_humidity", "u_wind", "v_wind", "rhi", "segment_length", "sin_a", 
    "cos_a", "G", "T_sat_liquid", "rh", "rh_critical_sac", "sac", "T_critical_sac", "width", "depth", 
    "rhi_1", "air_temperature_1", "specific_humidity_1", "altitude_1", "persistent_1", "rho_air_1", 
    "iwc_1", "n_ice_per_m_1", "ef", "contrail_age", "sdr_mean", "rsr_mean", "olr_mean", "rf_sw_mean", 
    "rf_lw_mean", "rf_net_mean", "cocip"
]

# Define paths
input_folder                = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\Opensky\\analysis_LA\\Flightradar24"
output_csv_file             = "2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_main.csv"
summary_output_csv_file     = "2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_summary.csv"

# Ensure headers are written only if the files do not exist or are empty
write_header_main = not os.path.exists(output_csv_file) or os.stat(output_csv_file).st_size == 0
write_header_summary = not os.path.exists(summary_output_csv_file) or os.stat(summary_output_csv_file).st_size == 0

processed_flights = set()  # Track processed flights

# Check if the file exists
if os.path.exists(output_csv_file):
    # Read the existing flight IDs from the CSV
    existing_flights_df = pd.read_csv(output_csv_file)
    existing_flight_ids = existing_flights_df["flight_id"].unique()  # Get unique flight IDs
    write_header_main   = False
else:
    # If the file does not exist, initialize an empty list of flight IDs
    existing_flight_ids = []

# Process all .csv files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_folder, file_name)
        print(f"\n Processing file: {file_path}")

        data = pd.read_csv(file_path, low_memory=False)
        data['time'] = pd.to_datetime(data['time'], errors='coerce') #- OpenSky
        #data['time'] = pd.to_datetime(data['time'], errors='coerce') # - Flight radar
        # print('data: ', data)

        unique_flights_list     = data['flight_id'].unique().tolist()
        filtered_flights_list   = [fid for fid in unique_flights_list if fid not in existing_flight_ids]

        # Loop through each unique flight ID
        for flight_id in tqdm(filtered_flights_list, desc="Processing flights", unit="flight"):
            # Filter data for the specific flight ID
            flight_data = data[data["flight_id"] == flight_id]

            print("flight_data: ", flight_data)

            # Determine the time bounds based on the minimum and maximum times for the specific flight
            time_bounds = (
                flight_data["time"].min().tz_localize(None),  # Remove timezone info - OpenSky
                flight_data["time"].max().tz_localize(None) + pd.Timedelta(hours=36)  # Add a time buffer - OpenSky
            )

            # Extract the aircraft_type from the first row of the flight_group
            aircraft_type = flight_data["aircraft_type"].iloc[0]  

            # Load flight group into a Flight object
            attrs = {"flight_id": flight_id, "aircraft_type": aircraft_type}

            # Pressure levels for ERA5 (for example)
            pressure_levels = (800, 775, 750, 700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 225, 200, 175, 150, 125, 100)

            # Create ERA5 objects for the flight
            era5pl = ERA5(
                time            = time_bounds,
                variables       = Cocip.met_variables + Cocip.optional_met_variables,
                pressure_levels = pressure_levels,
            )
            era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

            max_retries = 3
            retry_interval = 30
            for attempt in range(1, max_retries + 1):
                try:
                    # Download data from ERA5 (or open from cache)
                    met = era5pl.open_metdataset()
                    rad = era5sl.open_metdataset()
                    break  # Exit the loop if no error occurs
                except Exception as e:
                    print(f"Error occurred: {e}")
                    if attempt < max_retries:
                        print(f"Retrying in {retry_interval} seconds...")
                        time.sleep(retry_interval)
                    else:
                        print("Max retries reached. Unable to download data.")

            # Create a Flight object
            flight = Flight(flight_data, attrs=attrs)

            params = {
                "dt_integration": np.timedelta64(10, "m"),
                # The humidity_scaling parameter is only used for ECMWF ERA5 data
                # based on Teoh 2020 and Teoh 2022 - https://acp.copernicus.org/preprints/acp-2022-169/acp-2022-169.pdf
                # Here we use an example of constantly scaling the humidity value by 0.99
                "humidity_scaling": ConstantHumidityScaling(rhi_adj=0.99),
            }

            print("\n Assessing: ", flight_id)

            try:
                cocip = Cocip(met=met, rad=rad, params=params)
                output_flight = cocip.eval(source=flight)
            
                if output_flight is None or cocip.contrail is None:
                    print(f"\n Warning: CoCiP did not generate contrails for flight {flight_id}")
            
                    # Create a DataFrame with NaN values, except for flight_id
                    new_line = {col: [np.nan] for col in columns}
                    new_line["flight_id"] = [flight_id]  
            
                    new_df = pd.DataFrame(new_line)
            
                    # Append to the output CSV
                    new_df.to_csv(output_csv_file, mode='a', header=write_header_main, index=False)
                    write_header_main = False  # Prevent rewriting headers
            
                    del new_line, new_df
            
                else:
                    df = output_flight.dataframe
            
                    waypoint_summary = flight_waypoint_summary_statistics(cocip.source, cocip.contrail)
                    flight_summary = contrail_flight_summary_statistics(waypoint_summary)
            
                    # Save results only if contrails were detected
                    df.to_csv(output_csv_file, mode='a', header=write_header_main, index=False)
                    print(f"\n CoCiP added to output file: {flight_id}")
            
                    flight_summary.to_csv(summary_output_csv_file, mode='a', header=write_header_summary, index=False)
                    print(f"\n Summary added to output file: {flight_id}")
            
                    write_header_main = False  # Ensure headers are written only once
                    write_header_summary = False  
            
                    del df, output_flight, cocip, waypoint_summary, flight_summary
            
                processed_flights.add(flight_id)
            
            except Exception as e:
                print(f"Error processing flight {flight_id}: {e}")
            
                # Create a DataFrame with NaN values, marking the error
                new_line = {col: [np.nan] for col in columns}
                new_line["flight_id"] = [flight_id + "_ERROR"]
            
                new_df = pd.DataFrame(new_line)
            
                # Append to the output CSV
                new_df.to_csv(output_csv_file, mode='a', header=write_header_main, index=False)
                write_header_main = False  
            
                del new_line, new_df
            
            finally:
                if flight_id not in processed_flights:
                    print(f"Unexpected failure for flight {flight_id}")