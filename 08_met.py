# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: 
#     This script downloads and inspects meteorological and radiation data from 
#     the ERA5 dataset using the PyContrails library, focusing on a specific time 
#     period and pressure levels relevant for contrail modeling with the CoCiP model.
#     
# Inputs:
#     - time_bounds: Tuple of start and end datetime strings defining the period for data extraction.
#     - pressure_levels: Tuple of pressure levels (in hPa) for which meteorological data is requested.
#     - PyContrails CoCiP model variables:
#         * met_variables: mandatory meteorological variables for contrail modeling.
#         * optional_met_variables: additional meteorological variables that can enhance model accuracy.
#         * rad_variables: radiation-related variables for radiative forcing calculations.
# 
# Outputs:
#     - Downloaded ERA5 meteorological dataset (`met`) covering specified variables and pressure levels.
#     - Downloaded ERA5 radiation dataset (`rad`) covering radiation variables.
#     - Console output listing:
#         * The defined time bounds.
#         * The meteorological and optional variables used.
#         * The variables present in both datasets.
#         * The count of missing values (NaNs) for each variable in both datasets.
#         * Summary statements indicating whether any missing data exist in each dataset.
# 
# Additional Comments:
#     - This script is useful for quality checking ERA5 data before using it as input for contrail simulations with CoCiP.
#     - Handling missing data appropriately is crucial as it can affect the accuracy and stability of contrail modeling.
#     - Uses Dask (implied by `.compute()`) for handling large datasets efficiently.
#     - Time bounds are set with a buffer to ensure full coverage of flight data time ranges.
#     - Pressure levels are chosen to cover typical flight altitudes where contrails form.
# =========================================================================================================================================

from pycontrails.datalib.ecmwf import ERA5
from pycontrails.models.cocip import Cocip

# Pressure levels for ERA5 (for example)
pressure_levels = (900, 875, 850, 825, 800, 775, 750, 700, 650, 600, 550, 
                   500, 450, 400, 350, 300, 250, 225, 200, 175, 150, 125, 
                   100)

# Determine the time bounds based on the minimum and maximum times for the specific flight
time_bounds = (
    '2025-01-01 00:00:00',      # Remove timezone info
    '2025-01-16 00:00:00'       # Add a time buffer
)   

print('time_boounds: \n', time_bounds)

print('CoCiP.met_variables: \n', Cocip.met_variables)

print('CoCiP.met_variables: \n', Cocip.optional_met_variables)

# Create ERA5 objects for the flight
era5pl = ERA5(
    time            = time_bounds,
    variables       = Cocip.met_variables + Cocip.optional_met_variables,
    pressure_levels = pressure_levels,
)

era5sl = ERA5(time=time_bounds, variables=Cocip.rad_variables)

# Download data from ERA5 (or open from cache)
met = era5pl.open_metdataset()
rad = era5sl.open_metdataset()

#print("met: ", met)
#print("rad: ", rad)
print("met.attributes: ", met.data.variables)
print("rad.attributes: ", rad.data.variables)

import numpy as np

# Check missing values in meteorological data
print("Checking missing values in met dataset:")
for var in met.data.variables:
    missing_count = np.isnan(met.data[var]).sum().compute()
    print(f"Variable: {var}, Missing values: {missing_count}")

# Check missing values in radiation data
print("\nChecking missing values in rad dataset:")
for var in rad.data.variables:
    missing_count = np.isnan(rad.data[var]).sum().compute()
    print(f"Variable: {var}, Missing values: {missing_count}")

print("Variables with missing values in met dataset:")
for var in met.data.variables:
    missing_count = np.isnan(met.data[var]).sum().compute()
    if missing_count > 0:
        print(f"{var}: {missing_count} missing values")

print("\nVariables with missing values in rad dataset:")
for var in rad.data.variables:
    missing_count = np.isnan(rad.data[var]).sum().compute()
    if missing_count > 0:
        print(f"{var}: {missing_count} missing values")

if any(np.isnan(met.data[var]).sum().compute() > 0 for var in met.data.variables):
    print("There are missing values in the met dataset!")
else:
    print("No missing values in the met dataset.")

if any(np.isnan(rad.data[var]).sum().compute() > 0 for var in rad.data.variables):
    print("There are missing values in the rad dataset!")
else:
    print("No missing values in the rad dataset.")


import numpy as np

for var in met.data:
    missing_count = np.isnan(met.data["fraction_of_cloud_cover"]).sum().compute()
    print(f"Missing values in fraction_of_cloud_cover: {missing_count}")

    