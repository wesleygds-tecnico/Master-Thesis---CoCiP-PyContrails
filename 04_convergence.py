# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: 
#     This script performs a comparative analysis of EF (Emission Factor or 
#     Efficiency Factor) convergence across three datasets of flight emissions 
#     data. It filters flights common to all datasets, sums EF values per 
#     flight, and plots the cumulative EF for the top 20 flights with the 
#     highest emissions in each dataset.
#
# Inputs:
#     - Three CSV files containing flight emissions data:
#         * "data\\results\\combined_output_sample_two.csv"
#         * "data\\results\\combined_output_sample_three.csv"
#         * "data\\results\\combined_output_sample_four.csv"
#     Each file must contain at least the columns: 'flight_id' and 'ef'
#
# Outputs:
#     - Line plot comparing the cumulative EF values of top 20 flights across the 3 datasets
#     - Bar chart showing the average cumulative EF of the top 20 flights in each dataset
#     - Console printout of the top 20 flights and their EF values for each dataset
#     - Console printout of the average cumulative EF per dataset
#
# Additional Comments:
#     - The script ensures only flights common to all three datasets are considered.
#     - Sorting and cumulative summing are used to reveal convergence patterns.
#     - This script is useful for analyzing EF data convergence and comparing 
#       data consistency or optimization across different output samples or models.
#     - The variable 'top_n' allows for easy adjustment of how many top flights are analyzed.
# =========================================================================================================================================

import pandas as pd
import matplotlib.pyplot as plt

# Load the three datasets for comparison (replace 'dataset1.csv', 'dataset2.csv', etc. with your actual file paths)
df1 = pd.read_csv("data\\results\\combined_output_sample_two.csv")  # Dataset 1
df2 = pd.read_csv("data\\results\\combined_output_sample_three.csv")  # Dataset 2
df3 = pd.read_csv("data\\results\\combined_output_sample_four.csv")  # Dataset 3

# Find the common flight_ids across all datasets
common_flight_ids = set(df1['flight_id']).intersection(set(df2['flight_id']), set(df3['flight_id']))

# Filter the datasets to only include the common flight_ids
df1 = df1[df1['flight_id'].isin(common_flight_ids)]
df2 = df2[df2['flight_id'].isin(common_flight_ids)]
df3 = df3[df3['flight_id'].isin(common_flight_ids)]

# Sum ef values per flight_id for each dataset
df1_summed = df1.groupby("flight_id")["ef"].sum().reset_index()
df2_summed = df2.groupby("flight_id")["ef"].sum().reset_index()
df3_summed = df3.groupby("flight_id")["ef"].sum().reset_index()

# Sort each dataset by ef in descending order
df1_sorted = df1_summed.sort_values(by="ef", ascending=False)
df2_sorted = df2_summed.sort_values(by="ef", ascending=False)
df3_sorted = df3_summed.sort_values(by="ef", ascending=False)

# Calculate cumulative EF for each dataset
df1_sorted["cumulative_ef"] = df1_sorted["ef"].cumsum()
df2_sorted["cumulative_ef"] = df2_sorted["ef"].cumsum()
df3_sorted["cumulative_ef"] = df3_sorted["ef"].cumsum()

# Limit to top N flights, for example, top 20 flights
top_n = 20
df1_sorted = df1_sorted.head(top_n)
df2_sorted = df2_sorted.head(top_n)
df3_sorted = df3_sorted.head(top_n)

# Create a plot comparing the convergence for the top N flights
plt.figure(figsize=(12, 8))

# Plot the cumulative EF for each dataset with a line
plt.plot(df1_sorted["flight_id"], df1_sorted["cumulative_ef"], label="Dataset 1", color="blue", marker='o', markersize=5)
plt.plot(df2_sorted["flight_id"], df2_sorted["cumulative_ef"], label="Dataset 2", color="green", marker='s', markersize=5)
plt.plot(df3_sorted["flight_id"], df3_sorted["cumulative_ef"], label="Dataset 3", color="red", marker='^', markersize=5)

# Adding labels and title
plt.xlabel("Flight ID")
plt.ylabel("Cumulative EF")
plt.title("Comparison of EF Convergence Across Datasets (Top 20 Flights)")
plt.legend(loc="upper left")
plt.xticks(rotation=45)
plt.tight_layout()

# Show plot
plt.show()

# Print the cumulative EF at the top flights for each dataset
print("Top Flights - Dataset 1")
print(df1_sorted)

print("Top Flights - Dataset 2")
print(df2_sorted)

print("Top Flights - Dataset 3")
print(df3_sorted)


# Calculate the average cumulative EF for each dataset
avg_cumulative_ef_df1 = df1_sorted["cumulative_ef"].mean()
avg_cumulative_ef_df2 = df2_sorted["cumulative_ef"].mean()
avg_cumulative_ef_df3 = df3_sorted["cumulative_ef"].mean()

# Create a summary bar chart of the average cumulative EF for each dataset
plt.figure(figsize=(8, 6))
plt.bar(["Dataset 1", "Dataset 2", "Dataset 3"], [avg_cumulative_ef_df1, avg_cumulative_ef_df2, avg_cumulative_ef_df3], color=["blue", "green", "red"])

# Adding labels and title
plt.ylabel("Average Cumulative EF")
plt.title("Average Cumulative EF for Each Dataset")
plt.tight_layout()

# Show plot
plt.show()

# Print the average cumulative EF for each dataset
print(f"Average cumulative EF for Dataset 1: {avg_cumulative_ef_df1}")
print(f"Average cumulative EF for Dataset 2: {avg_cumulative_ef_df2}")
print(f"Average cumulative EF for Dataset 3: {avg_cumulative_ef_df3}")
