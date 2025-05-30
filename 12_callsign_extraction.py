# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script processes a summary CSV file containing flight contrail data and extracts the callsign from each flight_id. 
#     The callsign is assumed to be the substring before the first underscore ("_") in the flight_id. The extracted callsign 
#     is added as a new column in the DataFrame. Finally, the updated DataFrame is saved back to a CSV file.
# 
# Inputs:
#     - A CSV file containing flight summary data, including a "flight_id" column. This file is specified by `input_file`.
# 
# Outputs:
#     - A CSV file (specified by `output_file`) with the same data as the input but with an additional "callsign" column extracted 
#       from the flight_id.
# 
# Additional Comments:
#     - The script assumes that the flight_id field always contains an underscore separating the callsign from other identifiers.
#     - The input and output file paths currently point to the same file. If you want to keep the original file unchanged, 
#       change the output path accordingly.
#     - Uses pandas for efficient CSV file handling and string manipulation.
#     - Suitable for quick preprocessing of contrail summary data to facilitate further analysis by callsign.
# =========================================================================================================================================

import pandas as pd

# Define input and output file paths
input_file  = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_summary.csv"  # Change this to your actual file path
output_file = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\2025-01-01_2025-01-07_LA_Flight_Radar_24_checked_processed_cocip_summary.csv"  # Change this to the desired output path

# Load the CSV file
df = pd.read_csv(input_file, low_memory=False)

# Extract callsign from flight_id (before the first "_")
df["callsign"] = df["flight_id"].astype(str).str.split("_").str[0]

# Save the updated DataFrame to a new CSV file
df.to_csv(output_file, index=False)

print("Updated CSV file saved successfully:", output_file)