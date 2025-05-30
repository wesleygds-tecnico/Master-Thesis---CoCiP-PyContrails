# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script analyzes and visualizes aviation-related climate impact data based on flight callsigns
#     from a processed OpenSky dataset. It generates summary statistics and detailed bar plots showing
#     various metrics related to energy forcing and radiative forcing associated with flights.
# 
# Inputs:
#     - A CSV file containing flight data with columns such as 'callsign', 'total_energy_forcing',
#       'total_flight_distance_flown', 'mean_lifetime_rf_net', 'mean_lifetime_rf_sw', 'mean_lifetime_rf_lw',
#       and 'flight_id'.
#     - The path to this CSV file is specified in the variable `input_file`.
# 
# Outputs:
#     - Several bar plots saved as PNG and PDF files:
#       1. Top callsigns with highest total energy forcing (in TJ)
#       2. Top callsigns with highest normalized average energy forcing per km (in MJ/m)
#       3. Top callsigns with highest mean lifetime radiative forcing net, shortwave (SW), and longwave (LW)
#       4. Per-callsign plots showing total energy forcing, forcing per km, and mean lifetime RF metrics per flight
# 
# Additional Comments:
#     - The script uses pandas for data handling, seaborn and matplotlib for plotting.
#     - Callsigns are filtered based on a predefined list; update this list as necessary.
#     - Numeric columns are coerced to numeric types to handle possible data issues.
#     - Energy forcing units are converted appropriately for plotting clarity (J to TJ, J/m to MJ/m).
#     - Figures are saved in a dedicated output directory, created if not existing.
#     - The code includes rotation and font adjustments to enhance plot readability.
#     - The script handles multiple metrics for comprehensive impact analysis on climate forcing.
#     - Memory is managed by closing figures after saving to avoid issues in long runs.
# 
# Note:
#     - Update the input CSV path and callsign list as needed before running.
#     - Ensure required packages (pandas, seaborn, matplotlib) are installed in your environment.
# =========================================================================================================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

fontsize = 30

# Load the dataset
input_file = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\2025-01-01_2025-01-07_Opensky_checked_processed_cocip_summary.csv"  # Update with actual path
df = pd.read_csv(input_file, low_memory=False)

# Filter by selected callsigns
selected_callsigns = [
    # "AMX690",
    # "AVA102",
    # "AVA103",
    # "AVA185",
    # "AVA235",
    # "AZU4013",
    # "AZU4577",
    # "AZU4729",
    # "GLO7749",
    # "LPE2450" 
    "AFR11FF",
    "AEE6BR",
    "AEA14ZM",
    "AEA16UE",
    "AFR32QV",
    "AEA49NA",
    "AFR1751",
    "AFR1795",
    "AEA15HY",
    "AEA53HU"
    ]  

# Replace with your actual callsigns
df = df[df["callsign"].isin(selected_callsigns)]

# Ensure numeric columns are correctly formatted
df["total_energy_forcing"] = pd.to_numeric(df["total_energy_forcing"], errors="coerce")
df["total_flight_distance_flown"] = pd.to_numeric(df["total_flight_distance_flown"], errors="coerce")
df["mean_lifetime_rf_net"] = pd.to_numeric(df["mean_lifetime_rf_net"], errors="coerce")
df["mean_lifetime_rf_sw"] = pd.to_numeric(df["mean_lifetime_rf_sw"], errors="coerce")
df["mean_lifetime_rf_lw"] = pd.to_numeric(df["mean_lifetime_rf_lw"], errors="coerce")

# Calculate impact per km
df["forcing_per_km"] = df["total_energy_forcing"] / df["total_flight_distance_flown"]

# Aggregate data per callsign
impact_summary = df.groupby("callsign").agg(
    total_energy_forcing=("total_energy_forcing", "sum"),
    mean_forcing_per_km=("forcing_per_km", "mean"),
    mean_lifetime_rf_net=("mean_lifetime_rf_net", "mean"),
    mean_lifetime_rf_sw=("mean_lifetime_rf_sw", "mean"),  
    mean_lifetime_rf_lw=("mean_lifetime_rf_lw", "mean")
).reset_index()

# Sort callsigns by total impact
top_callsigns = impact_summary.sort_values(by="total_energy_forcing", ascending=False).head(20)

# Set plot style
sns.set_style("whitegrid")

# Convert J to TJ by dividing by 1e12
top_callsigns["total_energy_forcing"] /= 1e12

# Plot total energy forcing per callsign
fig = plt.figure(figsize=(12, 8))
sns.barplot(
    x="callsign", y="total_energy_forcing", 
    data=top_callsigns, 
    order=top_callsigns.sort_values("total_energy_forcing", ascending=False)["callsign"],
    palette="Reds_r"
)

# Adjust axis labels
plt.xlabel(r"Callsign", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"Total Energy Forcing [TJ]", fontsize=fontsize, fontfamily="serif")

# Adjust font sizes for tick labels
plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels for readability
plt.yticks(fontsize=fontsize, fontfamily="serif")

# Format y-axis ticks to show values in TJ
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))  # Adjust decimal places as needed

# Save the figure as PNG and PDF
fig.savefig("Top_10_Callsigns_with_Highest_Total_Energy_Forcing_OpenSky.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("Top_10_Callsigns_with_Highest_Total_Energy_Forcing_OpenSky.pdf", bbox_inches="tight", format="pdf")

import matplotlib.ticker as mticker

# Convert J/m to MJ/m
top_callsigns["mean_forcing_per_km"] /= 1e6

# Plot efficiency: Forcing per km
fig = plt.figure(figsize=(12, 8))
sns.barplot(
    x="callsign", y="mean_forcing_per_km", 
    data=top_callsigns, 
    order=top_callsigns.sort_values("mean_forcing_per_km", ascending=False)["callsign"],
    palette="Blues_r"
)

# Axis labels
plt.xlabel(r"Callsign", fontsize=fontsize, fontfamily="serif")  # Rotate x-axis labels for readability
plt.ylabel(r"Normalized Average EF [MJ/m]", fontsize=fontsize, fontfamily="serif")

# Adjust font sizes for tick labels
plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)
plt.yticks(fontsize=fontsize, fontfamily="serif")

# Format y-axis ticks to show values in MJ/m
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))  # Adjust decimal places as needed

# Save the figure as PNG and PDF
fig.savefig("Top_10_Callsigns_with_Highest_Forcing_per_km_OpenSky.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("Top_10_Callsigns_with_Highest_Forcing_per_km_OpenSky.pdf", bbox_inches="tight", format="pdf")

# Plot mean lifetime RF net
fig = plt.figure(figsize=(12, 8))
sns.barplot(
    x="callsign", y="mean_lifetime_rf_net", 
    data=top_callsigns, 
    order=top_callsigns.sort_values("mean_lifetime_rf_net", ascending=False)["callsign"],
    palette="Greens_r"
)
plt.xticks(rotation=25)
# plt.title("Top 10 Callsigns with Highest Mean Lifetime RF Net")
plt.xlabel(r"Callsign", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"Mean Lifetime RF Net [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

# Adjust font sizes for tick labels on both axes
plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels for readability
plt.yticks(fontsize=fontsize, fontfamily="serif")

# Save the figure as PNG and PDF
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_Net_OpenSky.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_Net_OpenSky.pdf", bbox_inches="tight", format="pdf")

# Plot mean lifetime RF lw
fig = plt.figure(figsize=(12, 8))
sns.barplot(
    x="callsign", y="mean_lifetime_rf_lw", 
    data=top_callsigns, 
    order=top_callsigns.sort_values("mean_lifetime_rf_lw", ascending=False)["callsign"],
    palette="Oranges_r"
)
plt.xticks(rotation=25)
# plt.title("Top 10 Callsigns with Highest Mean Lifetime RF LW")
plt.xlabel(r"Callsign", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"Mean Lifetime RF LW [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

# Adjust font sizes for tick labels on both axes
plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels for readability
plt.yticks(fontsize=fontsize, fontfamily="serif")

# Save the figure as PNG and PDF
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_LW_OpenSky.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_LW_OpenSky.pdf", bbox_inches="tight", format="pdf")

# Plot mean lifetime RF SW
fig = plt.figure(figsize=(12, 8))
sns.barplot(
    x="callsign", y="mean_lifetime_rf_sw", 
    data=top_callsigns, 
    order=top_callsigns.sort_values("mean_lifetime_rf_sw", ascending=False)["callsign"],
    palette="Blues_r"
)
plt.xticks(rotation=25)
# plt.title("Top 10 Callsigns with Highest Mean Lifetime RF SW")
plt.xlabel(r"Callsign", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"Mean Lifetime RF SW [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

# Adjust font sizes for tick labels on both axes
plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels for readability
plt.yticks(fontsize=fontsize, fontfamily="serif")

# Save the figure as PNG and PDF
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_SW_OpenSky.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("Top_10_Callsigns_with_Highest_Mean_Lifetime_RF_SW_OpenSky.pdf", bbox_inches="tight", format="pdf")

# Calculate impact per km
df["forcing_per_km"] = df["total_energy_forcing"] / df["total_flight_distance_flown"]

############################################################################################################################

# Create output directory if it doesn't exist
output_dir = "callsign_flight_plots"
os.makedirs(output_dir, exist_ok=True)

# Convert energy forcing to TJ
df["total_energy_forcing"] /= 1e12

# Get unique callsigns
unique_callsigns = df["callsign"].unique()

# Loop through each callsign
for callsign in unique_callsigns:
    callsign_data = df[df["callsign"] == callsign]

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    
    # Create bar plot for all flights under this callsign
    sns.barplot(
        x="flight_id", y="total_energy_forcing", 
        data=callsign_data, 
        order=callsign_data.sort_values("total_energy_forcing", ascending=False)["flight_id"], 
        palette="Reds_r"
    )

    # Adjust axis labels
    plt.xlabel(r"Flight ID", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"Total Energy Forcing [TJ]", fontsize=fontsize, fontfamily="serif")

    # Adjust font sizes for tick labels
    plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels
    plt.yticks(fontsize=fontsize, fontfamily="serif")

    # Format y-axis ticks to show values in TJ
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Save the figure
    filename = f"{output_dir}/Total_Energy_Forcing_{callsign}_OpenSky.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="png")
    # Save the figure
    filename = f"{output_dir}/Total_Energy_Forcing_{callsign}_OpenSky.pdf"    
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="pdf")

    # Close figure to avoid memory issues
    plt.close(fig)

# Convert energy forcing to TJ
df["forcing_per_km"] /= 1e6

# Loop through each callsign
for callsign in unique_callsigns:
    callsign_data = df[df["callsign"] == callsign]

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    
    # Create bar plot for all flights under this callsign
    sns.barplot(
        x="flight_id", y="forcing_per_km", 
        data=callsign_data, 
        order=callsign_data.sort_values("forcing_per_km", ascending=False)["flight_id"], 
        palette="Blues_r"
    )

    # Adjust axis labels
    plt.xlabel(r"Flight ID", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"Normalized Average EF [MJ/m]", fontsize=fontsize, fontfamily="serif")

    # Adjust font sizes for tick labels
    plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels
    plt.yticks(fontsize=fontsize, fontfamily="serif")

    # Format y-axis ticks to show values in TJ
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Save the figure
    filename = f"{output_dir}/Forcing_per_km_{callsign}_OpenSky.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="png")
    filename = f"{output_dir}/Forcing_per_km_{callsign}_OpenSky.pdf"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="pdf")

    # Close figure to avoid memory issues
    plt.close(fig)

print(f"Plots saved in '{output_dir}' directory.")

# Loop through each callsign
for callsign in unique_callsigns:
    callsign_data = df[df["callsign"] == callsign]

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    
    # Create bar plot for all flights under this callsign
    sns.barplot(
        x="flight_id", y="mean_lifetime_rf_net", 
        data=callsign_data, 
        order=callsign_data.sort_values("mean_lifetime_rf_net", ascending=False)["flight_id"], 
        palette="Greens_r"
    )

    # Adjust axis labels
    plt.xlabel(r"Flight ID", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"Mean Lifetime RF Net [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

    # Adjust font sizes for tick labels
    plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels
    plt.yticks(fontsize=fontsize, fontfamily="serif")

    # Format y-axis ticks to show values in TJ
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Save the figure
    filename = f"{output_dir}/mean_lifetime_rf_net_{callsign}_OpenSky.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="png")
    filename = f"{output_dir}/mean_lifetime_rf_net_{callsign}_OpenSky.pdf"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="pdf")

    # Close figure to avoid memory issues
    plt.close(fig)

print(f"Plots saved in '{output_dir}' directory.")

# Loop through each callsign
for callsign in unique_callsigns:
    callsign_data = df[df["callsign"] == callsign]

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    
    # Create bar plot for all flights under this callsign
    sns.barplot(
        x="flight_id", y="mean_lifetime_rf_lw", 
        data=callsign_data, 
        order=callsign_data.sort_values("mean_lifetime_rf_lw", ascending=False)["flight_id"], 
        palette="Oranges_r"
    )

    # Adjust axis labels
    plt.xlabel(r"Flight ID", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"Mean Lifetime RF LW [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

    # Adjust font sizes for tick labels
    plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels
    plt.yticks(fontsize=fontsize, fontfamily="serif")

    # Format y-axis ticks to show values in TJ
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Save the figure
    filename = f"{output_dir}/mean_lifetime_rf_lw_{callsign}_OpenSky.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="png")
    filename = f"{output_dir}/mean_lifetime_rf_lw_{callsign}_OpenSky.pdf"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="pdf")

    # Close figure to avoid memory issues
    plt.close(fig)

print(f"Plots saved in '{output_dir}' directory.")

# Loop through each callsign
for callsign in unique_callsigns:
    callsign_data = df[df["callsign"] == callsign]

    # Create figure
    fig = plt.figure(figsize=(12, 8))
    
    # Create bar plot for all flights under this callsign
    sns.barplot(
        x="flight_id", y="mean_lifetime_rf_sw", 
        data=callsign_data, 
        order=callsign_data.sort_values("mean_lifetime_rf_sw", ascending=False)["flight_id"], 
        palette="Blues_r"
    )

    # Adjust axis labels
    plt.xlabel(r"Flight ID", fontsize=fontsize, fontfamily="serif")
    plt.ylabel(r"Mean Lifetime RF SW [W/m$^{2}$]", fontsize=fontsize, fontfamily="serif")

    # Adjust font sizes for tick labels
    plt.xticks(fontsize=fontsize, fontfamily="serif", rotation=25)  # Rotate x-axis labels
    plt.yticks(fontsize=fontsize, fontfamily="serif")

    # Format y-axis ticks to show values in TJ
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Save the figure
    filename = f"{output_dir}/mean_lifetime_rf_sw_{callsign}_OpenSky.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="png")
    filename = f"{output_dir}/mean_lifetime_rf_sw_{callsign}_OpenSky.pdf"
    fig.savefig(filename, dpi=300, bbox_inches="tight", format="pdf")

    # Close figure to avoid memory issues
    plt.close(fig)

print(f"Plots saved in '{output_dir}' directory.")