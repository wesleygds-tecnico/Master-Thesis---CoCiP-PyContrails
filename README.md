Author: Wesley Gonçalves da Silva - IST1105271

This pipeline processes meteorological and air traffic data to estimate contrail impacts using the CoCiP model, including scenarios involving SAF (Sustainable Aviation Fuel).

------------------------------------------------------------
0. Installation and Setup
------------------------------------------------------------
- Install all required Python packages using the provided requirements.txt:
    pip install -r requirements.txt

- Ensure you have access credentials and a proper API key/signature to use the ECMWF ERA5 API.
  You can request access and follow setup instructions from: https://cds.climate.copernicus.eu/user-guide

------------------------------------------------------------
1. Download Meteorological Data
------------------------------------------------------------
Run the script `08_met.py` to download and cache meteorological data from the ECMWF ERA5 API.

    python 08_met.py

------------------------------------------------------------
2. Prepare Inputs for True Air Speed Calculation
------------------------------------------------------------
Input both meteorological and air traffic data into:

    13_true_air_speed.py

This script calculates the true air speed necessary for subsequent performance modeling.

------------------------------------------------------------
3. Compute Aircraft Performance Metrics
------------------------------------------------------------
Using outputs from the previous step, run:

    00_air_traffic_performance.py

This script estimates aircraft performance based on weather conditions and flight trajectories.

------------------------------------------------------------
4. Run the CoCiP Model (Standard or SAF Scenario)
------------------------------------------------------------
With performance, air traffic, and meteorological data available, you can now run the CoCiP route simulation:

    python 06_route_cocip.py
    or
    python 06_route_cocip_SAF_Blends.py

The first script is for conventional fuel, while the second includes SAF blend considerations.

------------------------------------------------------------
Notes
------------------------------------------------------------
- Ensure all input data is preprocessed and properly aligned in terms of time and flight IDs.
- Output files are saved to specified directories within the Results folder structure.
- This pipeline assumes a consistent naming convention and folder structure for data management.
