# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script loads an aircraft parameters database CSV file, performs cleaning on the dataset to improve data quality by:
#     1. Removing all single (') and double (") quotes from string entries.
#     2. Stripping leading and trailing whitespace in string columns.
#     3. Removing extra spaces between words to normalize spacing.
# 
# Inputs:
#     - CSV file containing aircraft parameters data (e.g., ICAO24 codes mapped to aircraft types and other attributes).
#     - Input file path is specified by the variable `aircraft_db_path`.
# 
# Outputs:
#     - The cleaned dataset is saved back to the same CSV file, overwriting the original.
# 
# Additional Comments:
#     - The cleaning operation is performed by applying a lambda function on the dataframe to sanitize each string element.
#     - This script assumes the CSV file is not too large to load into memory.
#     - It uses pandas for CSV reading and writing, with low_memory=False to ensure proper dtype inference.
#     - This cleaning improves data consistency, useful for subsequent analysis or matching operations.
#     - Consider creating a backup before overwriting the original CSV to avoid data loss.
#     - The current code applies `.map()` on the entire DataFrame object, which is incorrect — 
#     it should apply element-wise cleaning with `.applymap()` or similar.
# =========================================================================================================================================

import pandas as pd

# Paths to input files
aircraft_db_path = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\data\\aircraft\\ps-aircraft-params-20240524.csv"

"""
Cleans the dataframe by:
1. Removing all single (') and double (") quotes.
2. Stripping leading and trailing whitespace from all string columns.
3. Removing extra spaces between words.
"""

# Load the aircraft database (icao24 -> aircraft_type)
acft_df = pd.read_csv(aircraft_db_path, low_memory=False)

df = acft_df.map(lambda x: " ".join(str(x).replace("'", "").replace('"', "").strip().split()) if isinstance(x, str) else x)

df.to_csv(aircraft_db_path, index=False)