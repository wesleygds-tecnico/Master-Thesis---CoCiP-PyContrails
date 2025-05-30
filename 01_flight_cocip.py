# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script analyzes and visualizes the environmental effects of aircraft contrails based on flight trajectory data. 
#     It uses the pycontrails library to simulate contrail formation using the CoCiP (Contrail Cirrus Prediction) model 
#     and meteorological data from ERA5.
# 
# Inputs:
#     - `flight_data_sample_four.csv`: CSV file containing flight trajectory data including timestamp, position, and altitude.
#     - `flight_id`: Identifier of the flight to be analyzed (e.g., 'PGT14SP_12284').
# 
# Outputs:
#     - Plots of:
#         * Flight trajectory (latitude vs longitude)
#         * Altitude vs time
#         * Additional flight parameters vs time
#         * Environmental forcing (EF) and RHi maps along the trajectory
#     - A CSV file `<flight_id>_flight_data_sample_four.csv` containing CoCiP model results for the selected flight.
# 
# Dependencies:
#     - numpy
#     - pandas
#     - matplotlib
#     - pycontrails
#         * Flight, ERA5, Cocip, ConstantHumidityScaling classes
#     - A working internet connection or pre-cached ERA5 data is required to access meteorological datasets.
# 
# Additional Comments:
#     - This script converts flight altitude from feet to meters before modeling.
#     - It filters flight data for a specific `flight_id`, ensuring only one flight trajectory is processed.
#     - It plots flight attributes and evaluates the potential for contrail formation and their climate impact using the CoCiP model.
#     - RHi scaling is applied based on literature (Teoh et al. 2020, 2022) to adjust humidity measurements.
#     - The script includes data caching and robust error handling for ERA5 downloads.
#     - Output data is saved and visualized if contrail formation is detected.
# 
# Note:
#     - Ensure the ERA5 data license and API credentials are configured in your environment before execution.
#     - Change the `flight_id` as needed to analyze a different flight from the dataset.
# =========================================================================================================================================

import numpy as np
import pandas as pd
from pycontrails import Flight
from matplotlib import pyplot as plt
from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip
from pycontrails.models.humidity_scaling import ConstantHumidityScaling

data        =  pd.read_csv("data\\traffic\\flight_data_sample_four.csv")
flight_id   = 'PGT14SP_12284'
#flight_id   = 'MSR525_001'

# Construct the file name using the variable
output_file = f"{flight_id}_flight_data_sample_four.csv"


# Load flight from csv file
attrs   = {
            "flight_id": flight_id,
            "aircraft_type": "A320"
            }

# Filter the DataFrame for rows where 'column_name' matches a specific value
filtered_data = data[data['flight_id'] == flight_id]

# Convert the timestamp column to datetime
filtered_data['time'] = pd.to_datetime(data['time'])

filtered_data['altitude'] = filtered_data['altitude']*0.3048

print("Filtered data: ", filtered_data)

flight = Flight(filtered_data, attrs=attrs)

latitude, longitude, altitude = flight["latitude"], flight["longitude"], flight["altitude"]

time = flight["time"]

# List of attributes to exclude from plotting
exclude_keys = ["aircraft_type", "flight_id", "icao24", "time", "latitude", "longitude"]

# Plot Latitude vs Longitude
plt.figure(figsize=(10, 6))
plt.plot(longitude, latitude, marker="o", linestyle="-", color="blue")
plt.title("Flight Trajectory: Latitude vs Longitude")
plt.xlabel("Longitude (degrees)")
plt.ylabel("Latitude (degrees)")
plt.grid(True)

# Plot Altitude vs Time
plt.figure(figsize=(10, 6))
plt.plot(time, altitude, marker="o", linestyle="-", color="green")
plt.title("Altitude vs Time")
plt.xlabel("Time")
plt.ylabel("Altitude (meters)")
plt.grid(True)


# Loop through all attributes in the `flight` object
for key in flight.data.keys():
    if key in exclude_keys:
        # Skip plotting excluded keys
        continue

    # Get the attribute data
    data = flight[key]

    # Create a new figure for each attribute
    plt.figure(figsize=(10, 6))
    plt.plot(time, data, marker='o', linestyle='-', label=key, markersize=5)  # Points + lines
    plt.title(f"{key.capitalize()} vs Time")
    plt.xlabel("Time")
    plt.ylabel(key.capitalize())
    plt.legend()
    plt.grid(True)
    # plt.show()

time_bounds = (str(flight["time"].min()), str(flight["time"].max()))
# pressure_levels = (1000, 950, 900, 850, 800, 750, 700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 200)
pressure_levels = (700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 200, 150, 100, 50)

era5pl = ERA5(
    time=time_bounds,
    variables=Cocip.met_variables + Cocip.optional_met_variables,
    pressure_levels=pressure_levels,
)
era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

# download data from ERA5 (or open from cache)
met = era5pl.open_metdataset()
rad = era5sl.open_metdataset()

params = {
    "dt_integration": np.timedelta64(10, "m"),
    # The humidity_scaling parameter is only used for ECMWF ERA5 data
    # based on Teoh 2020 and Teoh 2022 - https://acp.copernicus.org/preprints/acp-2022-169/acp-2022-169.pdf
    # Here we use an example of constantly scaling the humidity value by 0.99
    "humidity_scaling": ConstantHumidityScaling(rhi_adj=0.99),
}

cocip = Cocip(met=met, rad=rad, params=params)

output_flight = cocip.eval(source=flight)

df = output_flight.dataframe
df.head()

print("CoCiP Output: ", df.head())

df.plot.scatter(
    x="longitude",
    y="latitude",
    c="ef",
    cmap="coolwarm",
    vmin=-1e13,
    vmax=1e13,
    title="EF generated by flight waypoint",
)
#plt.show()

if hasattr(cocip.contrail, "head"):
    # Code to execute if 'cocip.contrail' has the 'head' attribute
    print("cocip.contrail has the attribute 'head'")
    # Add your code here that shouldn't be skipped
    df.plot.scatter(
        x="longitude",
        y="latitude",
        c="rhi_1",
        cmap="magma",
        title="Initial RHi along flight path",
    )

    cocip.contrail.head()

    contrail = cocip.contrail
    contrail.head()

    print("CoCiP Output: ", contrail.head())

    ax = plt.axes()

    cocip.source.dataframe.plot(
        "longitude",
        "latitude",
        color="k",
        ax=ax,
        label="Flight path",
    )
    cocip.contrail.plot.scatter(
        "longitude",
        "latitude",
        c="rf_lw",
        cmap="Reds",
        ax=ax,
        label="Contrail LW RF",
    )
    ax.legend()

    # Convert to a DataFrame
    contrail_df = pd.DataFrame(cocip.contrail)

    # Export the DataFrame to a CSV file
    contrail_df.to_csv(output_file, index=False)

    print(f"cocip.contrail has been successfully exported to {output_file}")    

    plt.show()
else:
    # Code to execute if 'cocip.contrail' does not have the 'head' attribute
    print("cocip.contrail does not have the attribute 'head'")
    # Add your code here that should be skipped if the condition is not met
    pass  # Skip this part of the code