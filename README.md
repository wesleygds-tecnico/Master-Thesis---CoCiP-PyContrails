CoCiP through PyContrails Pipeline
------------------------------------------------------------

This pipeline processes meteorological and air traffic data to estimate contrail impacts using the CoCiP model, including scenarios involving SAF (Sustainable Aviation Fuel).

Required Setup
--------------

0. **Environment Setup**
   - Ensure you have a working Python/Conda environment.
   - Install the required packages using the following command:
     ```
     pip install -r requirements.txt
     ```
     or
     ```     
     conda install --yes --file requirements.txt
     ``` 
     - Ensure you have access credentials and a proper API key/signature to use the ECMWF ERA5 API.
       API access may be requested with support of: https://cds.climate.copernicus.eu/user-guide
  
Processing sequence
-------------------

1. **Download Meteorological Data**
     - Script: `08_met.py`
     - Purpose: Download and cache meteorological data from the ECMWF ERA5 API.
     - Output: Cache data of meteorological conditions used later on.    

2. **Prepare Inputs for True Air Speed Calculation**
     - Script: `13_true_air_speed.py`
     - Purpose: This script calculates the true air speed necessary for subsequent performance modeling.
     - Input: Air Traffic data, containing `timestemps`, `callsing`, `longitude`, `latitude`, `altitude`, and `groundspeed`.
     - Output: the original dataframe with flow speed and True Airspeed.

3. **Compute Aircraft Performance Metrics**
     - Script: `00_air_traffic_performance.py`
     - Purpose: This script estimates aircraft performance based on weather conditions and flight trajectories.
     - Input: Air Traffic data including air speed parameters.
     - Output: Air Traffic data, True Air Speed, and parameters of performance, required to CoCiP

4. **Run the CoCiP Model (Standard or SAF Scenario)**
     - Script: `python 06_route_cocip.py` or `python 06_route_cocip_SAF_Blends.py`
     - Purpose: Simulate contrail formation and development through real air traffic and meteorological data.
     - Input: With performance, air traffic, and meteorological data available, CoCiP traffic simulation can be run
     - Output: Air Traffic data, True Air Speed, and parameters of performance, and CoCiP outputs.

Notes
------------------------------------------------------------

- Ensure all input data is preprocessed and properly aligned in terms of time and flight IDs.
- Output files are saved to specified directories within the Results folder structure.
- This pipeline assumes a consistent naming convention and folder structure for data management.

Contact
-------

For questions or contributions, please contact: wesley.silva@tecnico.ulisboa.pt
