# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose:
#     This script analyzes and visualizes the effect of Sustainable Aviation Fuel (SAF) blend percentages
#     on the energy forcing (EF) of aircraft flights, using multiple CSV summary datasets for different SAF
#     blend ratios (0%, 10%, 20%, 50%, 100%). It compares the total energy forcing and energy forcing per
#     distance flown (EF per meter) across aircraft identified by their ICAO24 code, over a specific time
#     period.
# 
# Inputs:
#     - Five CSV files containing flight summary data for different SAF blend percentages.
#       Each CSV includes columns such as 'icao24' (or flight_id from which icao24 is derived), 
#       'total_energy_forcing', 'total_flight_distance_flown', and 'time'.
#     - A user-defined list of ICAO24 aircraft identifiers for focused analysis.
# 
# Outputs:
#     - Bar plots showing total energy forcing by aircraft (top 20 by EF with SAF 0%).
#     - Bar plots showing EF per meter flown by aircraft for the same subset.
#     - Time series bar plots of total energy forcing for selected ICAO24 aircraft over the analyzed period,
#       separated by SAF blend percentage.
#     - All plots are saved both as PNG and PDF files in the working directory.
# 
# Additional comments:
#     - The script assumes consistent CSV formatting with expected columns; it creates the 'icao24' column
#       from 'flight_id' if missing.
#     - Energy forcing values are large; units are converted and labeled appropriately (TJ, MJ/m).
#     - Uses matplotlib and seaborn for visualization, configuring fonts for publication-quality graphics.
#     - The code is modular with helper functions for grouping and calculation to maintain readability.
#     - Time is handled as datetime for proper sorting and plotting on time axes.
#     - This is primarily an exploratory and presentation script, useful for analyzing SAF impact on flight emissions.
# =========================================================================================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.dates as mdates

# Use LaTeX-style font for all text in the plot
mpl.rcParams["font.family"] = "serif"  # Use a serif font (LaTeX-like)
mpl.rcParams["font.size"] = 25  # Adjust global font size
mpl.rcParams["text.usetex"] = False  # Set to True if you have LaTeX installed

fontsize = 28

# Caminhos para os arquivos CSV com diferentes porcentagens de SAF
csv_path1 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_0_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path2 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_10_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path3 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_20_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path4 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_50_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path5 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"

# Lê os arquivos
df1 = pd.read_csv(csv_path1)
df2 = pd.read_csv(csv_path2)
df3 = pd.read_csv(csv_path3)
df4 = pd.read_csv(csv_path4)
df5 = pd.read_csv(csv_path5)

# Garante que a coluna 'icao24' existe
for df in [df1, df2, df3, df4, df5]:
    if 'icao24' not in df.columns:
        df['icao24'] = df['flight_id'].str[:6]

# Agrupa por icao24 e soma o total_energy_forcing
forcing1 = df1.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_0'})
forcing2 = df2.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_10'})
forcing3 = df3.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_20'})
forcing4 = df4.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_50'})
forcing5 = df5.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_100'})

# Merge entre todos os DataFrames
merged = forcing1.merge(forcing2, on='icao24', how='outer') \
                 .merge(forcing3, on='icao24', how='outer') \
                 .merge(forcing4, on='icao24', how='outer') \
                 .merge(forcing5, on='icao24', how='outer')

# Ordena pelos maiores valores de total_energy_forcing com SAF 0%
merged = merged.sort_values(by="forcing_0", ascending=False).head(20)
# merged = merged.sort_values(by="icao24")

# Plotagem
fig = plt.figure(figsize=(12, 8))
x = range(len(merged))
bar_width = 0.15

plt.bar([i - 2*bar_width for i in x], merged['forcing_0']/1e12, width=bar_width, label=r'0$\%$', color='skyblue')
plt.bar([i - bar_width for i in x], merged['forcing_10']/1e12, width=bar_width, label=r'10$\%$', color='orange')
plt.bar(x, merged['forcing_20']/1e12, width=bar_width, label=r'20$\%$', color='green')
plt.bar([i + bar_width for i in x], merged['forcing_50']/1e12, width=bar_width, label=r'50$\%$', color='red')
plt.bar([i + 2*bar_width for i in x], merged['forcing_100']/1e12, width=bar_width, label=r'100$\%$', color='purple')

plt.xticks(x, merged['icao24'], rotation=90, fontsize=fontsize, fontfamily="serif")
plt.xlabel(r"icao24", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"EF [TJ]", fontsize=fontsize, fontfamily="serif")
plt.legend(title="SAF Blend", fontsize=fontsize, ncol=3, loc='upper center')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
# plt.show()
# Salva as figuras
fig.savefig("EF_icao_SAF_0_10_20_50_100__ext_abs.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("EF_icao_SAF_0_10_20_50_100__ext_abs.pdf", bbox_inches="tight", format="pdf")
plt.close()

# Agrupa por icao24 e soma o total_energy_forcing e total_flight_distance_flown
def get_total_forcing(df, suffix):
    return df.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': f'forcing_{suffix}'})

def get_ef_m(df, suffix):
    grouped = df.groupby('icao24')[['total_energy_forcing', 'total_flight_distance_flown']].sum().reset_index()
    grouped[f'ef_m_{suffix}'] = grouped['total_energy_forcing'] / grouped['total_flight_distance_flown']
    return grouped[['icao24', f'ef_m_{suffix}']]

# Get total forcing just for sorting
forcing0 = get_total_forcing(df1, '0')

# Sort by highest total forcing (SAF 0%) and get top 20 ICAO24
top_icao24 = forcing0.sort_values(by='forcing_0', ascending=False).head(20)['icao24']

# Compute ef_m for each SAF level
ef0 = get_ef_m(df1, '0')
ef10 = get_ef_m(df2, '10')
ef20 = get_ef_m(df3, '20')
ef50 = get_ef_m(df4, '50')
ef100 = get_ef_m(df5, '100')

# Merge ef_m data
merged = ef0.merge(ef10, on='icao24', how='outer') \
            .merge(ef20, on='icao24', how='outer') \
            .merge(ef50, on='icao24', how='outer') \
            .merge(ef100, on='icao24', how='outer')

# Filter only top ICAO24 and preserve original order
merged = merged[merged['icao24'].isin(top_icao24)]
merged['icao24'] = pd.Categorical(merged['icao24'], categories=top_icao24, ordered=True)
merged = merged.sort_values(by="icao24")

# Plotagem
fig = plt.figure(figsize=(12, 8))
x = range(len(merged))
bar_width = 0.15

plt.bar([i - 2*bar_width for i in x], merged['ef_m_0']/1e6, width=bar_width, label=r'0$\%$', color='skyblue')
plt.bar([i - bar_width for i in x], merged['ef_m_10']/1e6, width=bar_width, label=r'10$\%$', color='orange')
plt.bar(x, merged['ef_m_20']/1e6, width=bar_width, label=r'20$\%$', color='green')
plt.bar([i + bar_width for i in x], merged['ef_m_50']/1e6, width=bar_width, label=r'50$\%$', color='red')
plt.bar([i + 2*bar_width for i in x], merged['ef_m_100']/1e6, width=bar_width, label=r'100$\%$', color='purple')

plt.xticks(x, merged['icao24'], rotation=90, fontsize=fontsize, fontfamily="serif")
plt.xlabel(r"icao24", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"EF per m [MJ/m]", fontsize=fontsize, fontfamily="serif")
plt.legend(title="SAF Blend", fontsize=fontsize, ncol=3)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()

# Salva as figuras
fig.savefig("EF_per_m_icao_SAF_0_10_20_50_100__ext_abs.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("EF_per_m_icao_SAF_0_10_20_50_100__ext_abs.pdf", bbox_inches="tight", format="pdf")
plt.close()

# 46b8a8, 3944f2, 3986e7, 46b8ad, 347481, 34750b, 345215, 4cad3b, 4bb843
# ICAO24 de interesse
input_str = "46b8ad"  # Substitua por sua string
selected_icao24 = [s.strip().lower() for s in input_str.split(",")]

# Filtra os DataFrames pelos ICAO24 selecionados
df1_selected = df1[df1['icao24'].isin(selected_icao24)]
df2_selected = df2[df2['icao24'].isin(selected_icao24)]
df3_selected = df3[df3['icao24'].isin(selected_icao24)]
df4_selected = df4[df4['icao24'].isin(selected_icao24)]
df5_selected = df5[df5['icao24'].isin(selected_icao24)]

# Agrupamento por icao24 e data para calcular EF/m
def group_by_date(df, label):
    grouped = df.groupby(['icao24', 'time']).agg({
        'total_energy_forcing': 'sum',
        'total_flight_distance_flown': 'sum'
    }).reset_index()
    grouped['ef_per_m'] = grouped['total_energy_forcing'] / (grouped['total_flight_distance_flown'] * 1e6)
    grouped['SAF'] = label
    return grouped

g1 = group_by_date(df1_selected, "0%")
g2 = group_by_date(df2_selected, "10%")
g3 = group_by_date(df3_selected, "20%")
g4 = group_by_date(df4_selected, "50%")
g5 = group_by_date(df5_selected, "100%")

# Concatena tudo
df_all = pd.concat([g1, g2, g3, g4, g5], ignore_index=True)

# Converte EF para terajoules
df_all["total_energy_forcing"] = df_all["total_energy_forcing"] / 1e12

# Keep time as datetime
df_all["time"] = pd.to_datetime(df_all["time"])

# Sort by time
df_all = df_all.sort_values("time")

fig = plt.figure(figsize=(18, 10))
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    sns.barplot(data=subset, x="time", y="total_energy_forcing", hue="SAF", 
                hue_order=["0%", "10%", "20%", "50%", "100%"])
    
    plt.xlabel("Flight date")
    plt.ylabel("EF [TJ]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=90)

    # Proper datetime formatting on x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()

    plt.legend(title="SAF Blend", fontsize=fontsize, ncol=2)
    plt.tight_layout()
    # plt.show()
    # Save the figure as PNG and PDF
    fig.savefig(f"EF_icao_SAF_0_10_20_50_100_{input_str}_ext_abs.png", dpi=300, bbox_inches="tight", format="png")
    fig.savefig(f"EF_icao_SAF_0_10_20_50_100_{input_str}_ext_abs.pdf", bbox_inches="tight", format="pdf")
    plt.close()

############################################################################

# Converte 'time' para datetime e calcula EF/km
for df in [df1, df2, df3, df4, df5]:
    df["time"] = pd.to_datetime(df["time"])
    df["ef_per_m"] = df["total_energy_forcing"] / df['total_flight_distance_flown']  # Novo campo EF/km

# Filtra os DataFrames pelos ICAO24 selecionados
df1_selected = df1[df1['icao24'].isin(selected_icao24)]
df2_selected = df2[df2['icao24'].isin(selected_icao24)]
df3_selected = df3[df3['icao24'].isin(selected_icao24)]
df4_selected = df4[df4['icao24'].isin(selected_icao24)]
df5_selected = df5[df5['icao24'].isin(selected_icao24)]

# Agrupamento por icao24 e data
def group_by_date(df, label):
    return df.groupby(['icao24', 'time'])['ef_per_m'].mean().reset_index().assign(SAF=label)

g1 = group_by_date(df1_selected, "0%")
g2 = group_by_date(df2_selected, "10%")
g3 = group_by_date(df3_selected, "20%")
g4 = group_by_date(df4_selected, "50%")
g5 = group_by_date(df5_selected, "100%")

# Concatena tudo
df_all = pd.concat([g1, g2, g3, g4, g5], ignore_index=True)

# Mantém time como datetime
df_all["time"] = pd.to_datetime(df_all["time"])
df_all = df_all.sort_values("time")
df_all["ef_per_m"] = df_all["ef_per_m"]/1e6  # Convertendo para MJ/m

fig = plt.figure(figsize=(12, 8))
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    sns.barplot(data=subset, x="time", y="ef_per_m", hue="SAF",
                hue_order=["0%", "10%", "20%", "50%", "100%"])

    plt.xlabel(r"Flight date")
    plt.ylabel(r"EF per m [MJ/m]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=90)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.legend(title="SAF Blend", fontsize=fontsize, ncol=2)
    plt.tight_layout()

    # Save the figure as PNG and PDF
    fig.savefig(f"EF_per_m_icao_SAF_0_10_20_50_100_{input_str}_ext_abs.png", dpi=300, bbox_inches="tight", format="png")
    fig.savefig(f"EF_per_m_icao_SAF_0_10_20_50_100_{input_str}_ext_abs.pdf", bbox_inches="tight", format="pdf")
    plt.close()