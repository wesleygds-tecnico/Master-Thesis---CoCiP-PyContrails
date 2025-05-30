# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes flight emissions data to visualize environmental impact metrics 
#     (e.g., Energy Forcing - EF, Radiative Forcing - RF) along flight trajectories on a geographic map, 
#     and plots time series for EF and RF parameters over the flight duration.
# 
# Inputs:
#     - CSV file containing flight data including longitude, latitude, ef (energy forcing), 
#       flight identifiers, timestamps, and radiative forcing parameters.
#     - Shapefile of world country borders for geographic plotting.
#     - A predefined list of callsigns to filter the flight data.
#     - Airports data with coordinates for reference points on the maps.
# 
# Outputs:
#     - Geographic plots for each flight date showing the flight path colored by EF per segment (MJ/m).
#     - Time series plots of EF over the day for each callsign and date.
#     - Time series plots of RF parameters (shortwave, longwave, net) over time for each flight.
#     - All plots saved as PNG and PDF files with descriptive filenames including date, callsign, and SAF percentage.
# 
# Additional Comments:
#     - Uses GeoPandas and shapely for geographic data handling and mapping.
#     - Normalizes EF data per segment length to visualize emissions intensity spatially.
#     - Time data is processed into seconds since midnight for time series consistency.
#     - The script is designed for flights within a specific longitude and latitude bounding box.
#     - Font and plotting styles are set globally for consistent and clear visualization.
#     - The SAF_pct variable allows for distinguishing plots by Sustainable Aviation Fuel percentage scenarios.
#     - Airports are plotted as points with labels for spatial context.
#     - Color maps and legends are used to convey emission intensity visually.
#     - Code assumes CSV has specific columns (callsign, longitude, latitude, ef, flight_id, time, rf_sw_mean, rf_lw_mean, rf_net_mean).
#     - Ensure that required libraries (pandas, numpy, matplotlib, geopandas, shapely) are installed before running.
# =========================================================================================================================================

import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
import geopandas as gpd
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from shapely.wkt import loads
import matplotlib as mpl

# Use LaTeX-style font for all text in the plot
mpl.rcParams["font.family"] = "serif"  # Use a serif font (LaTeX-like)
mpl.rcParams["font.size"] = 30  # Adjust global font size
mpl.rcParams["text.usetex"] = False  # Set to True if you have LaTeX installed

fontsize = 30

# Define the file path
file_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\2025-01-01_2025-01-14_by_airframe_SAF_0_pct_Opensky_checked_processed_cocip_main.csv"

SAF_pct = 0

shapefile_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\config_files\\geoplot\\ne_10m_admin_0_countries.shp"

# Load the shapefile into a GeoDataFrame
world = gpd.read_file(shapefile_path)

# List of callsigns to keep
selected_callsigns = ["AEA1065"]  # Add your specific callsigns here

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path, low_memory=False)

# Filter the DataFrame to keep only selected callsigns
df = df[df["callsign"].isin(selected_callsigns)]

vmin=df["ef"].min()
vmax=df["ef"].max()

df["ef_per_segment"] = df["ef"]/df["segment_length"]

# Define airports data - AZU8708
airports = pd.DataFrame({
    "Airport": ["MAD", "MXP"],
    "Coordinates": ["POINT(-3.560833 40.472222)", "POINT(8.723056 45.63)"]
})

# Convert "Coordinates" to GeoDataFrame
airports["geometry"] = airports["Coordinates"].apply(loads)
airports = gpd.GeoDataFrame(airports, geometry="geometry")

# Define plot limits (adjust these values based on your data or region of interest)
lon_min, lon_max =  -6, 12      # Longitude range
lat_min, lat_max =  38, 48     # Latitude range

grouped = df.groupby('flight_id')  # Group the DataFrame by 'flight_id'
# Assume df is your dataframe containing flight data with columns: 
# 'longitude', 'latitude', 'ef', and 'timestamp'
# Make sure the 'timestamp' is in datetime format
df["time"] = pd.to_datetime(df["time"])
# Extract the date from the timestamp (if necessary)
df["date"] = df["time"].dt.date
# Extract the time part (ignoring the date) for each timestamp
df["hour"] = df["time"].dt.strftime('%H:%M')  # Format as hour:minute
# Convert time to seconds since midnight
df["seconds_since_midnight"] = df["time"].dt.hour * 3600 + df["time"].dt.minute * 60 + df["time"].dt.second
# Group by date

grouped_by_date = df.groupby("date")    
#for flight_id, group in grouped:
for date, group in grouped_by_date:
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    # Normalize the 'ef' values to match color scale (converted to TJ)
    vmin = group["ef_per_segment"].min() / 1e6
    vmax = group["ef_per_segment"].max() / 1e6
    norm = Normalize(vmin=vmin, vmax=vmax)
    # Set background color for water
    ax.set_facecolor("lightblue")  
    # Plot the world map
    world.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)
    # Plot airports
    airports.plot(ax=ax, color="black", markersize=30, marker="o", label="Airports")
    # Add airport names as text labels
    for _, row in airports.iterrows():
        ax.text(
            row.geometry.x + 0.10, row.geometry.y + 0.1750,  
            row["Airport"],  
            fontsize=fontsize, color="black", fontweight="regular",
            horizontalalignment='center', verticalalignment='bottom',
            fontfamily="serif"
        )
    # Convert EF values to MJ for the scatter plot
    ef_scaled = group["ef_per_segment"] / 1e6  
    # Scatter plot the flight data
    scatter = ax.scatter(
        x=group["longitude"],
        y=group["latitude"],
        c=ef_scaled,  
        cmap="coolwarm",
        vmin=vmin,
        vmax=vmax,
        label=f"Flight on {date}",
        alpha=1,
        edgecolor=None,
    )
    # Add colorbar with dynamically adjusted limits
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label(r"EF [MJ/m]", fontsize=fontsize, fontfamily="serif")
    # Plot the trajectory lines using the same color scale
    for i in range(len(group) - 1):
        ax.plot(
            [group["longitude"].iloc[i], group["longitude"].iloc[i+1]],
            [group["latitude"].iloc[i], group["latitude"].iloc[i+1]],
            color=plt.cm.coolwarm(norm(ef_scaled.iloc[i])),
            linewidth=0.25,  
            alpha=1  
        )        
    # Customize the plot
    ax.set_xlim(lon_min, lon_max)  
    ax.set_ylim(lat_min, lat_max)  
    ax.set_xlabel(r"Longitude [º]", fontsize=fontsize, fontfamily="serif")
    ax.set_ylabel(r"Latitude [º]", fontsize=fontsize, fontfamily="serif")
    ax.grid(True, linewidth=0.1)  
    # Save the plot
    plot_filename = f"flight_data_{date}"
    fig.savefig(f"{plot_filename}_{selected_callsigns}_{str(SAF_pct)}_SAF_EF_per_m_trajectory.png", dpi=300, bbox_inches="tight", format="png")
    fig.savefig(f"{plot_filename}_{selected_callsigns}_{str(SAF_pct)}_SAF_EF_per_m_trajectory.pdf", bbox_inches="tight", format="pdf")

# Group by both date and callsign
for (date, callsign), group in df.groupby(["date", "callsign"]):
    plt.figure(figsize=(12, 6))

    # Plot EF (Energy Forcing) over the time of day (in hours)
    plt.plot(
        group["seconds_since_midnight"] / 3600,  # Time in hours
        group["ef"] / 1e12,                      # EF in megajoules
        linestyle="-",
        marker="o",
        markersize=6,
        label=f"{callsign}",
        alpha=0.7
    )

    # Customize and save the plot
    plt.xlabel(r"Time [h]", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"EF [TJ]", fontsize=fontsize, fontfamily="serif")
    # plt.legend(fontsize=fontsize * 0.9)
    plt.grid(True, linewidth=0.3)
    #plt.xlim(20, 24)  # Limit time range from 12h to 21h

    # Save with both date and callsign in filename
    sanitized_callsign = str(callsign).strip().replace("/", "_").replace(" ", "_")
    plt.savefig(f"energy_forcing_vs_time_{sanitized_callsign}_{date}_{SAF_pct}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"energy_forcing_vs_time_{sanitized_callsign}_{date}_{SAF_pct}.pdf", bbox_inches="tight", format="pdf")

# Iterate over the grouped data by flight ID
for flight_id, group in df.groupby("flight_id"):
    # Create a new figure for each flight
    plt.figure(figsize=(12, 6))

    # Plot each parameter over time
    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rf_sw_mean"],  
        linestyle="-", marker="o", markersize=5,
        label="RF Shortwave Mean", alpha=0.7
    )

    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rf_lw_mean"],  
        linestyle="-", marker="s", markersize=5,
        label="RF Longwave Mean", alpha=0.7
    )

    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rf_net_mean"],  
        linestyle="-", marker="d", markersize=5,
        label="RF Net Mean", alpha=0.7
    )

    # Customize the plot
    plt.xlabel(r"Time [h]")
    plt.ylabel(r"RF [W/m$^{2}$]")
    # plt.title(r"Radiative Forcing Over Time for Flight" + f"{flight_id}")
    # plt.xlim(20, 24)  # Limit time range from 12h to 21h
    plt.legend(fontsize=fontsize*0.75)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  

    # Save the figure uniquely for each flight
    plot_filename = f"rf_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}_{str(SAF_pct)}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}_{str(SAF_pct)}.pdf", bbox_inches="tight", format="pdf")