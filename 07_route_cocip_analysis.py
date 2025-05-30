# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: 
#     This script processes and visualizes flight trajectory data from a CSV file,
#     plotting geographic flight paths with emission factor (EF) and relative humidity index (RH_i)
#     overlays on a world map focused on a specific latitude and longitude range (Latin America region).
#     
# Inputs:
#     - shapefile_path: Path to a shapefile containing country borders (used to plot the world map)
#     - file_path: Path to the CSV file containing flight data, with columns such as 'flight_id', 'longitude', 
#     'latitude', 'ef', 'rhi_1', 'time', and 'segment_length'
#     - selected_callsigns: List of callsign strings to filter and visualize specific flights
#     - airports: DataFrame with airports and their coordinates, converted to GeoDataFrame for plotting
# 
# Outputs:
#     - Multiple PNG and PDF files of plots saved to the current directory, showing:
#         * Flight trajectories colored by EF per segment (MJ/m)
#         * Flight trajectories colored by relative humidity index (RH_i)
#     - Printed messages about data loading success or errors
# 
# Additional comments:
#     - The script uses GeoPandas for spatial data handling and Matplotlib for plotting.
#     - EF values are normalized and converted to MJ/m for color scaling.
#     - Airport locations are marked and labeled on the map.
#     - The plotting region is defined for a specific geographic bounding box (Latin America).
#     - The script handles time conversion and grouping by flight and date to create daily flight visualizations.
#     - The code includes commented out blocks for alternative airport data and origin/destination airports for flexibility.
#     - LaTeX-style fonts are configured but not required to have LaTeX installed (usetex=False).
#     - Error handling is included for file loading.
#     - This is primarily a visualization tool to help analyze flight emission data spatially and temporally.
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

shapefile_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\config_files\\geoplot\\ne_10m_admin_0_countries.shp"

# Load the shapefile into a GeoDataFrame
world = gpd.read_file(shapefile_path)

# Define plot limits (adjust these values based on your data or region of interest)
lon_min, lon_max =  -102.5, -72.5     # Longitude range
lat_min, lat_max =  5, 22.5     # Latitude range

# Define the file path
file_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_main.csv"

# List of callsigns to keep
selected_callsigns = [
    # "AFR11FF",    # EUROCONTROL    
    # "AEA14ZM",    # EUROCONTROL
    # "AEA53HU",    # EUROCONTROL
    # "AMX690",       # Latin-America
    # "AZU4577",       # Latin-America
    "AVA235"         # Latin-America
    ]  # Add your specific callsigns here

try:
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, low_memory=False)
    
    # Reset the index
    df.reset_index(drop=True, inplace=True)

    # Extract callsign from 'flight_id' (assumes callsign comes before "_")
    df["callsign"] = df["flight_id"].str.split("_").str[0]

    # Filter the DataFrame to keep only selected callsigns
    df = df[df["callsign"].isin(selected_callsigns)]

    # Display the first few rows of the filtered DataFrame
    print("CSV file successfully imported and filtered!")
    print(df.head())  # Print the first 5 rows of the filtered data

except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")

vmin=df["ef"].min()
vmax=df["ef"].max()

df["ef_per_segment"] = df["ef"]/df["segment_length"]

# dep_lon, dep_lat = 48.353889, 11.786111
# arr_lon, arr_lat = 52.460214, 9.683522

# # Define airports data
# airports = pd.DataFrame({
#     "Airport": ["MUC", "HAJ"],
#     "Coordinates": ["POINT(11.786111 48.353889)", "POINT(9.9500 52.460835)"]
# })

# # Define airports data
# airports = pd.DataFrame({
#     "Airport": ["CDG", "CMN"],
#     "Coordinates": ["POINT(2.547778 49.009724)", "POINT(-7.587164318 33.366998532)"]
# })

# # Define airports data
# airports = pd.DataFrame({
#     "Airport": ["MAD", "LGW"],
#     "Coordinates": ["POINT(-3.5679515 40.4839361)", "POINT(-0.182152 51.153629)"]
# })

# # Define airports data
# airports = pd.DataFrame({
#     "Airport": ["MAD", "CDG"],
#     "Coordinates": ["POINT(-3.5679515 40.4839361)", "POINT(2.547778 49.009724)"]
# })

# Define airports data - AZU8708
airports = pd.DataFrame({
    "Airport": ["MEX", "SJO"],
    "Coordinates": ["POINT(-99.071944 19.436111)", "POINT(-75.426667 6.167222)"]
})

# # Define airports data - AZU8708
# airports = pd.DataFrame({
#     "Airport": ["BEL", "CNF"],
#     "Coordinates": ["POINT(-48.478889 -1.384722)", "POINT(-43.971944 -19.624444)"]
# })

# # Define airports data - AZU8708
# airports = pd.DataFrame({
#     "Airport": ["BEL", "CNF"],
#     "Coordinates": ["POINT(-48.478889 -1.384722)", "POINT(-43.971944 -19.624444)"]
# })

# Convert "Coordinates" to GeoDataFrame
airports["geometry"] = airports["Coordinates"].apply(loads)
airports = gpd.GeoDataFrame(airports, geometry="geometry")

# Assuming 'df' is your DataFrame
# Replace 'flight_id' with the actual column name for flight identifiers
if 'flight_id' in df.columns:
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
        fig.savefig(f"{plot_filename}_{selected_callsigns}_EF_per_m_trajectory.png", dpi=300, bbox_inches="tight", format="png")
        fig.savefig(f"{plot_filename}_{selected_callsigns}_EF_per_m_trajectory.pdf", bbox_inches="tight", format="pdf")

    # Iterate over each date group
    for date, group in grouped_by_date:
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Normalize the 'rhi_1' values to match the color scale specific to each flight
        norm_rhi = Normalize(vmin=group["rhi_1"].min(), vmax=group["rhi_1"].max())

        # Paint the water blue by setting the background color
        ax.set_facecolor("lightblue")  # Set background color to blue

        # Plot the world map with land areas filled
        world.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)  # Land is white with black edges

        # Plot airports
        airports.plot(ax=ax, color="black", markersize=30, marker="o", label="Airports")

        # Add airport names as text labels
        for _, row in airports.iterrows():
            ax.text(
                row.geometry.x + 0.10, row.geometry.y + 0.1750,  # Longitude, Latitude
                row["Airport"],  # Airport code (e.g., "MUC", "HAJ")
                fontsize=fontsize, color="black", fontweight="regular",
                horizontalalignment='center', verticalalignment='bottom',
                fontfamily="serif"  # Ensures a LaTeX-like appearance
            )

        # Scatter plot the flight data with RH_i values
        scatter = ax.scatter(
            x=group["longitude"],
            y=group["latitude"],
            c=group["rhi_1"],  # Color mapped to RH_i values
            cmap="magma",
            norm=norm_rhi,  # Apply normalization based on this flight's RH_i range
            label=f"Flight on {date}",
            alpha=0.7,
            edgecolor=None,
        )

        # Add colorbar for RH_i values
        cbar = plt.colorbar(scatter, ax=ax, label=r"RH$_{i}$")
        cbar.set_label(r"RH$_{i}$", fontsize=fontsize, fontfamily="serif")

        # Plot the trajectory lines with RH_i-based colors
        for i in range(len(group) - 1):
            ax.plot(
                [group["longitude"].iloc[i], group["longitude"].iloc[i + 1]],
                [group["latitude"].iloc[i], group["latitude"].iloc[i + 1]],
                color=plt.cm.magma(norm_rhi(group["rhi_1"].iloc[i])),  # Color based on RH_i values
                linewidth=0.7,  # Adjust line thickness to make it more readable
                alpha=0.7       # Transparency for the lines
            )

        # Customize the plot
        ax.set_xlim(lon_min, lon_max)  # Set longitude limits
        ax.set_ylim(lat_min, lat_max)  # Set latitude limits
        ax.set_xlabel(r"Longitude [º]", fontsize=fontsize, fontfamily="serif")
        ax.set_ylabel(r"Latitude [º]", fontsize=fontsize, fontfamily="serif")
        ax.grid(True, linewidth=0.3)  # Reduced gridline thickness

        # Save the plot as both PDF and PNG with high resolution
        plot_filename = f"RHi_flight_data_{date}"
        fig.savefig(f"{plot_filename}" + "_"+f"{selected_callsigns}.png", dpi=300, bbox_inches="tight", format="png")
        fig.savefig(f"{plot_filename}" + "_"+f"{selected_callsigns}.pdf", bbox_inches="tight", format="pdf")

# flight_statistics = cocip.output_flight_statistics()
# flight_statistics

# waypoint_summary = flight_waypoint_summary_statistics(,)
# flight_summary = contrail_flight_summary_statistics(waypoint_summary)
# flight_summary

# print EF for each flight
# print(df.head())
# for fl in df:
#     print(f"{fl.attrs['date']}: {np.sum(fl['ef'])}")

# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Paint the water blue by setting the background color
ax.set_facecolor("lightblue")  # Set background color to blue

# Plot the world map
world.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)  # Land is white with black edges

# # Normalize the 'ef' values for color mapping
# norm = Normalize(vmin=df["ef"].min(), vmax=df["ef"].max())

# Create a list to hold the flight labels for the legend
flight_labels = []

# Define a list of markers for different days
markers = ['o', 's', '^', 'D', 'p', '*', 'H', 'X']  # Add more if needed

# Plot the trajectory lines for each flight, grouped by date
for i, (date, group) in enumerate(grouped_by_date):
    # Plot the trajectory lines for each flight on the same date
    for j in range(len(group) - 1):
        ax.plot(
            [group["longitude"].iloc[j], group["longitude"].iloc[j+1]],
            [group["latitude"].iloc[j], group["latitude"].iloc[j+1]],
            color=plt.cm.coolwarm(norm(group["ef"].iloc[j])),  # Color based on EF
            linewidth=0.7,  # Adjust line thickness to make it more readable
            alpha=0.7       # Transparency for the lines
        )

        

    # Scatter plot for the flight waypoints (using EF values)
    scatter = ax.scatter(
        x=group["longitude"],
        y=group["latitude"],
        c=group["ef"],         # Use the 'ef' values for coloring the points
        cmap="coolwarm",       # Color map to use
        vmin=vmin,
        vmax=vmax,        
        #norm=norm,             # Apply normalization
        label=r"Flight on " + f"{date}",  # Label for the legend
        alpha=0.7,             # Transparency for the points
        edgecolor=None,        # Remove the black contour around the points
        marker=markers[i % len(markers)]  # Different markers for different dates
    )

    # Add date to the flight labels list
    flight_labels.append(f"Flight on {date}")

# Plot airports
airports.plot(ax=ax, color="black", markersize=30, marker="o", label="Airports")

# Add airport names as text labels
for _, row in airports.iterrows():
    ax.text(
    row.geometry.x+0.10, row.geometry.y+0.1750,  # Longitude, Latitude
    row["Airport"],  # Airport code (e.g., "MUC", "HAJ")
    fontsize=fontsize, color="black", fontweight="regular",
    horizontalalignment='center', verticalalignment='bottom',
    fontfamily="serif"  # Ensures a LaTeX-like appearance
    )

# Add colorbar for the EF values
#cbar = plt.colorbar(scatter, ax=ax, label="EF")
#cbar.set_label(r"EF [J]", fontsize=14, fontfamily="serif")

# Customize the plot appearance
ax.set_xlim(lon_min, lon_max)  # Longitude limits
ax.set_ylim(lat_min, lat_max)  # Latitude limits
ax.set_title(r"EF Generated by Flight Waypoints", fontsize=fontsize, fontfamily="serif")
ax.set_xlabel(r"Longitude [º]", fontsize=fontsize, fontfamily="serif")
ax.set_ylabel(r"Latitude [º]", fontsize=fontsize, fontfamily="serif")
ax.grid(True, linewidth=0.3)  # Reduced gridline thickness

# Add legend
ax.legend(title="Flights", loc="upper left", fontsize=fontsize*0.75)

# Save the plot as both PDF and PNG with high resolution
plot_filename = "all_flights_by_date"

# Save as PNG with high resolution (300 DPI)
fig.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")

# Save as PDF
fig.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Paint the water blue by setting the background color
ax.set_facecolor("lightblue")  # Set background color to blue

# Plot the world map
world.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)  # Land is white with black edges

# Create a list to hold the flight labels for the legend
flight_labels = []

# Define a list of markers for different days
markers = ['o', 's', '^', 'D', 'p', '*', 'H', 'X']  # Add more if needed

# Plot the trajectory lines for each flight, grouped by date
for i, (date, group) in enumerate(grouped_by_date):
    # Plot the trajectory lines for each flight on the same date
    for j in range(len(group) - 1):
        ax.plot(
            [group["longitude"].iloc[j], group["longitude"].iloc[j+1]],
            [group["latitude"].iloc[j], group["latitude"].iloc[j+1]],
            color=plt.cm.coolwarm(norm(group["rhi_1"].iloc[j])),  # Color based on EF
            linewidth=0.7,  # Adjust line thickness to make it more readable
            alpha=0.7       # Transparency for the lines
        )

    # Scatter plot for the flight waypoints (using EF values)
    scatter = ax.scatter(
        x=group["longitude"],
        y=group["latitude"],
        c=group["rhi_1"],         # Use the 'ef' values for coloring the points
        cmap="coolwarm",       # Color map to use
        vmin=0,
        vmax=1.5,        
        #norm=norm,             # Apply normalization
        label=f"Flight on {date}",  # Label for the legend
        alpha=0.7,             # Transparency for the points
        edgecolor=None,        # Remove the black contour around the points
        marker=markers[i % len(markers)]  # Different markers for different dates
    )

    # Add date to the flight labels list
    flight_labels.append(f"Flight on {date}")

# Plot airports
airports.plot(ax=ax, color="black", markersize=30, marker="o", label="Airports")

# Add airport names as text labels
for _, row in airports.iterrows():
    ax.text(
    row.geometry.x+0.10, row.geometry.y+0.1750,  # Longitude, Latitude
    row["Airport"],  # Airport code (e.g., "MUC", "HAJ")
    fontsize=fontsize, color="black", fontweight="regular",
    horizontalalignment='center', verticalalignment='bottom',
    fontfamily="serif"  # Ensures a LaTeX-like appearance
    )    

# Add colorbar for the EF values
# cbar = plt.colorbar(scatter, ax=ax, label="rhi_1")
# cbar.set_label(r"RH$_{i}$", fontsize=14, fontfamily="serif")

# Customize the plot appearance
ax.set_xlim(lon_min, lon_max)  # Longitude limits
ax.set_ylim(lat_min, lat_max)  # Latitude limits
ax.set_title(r"RH$_{i}$ along flight path", fontsize=fontsize, fontfamily="serif")
ax.set_xlabel(r"Longitude [º]", fontsize=fontsize, fontfamily="serif")
ax.set_ylabel(r"Latitude [º]", fontsize=fontsize, fontfamily="serif")
ax.grid(True, linewidth=0.3)  # Reduced gridline thickness

# Add legend
ax.legend(title="Flights", loc="upper left", fontsize=fontsize*0.75)

# Save the plot as both PDF and PNG with high resolution
plot_filename = "RH_i_all_flights_by_date"

# Save as PNG with high resolution (300 DPI)
fig.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")

# Save as PDF
fig.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

# Plot with subplots

# Define the number of plots
num_plots = 6  # Adjust as needed

# Select the first six dates for plotting
selected_dates = list(grouped_by_date.groups.keys())[:num_plots]

# Create subplots: 2 rows, 3 columns
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 18))  # Adjust size if needed
axes = axes.flatten()  # Flatten the 2D array for easier iteration

# Define global normalization for color consistency
all_ef_values = np.concatenate([grouped_by_date.get_group(date)["ef"].values for date in selected_dates])
norm = Normalize(vmin=all_ef_values.min(), vmax=all_ef_values.max())

# Iterate over selected dates and plot
for i, (date, ax) in enumerate(zip(selected_dates, axes)):
    group = grouped_by_date.get_group(date)  # Get the group for this date

    # Convert EF values from Joules to Terajoules (TJ)
    group["ef_TJ"] = group["ef"] / 1e12
    
    # Normalize the EF values for color mapping
    ef_min, ef_max = group["ef_TJ"].min(), group["ef_TJ"].max()
    norm = Normalize(vmin=ef_min, vmax=ef_max)

    # Set background color for water representation
    ax.set_facecolor("lightblue")  

    # Plot world map
    world.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)

    # Plot airports
    airports.plot(ax=ax, color="black", markersize=30, marker="o", label="Airports")

    # Add airport names as text labels
    for _, row in airports.iterrows():
        ax.text(
            row.geometry.x + 0.10, row.geometry.y + 0.1750,  # Longitude, Latitude
            row["Airport"],  # Airport code (e.g., "MUC", "HAJ")
            fontsize=fontsize, color="black", fontweight="regular",
            horizontalalignment='center', verticalalignment='bottom',
            fontfamily="serif"  # Ensures a LaTeX-like appearance
        )

    # Scatter plot flight data with EF-based coloring
    scatter = ax.scatter(
        x=group["longitude"],
        y=group["latitude"],
        c=group["ef_TJ"],  # Use scaled EF values
        cmap="coolwarm",
        norm=norm,
        label=f"Flight on {date}",
        alpha=0.7,  # Transparency for the points
        edgecolor=None,  # Remove the black contour around the points
        marker=markers[i % len(markers)]  # Different markers for different dates
    )

    # Add colorbar and set it to show values in terajoules (TJ)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label(r"EF [TJ]", fontsize=fontsize, fontfamily="serif")
    
    # Format the colorbar ticks in scientific notation
    cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.2f}"))

    # Plot the trajectory lines with EF-based color
    for j in range(len(group) - 1):
        ax.plot(
            [group["longitude"].iloc[j], group["longitude"].iloc[j+1]],
            [group["latitude"].iloc[j], group["latitude"].iloc[j+1]],
            color=plt.cm.coolwarm(norm(group["ef_TJ"].iloc[j])),
            linewidth=0.7,
            alpha=0.7
        )

    # Customize each subplot
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    # ax.set_title(r"EF by Flight Waypoints " + f"{date}", fontsize=fontsize, fontfamily="serif")
    ax.set_xlabel(r"Longitude [º]", fontsize=fontsize, fontfamily="serif")
    ax.set_ylabel(r"Latitude [º]", fontsize=fontsize, fontfamily="serif")
    ax.grid(True, linewidth=0.1)


# Adjust layout
fig.tight_layout()

# Save the figure as PNG and PDF
fig.savefig("flights_map.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("flights_map.pdf", bbox_inches="tight", format="pdf")

# Create the figure
plt.figure(figsize=(24, 12))

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
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

    # Save with both date and callsign in filename
    sanitized_callsign = str(callsign).strip().replace("/", "_").replace(" ", "_")
    plt.savefig(f"energy_forcing_vs_time_{sanitized_callsign}_{date}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"energy_forcing_vs_time_{sanitized_callsign}_{date}.pdf", bbox_inches="tight", format="pdf")
    plt.close()

# Iterate over the grouped data by flight ID
for flight_id, group in df.groupby("flight_id"):
    # Create a new figure for each flight
    plt.figure(figsize=(12, 6))

    # Plot the EF over time for this specific flight
    plt.plot(
        group["seconds_since_midnight"]/3600,  # X-axis: Seconds since midnight
        group["ef"]/1e6,                      # Y-axis: Energy Forcing
        linestyle="-", 
        marker="o",
        markersize=4,
        label=f"Flight {flight_id}",
        alpha=1
    )

    # Set logarithmic scale for y-axis
    #plt.yscale("log")

    # Customize the plot
    plt.xlabel(r"Time [h]")
    plt.ylabel(r"EF [MJ]")
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  # Grid for both major and minor ticks

    # Save the figure uniquely for each flight
    plot_filename = f"ef_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

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
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h
    plt.legend(fontsize=fontsize*0.75)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)  

    # Save the figure uniquely for each flight
    plot_filename = f"rf_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

# Iterate over the grouped data by flight ID
for flight_id, group in df.groupby("flight_id"):
    # Create a new figure for each flight
    plt.figure(figsize=(12, 6))

    # Plot each parameter over time
    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rh"],  
        linestyle="-", marker="o", markersize=4,
        label="Relative Humidity (RH)", alpha=0.7
    )

    # plt.plot(
    #     group["seconds_since_midnight"]/3600,  
    #     group["rh_critical_sac"],  
    #     linestyle="-", marker="s", markersize=4,
    #     label="RH Critical SAC", alpha=0.7
    # )

    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rhi_1"],  
        linestyle="-", marker="d", markersize=4,
        label="Relative Humidity w/ Ice (RHI)", alpha=0.7
    )

    # plt.plot(
    #     group["seconds_since_midnight"]/3600,  
    #     group["specific_humidity_1"],  
    #     linestyle="-", marker="^", markersize=4,
    #     label="Specific Humidity", alpha=0.7
    # )

    # Customize the plot
    plt.xlabel(r"Time [h]")
    plt.ylabel(r"Rh")
    # plt.title(f"Humidity Metrics Over Time for Flight {flight_id}")
    plt.legend(fontsize=fontsize*0.75)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

    # Save the figure uniquely for each flight
    plot_filename = f"humidity_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

    plt.close()

# Iterate over the grouped data by flight ID
for flight_id, group in df.groupby("flight_id"):
    # Create a new figure for each flight
    plt.figure(figsize=(12, 6))

    # Plot each parameter over time
    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rh"],  
        linestyle="-", marker="o", markersize=4,
        label="Relative Humidity", alpha=0.7
    )

    # Plot each parameter over time
    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["rh_critical_sac"],  
        linestyle="-", marker="o", markersize=4,
        label="Critical Relative Humidity", alpha=0.7
    )

    # Customize the plot
    plt.xlabel(r"Time [h]")
    plt.ylabel(r"Rh")
    # plt.title(f"Humidity Metrics Over Time for Flight {flight_id}")
    plt.legend(fontsize=fontsize*0.75)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

    # Save the figure uniquely for each flight
    plot_filename = f"rh_rh_sac_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

    plt.close()

    # Iterate over the grouped data by flight ID
    for flight_id, group in df.groupby("flight_id"):
        # Create a new figure for each flight
        plt.figure(figsize=(12, 6))

        # Plot each parameter over time
        plt.plot(
            group["seconds_since_midnight"]/3600,  
            group["air_temperature"],  
            linestyle="-", marker="o", markersize=4,
            label="Air Temperature", alpha=0.7
        )

        # Plot each parameter over time
        plt.plot(
            group["seconds_since_midnight"]/3600,  
            group["T_sat_liquid"],  
            linestyle="-", marker="o", markersize=4,
            label="Critical Air Temperature", alpha=0.7
        )

        # Customize the plot
        plt.xlabel(r"Time [h]")
        plt.ylabel(r"Air Temperature [K]")
        # plt.title(f"Humidity Metrics Over Time for Flight {flight_id}")
        plt.legend(fontsize=fontsize*0.75)
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

        # Save the figure uniquely for each flight
        plot_filename = f"air_temperature_T_sat_liquid_vs_time_flight_{flight_id}"
        plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
        plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")    

        plt.close()

# Iterate over the grouped data by flight ID
for flight_id, group in df.groupby("flight_id"):
    # Create a new figure for each flight
    plt.figure(figsize=(12, 6))

    # Plot each parameter over time
    plt.plot(
        group["seconds_since_midnight"]/3600,  
        group["altitude"]/1e3,  
        linestyle="-", marker="o", markersize=4,
        label="Altitude", alpha=0.7
    )

    # Customize the plot
    plt.xlabel(r"Time [h]")
    plt.ylabel(r"Altitude [km]")
    # plt.title(f"Humidity Metrics Over Time for Flight {flight_id}")
    plt.legend(fontsize=fontsize*0.75)
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

    # Save the figure uniquely for each flight
    plot_filename = f"altitude_vs_time_flight_{flight_id}"
    plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
    plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")

    plt.close()

    # Iterate over the grouped data by flight ID
    for flight_id, group in df.groupby("flight_id"):
        # Create a new figure for each flight
        plt.figure(figsize=(12, 6))

        # Plot each parameter over time
        plt.plot(
            group["seconds_since_midnight"]/3600,  
            group["altitude"]/1e3,  
            linestyle="-", marker="o", markersize=4,
            label="Altitude", alpha=0.7
        )

        # Customize the plot
        plt.xlabel(r"Time [h]")
        plt.ylabel(r"Altitude [km]")
        # plt.title(f"Humidity Metrics Over Time for Flight {flight_id}")
        # plt.legend(fontsize=fontsize*0.5)
        plt.grid(True, which="both", linestyle="--", linewidth=0.5)
        plt.xlim(10.5, 15.6)  # Limit time range from 12h to 21h

        # Save the figure uniquely for each flight
        plot_filename = f"altitude_vs_time_flight_2_{flight_id}"
        plt.savefig(f"{plot_filename}.png", dpi=300, bbox_inches="tight", format="png")
        plt.savefig(f"{plot_filename}.pdf", bbox_inches="tight", format="pdf")    

        plt.close()        