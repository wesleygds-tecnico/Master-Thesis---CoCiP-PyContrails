# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: This script performs exploratory data analysis on contrail emissions data to identify patterns,
#          compute emissions efficiency (EF per meter flown), and determine the most environmentally impactful route.
# 
# Inputs:
#     - A CSV file named 'contrail_data.csv' containing at least the following columns:
#         'timestamp': Timestamps of contrail observations (datetime format),
#         'route': Identifier of the flight route (string or category),
#         'EF': Energy Forcing caused by contrails (float),
#         'RF': Radiative Forcing from contrails (float),
#         'distance_flown': Distance flown during the observation (float).
#
# Outputs:
#     - Printed descriptive statistics of EF, RF, and EF per meter flown.
#     - Distribution histograms of EF, RF, and EF per meter.
#     - Time-series plot of EF for the most impactful route.
#     - Boxplot of EF by day of the week for the most impactful route.
#     - ANOVA test result comparing EF across different weekdays.
#     - Correlation matrix and heatmap between EF and RF.
#     - Printed identification of the most impactful route by EF per meter.
#
# Additional Comments:
#     - Make sure the 'contrail_data.csv' file is present and correctly formatted.
#     - The analysis assumes no major outliers or unit inconsistencies.
#     - Further analysis can include seasonal trends, altitude effects, or fuel type comparison.
#     - Libraries required: pandas, matplotlib, seaborn, scipy, numpy.
# =========================================================================================================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

# Load the dataset
file_path = 'contrail_data.csv'  # Change this to your actual file path
data = pd.read_csv(file_path)

# Preprocess the data (handle missing values, ensure correct data types)
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['day_of_week'] = data['timestamp'].dt.day_name()

# Convert route names or identifiers to categorical if necessary
data['route'] = data['route'].astype('category')

# Compute EF per meter flown
data['EF_per_meter'] = data['EF'] / data['distance_flown']

# Descriptive statistics
print("Descriptive Statistics:")
print(data[['EF', 'RF', 'EF_per_meter']].describe())

# Visualize the distribution of EF, RF, and EF_per_meter
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
sns.histplot(data['EF'], ax=axes[0], kde=True, color='blue').set_title('Distribution of EF')
sns.histplot(data['RF'], ax=axes[1], kde=True, color='green').set_title('Distribution of RF')
sns.histplot(data['EF_per_meter'], ax=axes[2], kde=True, color='red').set_title('EF per Meter Flown')

plt.tight_layout()
plt.show()

# Investigate the most impactful route (max EF per meter flown)
impactful_route = data.groupby('route')['EF_per_meter'].mean().idxmax()
max_EF_route = data[data['route'] == impactful_route]

# Plot the most impactful route's EF over time
plt.figure(figsize=(10, 6))
sns.lineplot(data=max_EF_route, x='timestamp', y='EF', hue='route')
plt.title(f"Contrail Energy Forcing (EF) for Route {impactful_route}")
plt.xlabel('Date')
plt.ylabel('Energy Forcing (EF)')
plt.show()

# Compare contrail development across days of the week for the most impactful route
plt.figure(figsize=(10, 6))
sns.boxplot(data=max_EF_route, x='day_of_week', y='EF')
plt.title(f"Contrail Energy Forcing (EF) by Day of Week for Route {impactful_route}")
plt.xlabel('Day of Week')
plt.ylabel('Energy Forcing (EF)')
plt.show()

# Statistical test: Compare EF across days of the week (ANOVA)
anova_result = stats.f_oneway(*[group['EF'].values for name, group in max_EF_route.groupby('day_of_week')])
print(f"ANOVA Test Result for EF across Days of Week: {anova_result}")

# Investigate correlation between EF and RF
correlation = data[['EF', 'RF']].corr()
print(f"Correlation between EF and RF:\n{correlation}")

# Correlation Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Heatmap: EF vs RF')
plt.show()

# Summarize most impactful route
print(f"The most impactful route based on EF per meter flown: {impactful_route}")