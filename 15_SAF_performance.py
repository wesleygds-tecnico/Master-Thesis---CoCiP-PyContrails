# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Author: [Your Name or Organization]  # Replace with actual author name if desired
# Purpose: 
#     This script processes flight data to model and evaluate contrail formation using 
#     the CoCiP (Contrail Cirrus Prediction) model. It incorporates meteorological data from 
#     ERA5 reanalysis datasets, simulates the effects of sustainable aviation fuel (SAF) blending, 
#     and generates both detailed waypoint-level and overall flight summary statistics for contrail characteristics.
# 
# Inputs:
#     - Flight data CSV file containing flight trajectory and aircraft parameters 
#       (example: "2025_01_01-2025_01_14_flight_id_filtered_airframe_checked_TAS_processed.csv")
#     - ERA5 meteorological data for specified time bounds and pressure levels, 
#       loaded via the pycontrails ERA5 interface.
# 
# Outputs:
#     - CSV file "SAF_output_2.csv" containing the detailed contrail simulation results for the selected flight.
#     - CSV file "SAF_output_summary_2.csv" containing summary statistics for the contrail properties of the flight.
#     - (Optional) Matplotlib-generated plots for contrail properties over time (commented out).
# 
# Key Steps:
#     1. Define time bounds and ERA5 pressure levels for meteorological data retrieval.
#     2. Load ERA5 meteorological and radiation datasets for the specified time window.
#     3. Load and filter flight trajectory data for a specific flight ID.
#     4. Create a Flight object from the filtered flight data.
#     5. Apply a 25% Sustainable Aviation Fuel (SAF) blend to the flight fuel properties.
#     6. Run the CoCiP contrail model with humidity scaling and aircraft performance parameters.
#     7. Extract contrail simulation outputs and save detailed and summary results to CSV files.
#     8. (Optional) Plot contrail number vs time for visualization purposes.
# 
# Additional Comments:
#     - The humidity scaling uses a constant scaling factor (0.99) based on recent research (Teoh 2020, 2022).
#     - The script assumes familiarity with the pycontrails package and its data structures.
#     - Pressure levels for ERA5 are defined to cover the typical altitudes relevant to commercial flights.
#     - The script currently processes one example flight ("AFR1342_3891") but can be adapted for batch processing.
#     - Plotting code is provided but commented out; uncomment to generate visual outputs.
# =========================================================================================================================================

import numpy as np
import pandas as pd
from pycontrails import SAFBlend
from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip
from pycontrails.models.humidity_scaling import ConstantHumidityScaling
from pycontrails import Flight
from pycontrails.models.ps_model import PSFlight
from pycontrails.models.cocip import (contrail_flight_summary_statistics, flight_waypoint_summary_statistics)

# Determine the time bounds based on the minimum and maximum times for the specific flight
time_bounds = (
    '2025-01-01 00:00:00',  # Remove timezone info - OpenSky
    '2025-01-03 00:00:00'  # Add a time buffer - OpenSky
)

# Pressure levels for ERA5 (for example)
pressure_levels = (900, 875, 850, 825, 800, 775, 750, 700, 650, 600, 550,
                    500, 450, 400, 350, 300, 250, 225, 200, 175, 150, 125,
                    100)

# Create ERA5 objects for the flight
era5pl = ERA5(
            time            = time_bounds,
            variables       = Cocip.met_variables + Cocip.optional_met_variables,
            pressure_levels = pressure_levels,
)

era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

met = era5pl.open_metdataset()
rad = era5sl.open_metdataset()

file_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\traffic\\Opensky\\analysis_by_airframe\\2025_01_01-2025_01_14_flight_id_filtered_airframe_checked_TAS_processed.csv"

data = pd.read_csv(file_path, low_memory=False)

# Example flight
# Filter data for the specific flight ID
flight_data = data[data["flight_id"] == "AFR1342_3891"]

# Extract the aircraft_type from the first row of the flight_group
aircraft_type = flight_data["aircraft_type"].iloc[0]  

# Load flight group into a Flight object
attrs = {"flight_id": "AFR1342_3891", "aircraft_type": aircraft_type}

print("flight_data: ", flight_data)

key_attrs  = ["icao24", "callsign", "time", "latitude", "longitude",
              "altitude", "vertical_rate", "groundspeed", "flight_id",
              "heading", "pressure_hPa", "u_wind", "v_wind", "heading_rad",
              "GS_x", "GS_y", "true_airspeed", "aircraft_type", "wingspan"]

flight_data = flight_data[key_attrs]

fl = Flight(data=flight_data, attrs=attrs)

saf_fuel = SAFBlend(pct_blend=25)  # 25% SAF blend

fl.fuel = saf_fuel

cocip = Cocip(
    met=met,
    rad=rad,
    humidity_scaling=ConstantHumidityScaling(rhi_adj=0.99),
    aircraft_performance=PSFlight(),
)

output_flight = cocip.eval(source=fl)

df = output_flight.dataframe

print(df)

# Save results only if contrails were detected
df.to_csv("SAF_output_2.csv", index=False)

waypoint_summary    = flight_waypoint_summary_statistics(cocip.source, cocip.contrail)
flight_summary      = contrail_flight_summary_statistics(waypoint_summary)

flight_summary.to_csv("SAF_output_summary_2.csv", index=False)

# import matplotlib.pyplot as plt
# 
# # Ensure time is a datetime or float-like series
# time = output_flight["time"]
# nvpm = output_flight["nvpm_number"]
# 
# # Create the plot
# plt.figure(figsize=(10, 6))
# plt.plot(time, nvpm, marker='o', linestyle='-', color='darkblue')
# plt.title("nvpm_number vs Time")
# plt.xlabel("Time")
# plt.ylabel("nvpm_number")
# plt.grid(True)
# plt.tight_layout()
# 
# # Save the figure
# plt.savefig("nvpm_number_vs_time.png")
# plt.savefig("nvpm_number_vs_time.pdf")
# 
# # Ensure time is a datetime or float-like series
# time = output_flight["time"]
# nvpm = output_flight["nvpm_number"]
# 
# # Create the plot
# plt.figure(figsize=(10, 6))
# plt.plot(time, nvpm, marker='o', linestyle='-', color='darkblue')
# plt.title("nvpm_number vs Time")
# plt.xlabel("Time")
# plt.ylabel("nvpm_number")
# plt.grid(True)
# plt.tight_layout()
# 
# # Save the figure
# plt.savefig("nvpm_number_vs_time.png")
# plt.savefig("nvpm_number_vs_time.pdf")
# 
# # Display the plot
# plt.show()