# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script performs an in-depth analysis and visualization of EF (Environmental Footprint or another emission-related metric) 
#     data, aggregated by `flight_id`. It helps identify the flights with the highest impact in terms of EF and provides visual 
#     insights such as rankings, distributions, density plots, and Pareto charts.
# 
# Inputs:
#     - A CSV file named 'combined_output_sample_two.csv' located at 'data\\results\\'
#       - Expected columns include: 'flight_id' and 'ef'
#       - 'ef' represents the environmental footprint or a similar metric.
# 
# Outputs:
#     - Bar charts ranking EF per flight
#     - Boxplot showing the EF distribution
#     - Density (KDE) plot for EF values
#     - Pareto charts highlighting cumulative EF contributions per flight and by value bins
#     - Summary table and plot of the top 10 flights with the highest EF, including percentage contribution
# 
# Key Features:
#     - Summarizes EF values per flight
#     - Ranks flights and visualizes top contributors
#     - Identifies the cumulative effect of flight EF in a Pareto analysis (including “Others”)
#     - Bins EF into ranges to analyze distribution patterns
#     - Computes and displays percentage contribution to total EF
# 
# Dependencies:
#     - pandas
#     - matplotlib
#     - seaborn
# 
# Usage:
#     - Update the file path if needed
#     - Run the script in a Python environment where required libraries are installed
#     - Interpreting charts can assist in emission reduction strategies or anomaly detection
# =========================================================================================================================================

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# Path to the output .csv file
input_csv_file = "combined_output_sample_two.csv"

df =  pd.read_csv("data\\results\\combined_output_sample_two.csv")

# Group by 'flight_id' and sum the 'ef' column
summed_ef = df.groupby("flight_id")["ef"].sum().sort_values(ascending=False)


# Rank flights (optional: 1-based ranking)
summed_ef = summed_ef.reset_index()
summed_ef["rank"] = summed_ef["ef"].rank(ascending=False, method="min").astype(int)

# Filter for non-zero EF values
#summed_ef_non_zero = summed_ef[summed_ef["ef"] != 0]

# Plot a bar chart
plt.figure(figsize=(8, 6))
plt.barh(summed_ef["flight_id"], summed_ef["ef"], color="skyblue")
plt.gca().invert_yaxis()  # Rank order from highest to lowest
plt.title("Total EF by Flight ID (Ranked)", fontsize=14)
plt.xlabel("Total EF", fontsize=12)
plt.ylabel("Flight ID", fontsize=12)

# Add values to bars
for index, value in enumerate(summed_ef["ef"]):
    plt.text(value + 1, index, str(value), va="center")

plt.tight_layout()

# Sort and select the top 10 flights
top_flights = summed_ef.sort_values("ef", ascending=False).head(50)

# Plot
plt.figure(figsize=(10, 6))
plt.bar(top_flights["flight_id"], top_flights["ef"], color="steelblue")
plt.xlabel("Flight ID")
plt.ylabel("EF")
plt.title("Top 50 Flights with Highest EF")
plt.xticks(rotation=45)
plt.tight_layout()

plt.figure(figsize=(8, 6))
plt.boxplot(summed_ef["ef"], vert=False, patch_artist=True)
plt.xlabel("EF")
plt.title("Distribution of EF Values")

plt.figure(figsize=(10, 6))
sns.kdeplot(summed_ef["ef"], shade=True, color="steelblue")
plt.xlabel("EF")
plt.title("Density Plot of EF Values")

# Sort by EF and calculate cumulative percentage
sorted_ef = summed_ef.sort_values("ef", ascending=False)
sorted_ef["cumulative_percentage"] = sorted_ef["ef"].cumsum() / sorted_ef["ef"].sum() * 100

# Plot
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(sorted_ef["flight_id"], sorted_ef["ef"], color="steelblue", label="EF")
ax1.set_xlabel("Flight ID")
ax1.set_ylabel("EF")
ax1.tick_params(axis="x", rotation=45)

ax2 = ax1.twinx()
ax2.plot(sorted_ef["flight_id"], sorted_ef["cumulative_percentage"], color="darkred", marker="o", label="Cumulative %")
ax2.set_ylabel("Cumulative Percentage")
ax2.axhline(80, color="green", linestyle="--", linewidth=1)

fig.tight_layout()
plt.title("Pareto Chart of EF by Flight ID")

# Define threshold for "Others" (e.g., cumulative contribution of 20%)
threshold = 20

# Sort by EF and calculate cumulative percentage
sorted_ef = summed_ef.sort_values("ef", ascending=False)
sorted_ef["cumulative_percentage"] = sorted_ef["ef"].cumsum() / sorted_ef["ef"].sum() * 100

# Filter top contributors and group the rest as "Others"
top_contributors = sorted_ef[sorted_ef["cumulative_percentage"] <= threshold]
others = sorted_ef[sorted_ef["cumulative_percentage"] > threshold]
others_sum = others["ef"].sum()

# Append "Others" row
top_contributors = top_contributors._append(
    {"flight_id": "Others", "ef": others_sum, "cumulative_percentage": 100}, 
    ignore_index=True
)

# Recalculate cumulative percentage
top_contributors["cumulative_percentage"] = top_contributors["ef"].cumsum() / top_contributors["ef"].sum() * 100

# Plot
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(top_contributors["flight_id"], top_contributors["ef"], color="steelblue", label="EF")
ax1.set_xlabel("Flight ID")
ax1.set_ylabel("EF")
ax1.tick_params(axis="x", rotation=45)

ax2 = ax1.twinx()
ax2.plot(
    top_contributors["flight_id"], 
    top_contributors["cumulative_percentage"], 
    color="darkred", marker="o", label="Cumulative %"
)
ax2.set_ylabel("Cumulative Percentage")
ax2.axhline(80, color="green", linestyle="--", linewidth=1)

fig.tight_layout()
plt.title("Pareto Chart of EF by Flight ID (With 'Others')")

# Define bins, excluding values above 1e16 and adding more smaller bins
bins = [
    0, 1e8, 1e9, 1e10, 1e11, 1e12, 5e12, 1e13, 5e13, 1e14, 
    5e14, 1e15, 5e15, 1e16
]
labels = [
    "0-1e8", "1e8-1e9", "1e9-1e10", "1e10-1e11", "1e11-1e12", 
    "1e12-5e12", "5e12-1e13", "1e13-5e13", "5e13-1e14", "1e14-5e14", 
    "5e14-1e15", "1e15-5e15", "5e15-1e16"
]

# Add a new column for binned categories
summed_ef["ef_bin"] = pd.cut(summed_ef["ef"], bins=bins, labels=labels, right=False)

# Summarize ef for each bin
binned_summary = summed_ef.groupby("ef_bin")["ef"].sum().reset_index()

# Calculate cumulative percentage
binned_summary["cumulative_percentage"] = binned_summary["ef"].cumsum() / binned_summary["ef"].sum() * 100

# Plot Pareto chart for bins
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.bar(binned_summary["ef_bin"], binned_summary["ef"], color="steelblue", label="EF")
ax1.set_xlabel("EF Range")
ax1.set_ylabel("EF")
ax1.tick_params(axis="x", rotation=45)

ax2 = ax1.twinx()
ax2.plot(
    binned_summary["ef_bin"], 
    binned_summary["cumulative_percentage"], 
    color="darkred", marker="o", label="Cumulative %"
)
ax2.set_ylabel("Cumulative Percentage")
ax2.axhline(80, color="green", linestyle="--", linewidth=1, label="80% Line")
ax2.legend(loc="upper left")

fig.tight_layout()
plt.title("Pareto Chart: EF Distribution by Bins")

# Sum ef values per flight_id
summed_flight_ef = summed_ef.groupby("flight_id")["ef"].sum().reset_index()

# Sort by ef in descending order
summed_flight_ef_sorted = summed_flight_ef.sort_values(by="ef", ascending=False)

# Calculate the total EF
total_ef = summed_flight_ef["ef"].sum()

# Calculate percentage contribution of each flight's EF
summed_flight_ef_sorted["ef_percentage"] = (summed_flight_ef_sorted["ef"] / total_ef) * 100

# Display the top flights and their EF contributions
top_flights = summed_flight_ef_sorted.head(10)  # Get the top 10 flights

# Print the top flights and their EF
print("Top 10 Flights by EF:")
print(top_flights)

# Plot the results
plt.figure(figsize=(12, 8))
plt.bar(top_flights["flight_id"], top_flights["ef"], color="steelblue", label="EF")
plt.xlabel("Flight ID")
plt.ylabel("EF Value")
plt.title("Top 10 Flights by EF")
plt.xticks(rotation=45)
plt.tight_layout()

# Add secondary axis for EF percentage contribution
ax2 = plt.gca().twinx()
ax2.plot(top_flights["flight_id"], top_flights["ef_percentage"], color="darkred", marker="o", label="EF Percentage")
ax2.set_ylabel("EF Percentage (%)")
ax2.legend(loc="upper left")

plt.show()