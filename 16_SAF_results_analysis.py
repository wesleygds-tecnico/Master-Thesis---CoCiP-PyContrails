# =========================================================================================================================================
# Author: Wesley Gonçalves da Silva - IST1105271
# Purpose: 
#     This script performs a comparative analysis of total energy forcing (EF)
#     from aviation activity under three different SAF (Sustainable Aviation Fuel)
#     blending scenarios: 0%, 50%, and 100%.
#     It generates visual plots to highlight emissions differences by aircraft
#     (identified by ICAO24 codes), based on raw data from CSV files.
#
# Inputs:
#     - Three CSV files containing flight and forcing data for SAF blend levels
#       of 0%, 50%, and 100%, respectively.
#     - Each CSV is expected to have the following columns:
#         * 'icao24' or 'flight_id' (from which 'icao24' is extracted)
#         * 'total_energy_forcing'
#         * 'total_flight_distance_flown'
#         * 'mean_lifetime_rf_net', 'mean_lifetime_rf_sw', 'mean_lifetime_rf_lw'
#         * 'time' (used in the last part for time-series analysis)
#
# Outputs:
#     - Two bar plots comparing:
#         1. Total Energy Forcing per aircraft (EF [TJ])
#         2. Normalized Energy Forcing per meter flown (EF per m [MJ/m])
#     - Both plots are saved in PNG and PDF formats:
#         * "EF_icao_SAF_0_50_100.png/pdf"
#         * "EF_per_m_icao_SAF_0_50_100.png/pdf"
#
# Additional Comments:
#     - Font settings are adjusted to resemble LaTeX styling using serif fonts.
#     - Plots include the 5 aircraft with the highest and lowest forcing values.
#     - ICAO24 codes are used as unique aircraft identifiers for comparative analysis.
#     - It includes safeguards to reconstruct 'icao24' from 'flight_id' if missing.
#     - The code can be extended to generate time-series EF/m plots for selected aircraft.
#     - File paths are hardcoded and should be updated if the file locations change.
#     - Designed for quick exploratory visualization of aircraft-level SAF impact.
# =========================================================================================================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.dates as mdates

# Use LaTeX-style font for all text in the plot
mpl.rcParams["font.family"] = "serif"  # Use a serif font (LaTeX-like)
mpl.rcParams["font.size"] = 35  # Adjust global font size
mpl.rcParams["text.usetex"] = False  # Set to True if you have LaTeX installed

fontsize = 35

# Caminho para o arquivo CSV único
csv_path1 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_0_pct_Opensky_checked_processed_cocip_summary.csv"  # <-- substitua pelo caminho correto
csv_path2 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_50_pct_Opensky_checked_processed_cocip_summary.csv"  # Ex: SAF 50%
csv_path3 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"  # Ex: SAF 50%

# Lê os arquivos
df1 = pd.read_csv(csv_path1)
df2 = pd.read_csv(csv_path2)
df3 = pd.read_csv(csv_path3)

# Garante que a coluna icao24 existe
for df in [df1, df2, df3]:
    if 'icao24' not in df.columns:
        df['icao24'] = df['flight_id'].str[:6]

# Agrupa por icao24 e soma total_energy_forcing
forcing1 = df1.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_1'})
forcing2 = df2.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_2'})
forcing3 = df3.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_3'})

# Faz o merge entre os três conjuntos com base em aeronaves comuns
merged = forcing1.merge(forcing2, on='icao24', how='inner').merge(forcing3, on='icao24', how='inner')

# 5 maiores ICAO24 com maior média de forcing por km
top5 = merged.nlargest(5, "forcing_1")

# 5 menores ICAO24 com menor média de forcing por km
bottom5 = merged.nsmallest(5, "forcing_1")

# Combinar os dois em um só DataFrame
merged  = pd.concat([top5, bottom5])

# Seleciona os 20 ICAO24 com maior total_energy_forcing no primeiro arquivo
merged = merged.sort_values(by="forcing_1", ascending=False)

# Plotagem
fig = plt.figure(figsize=(24, 8))
x = range(len(merged))
bar_width = 0.25

plt.bar([i - bar_width for i in x], merged['forcing_1']/1e12, width=bar_width, label=r'0$\%$ SAF', color='skyblue')
plt.bar(x, merged['forcing_2']/1e12, width=bar_width, label=r'50$\%$ SAF', color='orange')
plt.bar([i + bar_width for i in x], merged['forcing_3']/1e12, width=bar_width, label=r'100$\%$ SAF', color='green')

plt.xticks(x, merged['icao24'], rotation=15, fontsize=fontsize, fontfamily="serif")
plt.xlabel(r"icao24", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"EF [TJ]", fontsize=fontsize, fontfamily="serif")
plt.legend(fontsize=fontsize)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
# plt.show()
# Save the figure as PNG and PDF
fig.savefig("EF_icao_SAF_0_50_100.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("EF_icao_SAF_0_50_100.pdf", bbox_inches="tight", format="pdf")
plt.close()

# Lista com os caminhos dos arquivos CSV
csv_files = [
    "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_0_pct_Opensky_checked_processed_cocip_summary.csv",  
    "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_50_pct_Opensky_checked_processed_cocip_summary.csv", 
    "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"
    ]

# Lista para armazenar os DataFrames agregados
summaries = []

# Loop pelos arquivos
for i, path in enumerate(csv_files):
    df = pd.read_csv(path)

    # Cálculo do forcing normalizado pela distância
    df['ef_m'] = df['total_energy_forcing'] / df['total_flight_distance_flown']

    # Agregação por ICAO24
    summary = df.groupby("icao24").agg(
        total_energy_forcing=("total_energy_forcing", "sum"),
        ef_m=("ef_m", "mean"),
        mean_lifetime_rf_net=("mean_lifetime_rf_net", "mean"),
        mean_lifetime_rf_sw=("mean_lifetime_rf_sw", "mean"),
        mean_lifetime_rf_lw=("mean_lifetime_rf_lw", "mean")
    ).reset_index()

    # Adiciona sufixo de identificação para colunas (exceto "icao24")
    suffix = f"_{i+1}"
    summary = summary.rename(columns={col: col + suffix for col in summary.columns if col != "icao24"})

    summaries.append(summary)

# Merge sucessivo com base em "icao24"
merged = summaries[0]
for summary in summaries[1:]:
    merged = merged.merge(summary, on="icao24", how="outer")

# 5 maiores ICAO24 com maior média de forcing por km
top5 = merged.nlargest(5, "ef_m_1")

# 5 menores ICAO24 com menor média de forcing por km
bottom5 = merged.nsmallest(5, "ef_m_1")

# Combinar os dois em um só DataFrame
merged  = pd.concat([top5, bottom5])

# Seleciona os 20 ICAO24 com maior total_energy_forcing no primeiro arquivo
merged = merged.sort_values(by="ef_m_1", ascending=False)

# Plotagem
fig = plt.figure(figsize=(24, 8))
x = range(len(merged))
bar_width = 0.25

plt.bar([i - bar_width for i in x], merged['ef_m_1']/1e6, width=bar_width, label=r'0$\%$ SAF', color='skyblue')
plt.bar(x, merged['ef_m_2']/1e6, width=bar_width, label=r'50$\%$ SAF', color='orange')
plt.bar([i + bar_width for i in x], merged['ef_m_3']/1e6, width=bar_width, label=r'100$\%$ SAF', color='green')    

plt.xticks(x, merged['icao24'], rotation=15, fontsize=fontsize, fontfamily="serif")
plt.xlabel(r"icao24", fontsize=fontsize, fontfamily="serif")
plt.ylabel(r"EF per m [MJ/m]", fontsize=fontsize, fontfamily="serif")
# plt.title("Comparação Normalizada de Energy Forcing por Aeronave")
plt.legend(fontsize=fontsize)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
# plt.show()
# Save the figure as PNG and PDF
fig.savefig("EF_per_m_icao_SAF_0_50_100.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig("EF_per_m_icao_SAF_0_50_100.pdf", bbox_inches="tight", format="pdf")
plt.close()

# Caminhos dos arquivos
csv_path1 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_0_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path2 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_50_pct_Opensky_checked_processed_cocip_summary.csv"
csv_path3 = "C:\\Users\\wesle\\OneDrive\\Documentos\\Master\\code5\\Results\\SAF_analysis\\summary_with_icao24\\2025-01-01_2025-01-14_by_airframe_SAF_100_pct_Opensky_checked_processed_cocip_summary.csv"

# Lê os arquivos
df1 = pd.read_csv(csv_path1)
df2 = pd.read_csv(csv_path2)
df3 = pd.read_csv(csv_path3)

for df in [df1, df2, df3]:
    df["time"] = pd.to_datetime(df["time"])  # Certifica que a coluna "date" é datetime

# Agrupa por icao24 e soma total_energy_forcing no df1 (SAF 0%)
forcing1 = df1.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_1'})
forcing2 = df2.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_2'})
forcing3 = df3.groupby('icao24')['total_energy_forcing'].sum().reset_index().rename(columns={'total_energy_forcing': 'forcing_3'})

# Faz merge
merged = forcing1.merge(forcing2, on='icao24', how='inner').merge(forcing3, on='icao24', how='inner')

# 46b8a8, 3944f2, 3986e7, 34750b, 345215
input_str = "345215"  # Substitua por sua string
selected_icao24 = [s.strip().lower() for s in input_str.split(",")]

# Filtra os DataFrames pelos ICAO24 selecionados
df1_selected = df1[df1['icao24'].isin(selected_icao24)]
df2_selected = df2[df2['icao24'].isin(selected_icao24)]
df3_selected = df3[df3['icao24'].isin(selected_icao24)]

# Agrupamento por icao24 e data para calcular EF/m
def group_by_date(df, label):
    grouped = df.groupby(['icao24', 'time']).agg({
        'total_energy_forcing': 'sum',
        'total_flight_distance_flown': 'sum'
    }).reset_index()
    grouped['ef_per_m'] = grouped['total_energy_forcing'] / (grouped['total_flight_distance_flown']*1e6)
    grouped['SAF'] = label
    return grouped

g1 = group_by_date(df1_selected, "0%")
g2 = group_by_date(df2_selected, "50%")
g3 = group_by_date(df3_selected, "100%")

# Concatena tudo
df_all = pd.concat([g1, g2, g3], ignore_index=True)

df_all["total_energy_forcing"] = df_all["total_energy_forcing"]/1e12

fig = plt.figure(figsize=(24, 8))
# Loop para cada ICAO24
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    lines = sns.lineplot(data=subset, x="time", y="total_energy_forcing", hue="SAF", marker="o")
    for line in lines.lines:
        line.set_markersize(10)  # Adjust size here
    # plt.title(f"Total Energy Forcing por Data para ICAO24 selecionados")
    plt.xlabel(r"Flight date")
    plt.ylabel(r"EF [TJ]")
    plt.grid(True, linestyle="--", alpha=0.5)

# Ajustes finais
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gcf().autofmt_xdate()
plt.legend(title="SAF Blend")
plt.tight_layout()
# plt.show()
# Save the figure as PNG and PDF
fig.savefig(f"EF_line_icao_SAF_0_50_100_{input_str}.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"EF_line_icao_SAF_0_50_100_{input_str}.pdf", bbox_inches="tight", format="pdf")
plt.close()

fig = plt.figure(figsize=(24, 8))
# Loop para cada ICAO24
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    sns.lineplot(data=subset, x="time", y="ef_per_m", hue="SAF", marker="o")
    for line in lines.lines:
        line.set_markersize(10)  # Adjust size here
    plt.xlabel(r"Flight date")
    plt.ylabel(r"EF per m [MJ/m]")
    plt.grid(True, linestyle="--", alpha=0.5)

# Ajustes finais
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=15)
plt.gcf().autofmt_xdate()
plt.legend(title="SAF Blend")
plt.tight_layout()
# plt.show()
# Save the figure as PNG and PDF
fig.savefig(f"EF_line_per_m_icao_SAF_0_50_100_{input_str}.png", dpi=300, bbox_inches="tight", format="png")
fig.savefig(f"EF_line_per_m_icao_SAF_0_50_100_{input_str}.pdf", bbox_inches="tight", format="pdf")
plt.close()

# Keep time as datetime
df_all["time"] = pd.to_datetime(df_all["time"])  # Ensure it's datetime

# Sort by time
df_all = df_all.sort_values("time")

fig = plt.figure(figsize=(24, 8))
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    sns.barplot(data=subset, x="time", y="total_energy_forcing", hue="SAF", hue_order=["0%", "50%", "100%"])
    
    plt.xlabel(r"Flight date")
    plt.ylabel(r"EF [TJ]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=15)

    # Proper datetime formatting on x-axis
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

    plt.legend(title="SAF Blend")
    plt.tight_layout()
    # plt.show()
    # Save the figure as PNG and PDF
    fig.savefig(f"EF_icao_SAF_0_50_100_{input_str}.png", dpi=300, bbox_inches="tight", format="png")
    fig.savefig(f"EF_icao_SAF_0_50_100_{input_str}.pdf", bbox_inches="tight", format="pdf")
    plt.close()    

############################################################################

# Converte 'time' para datetime
for df in [df1, df2, df3]:
    df["time"] = pd.to_datetime(df["time"])
    df["ef_per_m"] = df["total_energy_forcing"] / df['total_flight_distance_flown']  # Novo campo EF/km

# Filtra os DataFrames pelos ICAO24 selecionados
df1_selected = df1[df1['icao24'].isin(selected_icao24)]
df2_selected = df2[df2['icao24'].isin(selected_icao24)]
df3_selected = df3[df3['icao24'].isin(selected_icao24)]

# Agrupamento por icao24 e data
def group_by_date(df, label):
    return df.groupby(['icao24', 'time'])['ef_per_m'].mean().reset_index().assign(SAF=label)

g1 = group_by_date(df1_selected, "0%")
g2 = group_by_date(df2_selected, "50%")
g3 = group_by_date(df3_selected, "100%")

# Concatena tudo
df_all = pd.concat([g1, g2, g3], ignore_index=True)

# Mantém time como datetime
df_all["time"] = pd.to_datetime(df_all["time"])
df_all = df_all.sort_values("time")
df_all["ef_per_m"] = df_all["ef_per_m"]/1e6

# Plotagem
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

fig = plt.figure(figsize=(24, 8))
for icao in selected_icao24:
    subset = df_all[df_all['icao24'] == icao]
    sns.barplot(data=subset, x="time", y="ef_per_m", hue="SAF", hue_order=["0%", "50%", "100%"])

    plt.xlabel(r"Flight date")
    plt.ylabel(r"EF per m [MJ/m]")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=15)

    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()
    plt.legend(title="SAF Blend")
    plt.tight_layout()
    # plt.show()
    # Save the figure as PNG and PDF
    fig.savefig(f"EF_per_m_icao_SAF_0_50_100_{input_str}.png", dpi=300, bbox_inches="tight", format="png")
    fig.savefig(f"EF_per_m_icao_SAF_0_50_100_{input_str}.pdf", bbox_inches="tight", format="pdf")
    plt.close()    