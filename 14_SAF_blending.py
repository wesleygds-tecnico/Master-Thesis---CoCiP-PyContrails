# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: 
#     This script analyzes the properties and emissions of Sustainable Aviation Fuel (SAF) blends 
#     with conventional jet fuel over varying blend percentages. It calculates key fuel properties 
#     such as energy content, hydrogen content, and emissions indices (EI) for several compounds, 
#     then visualizes these properties as a function of the SAF blend percentage.
# 
# Inputs:
#     - Blend percentages: A numpy array of blend ratios from 0% (pure conventional fuel) 
#       to 100% (pure SAF) in increments of 25% (default here is 5 points between 0 and 100).
#     - PyContrails SAFBlend class: Provides access to fuel properties and emissions indices 
#       for each blend percentage.
# 
# Outputs:
#     - Six plots saved both as PNG and PDF files showing:
#         1. Energy content per kg of fuel (q_fuel) vs blend percentage
#         2. Hydrogen content (%) vs blend percentage
#         3. Emission Index (EI) of water (H2O) vs blend percentage
#         4. EI of sulfur dioxide (SO2) and sulphates vs blend percentage
#         5. EI of organic carbon (OC) vs blend percentage
#         6. EI of carbon dioxide (CO2) vs blend percentage
# 
# Additional comments:
#     - The plotting uses matplotlib with LaTeX-style serif fonts for improved readability.
#     - Emission indices for SO2, sulphates, and OC are scaled to mg/kg for clearer visualization.
#     - The code assumes that `pycontrails.SAFBlend` and `JetA` classes are properly defined and imported.
#     - The figure saving commands export high-resolution images suitable for reports or publications.
#     - The plt.show() calls are commented out to enable batch processing without displaying plots interactively.
#     - User can adjust blend percentage resolution by modifying the np.linspace() parameters.
# =========================================================================================================================================

import pycontrails
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Assuming SAFBlend is already imported
# and JetA class is defined somewhere in the same module

# Use LaTeX-style font for all text in the plot
mpl.rcParams["font.family"] = "serif"  # Use a serif font (LaTeX-like)
mpl.rcParams["font.size"] = 30  # Adjust global font size
mpl.rcParams["text.usetex"] = False  # Set to True if you have LaTeX installed

fontsize = 30

# Generate blend percentages from 0% to 100% in steps of 5
blend_percentages = np.linspace(0, 100, 5)

# Store output values for each percentage
q_fuel_values = []
hydrogen_content_values = []
ei_h2o_values = []
ei_so2_values = []
ei_sulphates_values = []
ei_oc_values = []
ei_co2_values = []

for pct in blend_percentages:
    saf = pycontrails.SAFBlend(pct_blend=pct)
    q_fuel_values.append(saf.q_fuel/1e6)
    hydrogen_content_values.append(saf.hydrogen_content)
    ei_h2o_values.append(saf.ei_h2o)
    ei_so2_values.append(saf.ei_so2*1e6)
    ei_sulphates_values.append(saf.ei_sulphates*1e6)
    ei_oc_values.append(saf.ei_oc*1e6)
    ei_co2_values.append(saf.ei_co2)

# Create figure: q_fuel
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         q_fuel_values, 
         label='q_fuel',
         linestyle="-",
         marker="s",  
         markersize=10,
         alpha=1
        )
plt.xlabel(r"Blend [$\%$]", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"$q_{fuel}$ [MJ/kg]", fontsize=fontsize, fontfamily="serif")
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_Energy_Content_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_Energy_Content_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()

# Subplot 2: Hydrogen Content
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         hydrogen_content_values, 
         label='Hydrogen Content', 
         color='green',
         linestyle="-", 
         marker='s',
         markersize=10,
         alpha=1
         )
plt.xlabel(r"Blend [$\%$]")
plt.ylabel(r"EI$_{H}$ [$\%$]")
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_Hydrogen_Content_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_Hydrogen_Content_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()

# Subplot 3: EI H2O
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         ei_h2o_values, 
         label='EI H2O', 
         color='blue', 
         marker='s',
         markersize=10,
         alpha=1
         )
plt.xlabel(r"Blend [$\%$]")
plt.ylabel(r"EI$_{H_{2}O}$ [kg/kg]")
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_EI_H2O_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_EI_H2O_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()

# Subplot 4: EI SO2 & Sulphates
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         ei_so2_values, 
         label='EI SO2', 
         color='red', 
         marker='s',
         markersize=10,
         alpha=1         
         )
plt.plot(blend_percentages, 
         ei_sulphates_values, 
         label='EI Sulphates', 
         color='purple', 
         linestyle='--', 
         marker='s',
         markersize=10,
         alpha=1
         )
plt.xlabel(r"Blend [$\%$]")
plt.ylabel(r"EI$_{SO_{2}}$ [mg/kg]")
plt.legend(fontsize=fontsize*0.9)  # Add legend
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_EI_SO2_&_Sulphates_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_EI_SO2_&_Sulphates_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()

# Subplot 5: EI OC
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         ei_oc_values, 
         label='EI OC', 
         marker='s',
         markersize=10,
         alpha=1
         )
plt.xlabel(r"Blend [$\%$]")
plt.ylabel(r"EI$_{OC}$ [mg/kg]")
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_EI_OC_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_EI_OC_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()

# Subplot 6: EI CO2
fig = plt.figure(figsize=(12, 6))
plt.plot(blend_percentages, 
         ei_oc_values, 
         label='EI CO2', 
         marker='s',
         markersize=10,
         alpha=1
         )
plt.xlabel(r"Blend [$\%$]")
plt.ylabel(r"EI$_{CO_{2}}$ [kg/kg]")
plt.grid(True, linewidth=0.3)  # Enable grid with thin lines
fig.savefig(f"SAF_comparison_EI_CO2_vs_Blend.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"SAF_comparison_EI_CO2_vs_Blend.pdf", bbox_inches="tight", format="pdf")
# plt.show()