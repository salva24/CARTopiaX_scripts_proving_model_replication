# -----------------------------------------------------------------------------
# Copyright (C) 2025 Salvador de la Torre Gonzalez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Set global font sizes
plt.rcParams.update({
    'font.size': 16,           # Base font size
    'axes.titlesize': 20,      # Title font size
    'axes.labelsize': 18,      # Axis label font size
    'xtick.labelsize': 16,     # X-axis tick label size
    'ytick.labelsize': 16,     # Y-axis tick label size
    'legend.fontsize': 14,     # Legend font size
    'figure.titlesize': 22     # Figure title size
})

# Data files
CARTopiaX_csv_data_dir = './data/data_results_CARTopiaX/'
num_csv_files_CARTopiaX = 5
paper_data_dir = './data/data_results_CART-ABM/'
num_csv_files_paper = 5
days = 30.1

# CSV files from yCARTopiaX model
csv_dataframes = []
for i in range(1, num_csv_files_CARTopiaX + 1):
    csv_file_path = os.path.join(CARTopiaX_csv_data_dir, f'final_data{i}.csv')
    if os.path.exists(csv_file_path):
        df_csv = pd.read_csv(csv_file_path)
        csv_dataframes.append(df_csv)
        print(f"Loaded {csv_file_path}")
    else:
        print(f"Warning: {csv_file_path} not found")

print(f"Successfully loaded {len(csv_dataframes)} CSV files from CARTopiaX model")

# CSV files from the Nature paper model
paper_dataframes = []
for i in range(1, num_csv_files_paper + 1):
    paper_file_path = os.path.join(paper_data_dir, f'datos_finales{i}.csv')
    if os.path.exists(paper_file_path):
        df_paper = pd.read_csv(paper_file_path)
        paper_dataframes.append(df_paper)
        print(f"Loaded {paper_file_path}")
    else:
        print(f"Warning: {paper_file_path} not found")

print(f"Successfully loaded {len(paper_dataframes)} CSV files from the Nature paper model")

# Check CSV columns
for df_csv in csv_dataframes:
    print("CARTopiaX CSV columns:", df_csv.columns)
for df_paper in paper_dataframes:
    print("CART-ABM CSV columns:", df_paper.columns)

csv_time_points = None
csv_mean_cells = None
csv_std_cells = None

if csv_dataframes:
    filtered_csv_dfs = [df[df['total_days'] <= days] for df in csv_dataframes]
    csv_time_points = filtered_csv_dfs[0]['total_days'].values
    all_csv_cell_counts = []
    for df_csv in filtered_csv_dfs:
        cell_counts = np.interp(csv_time_points, df_csv['total_days'], df_csv['num_tumor_cells'])
        all_csv_cell_counts.append(cell_counts)
    all_csv_cell_counts = np.array(all_csv_cell_counts)
    csv_mean_cells = np.mean(all_csv_cell_counts, axis=0)
    csv_std_cells = np.std(all_csv_cell_counts, axis=0)

# Process the Nature paper data to calculate mean and std
paper_time_points = None
paper_mean_cells = None
paper_std_cells = None

if paper_dataframes:
    filtered_paper_dfs = [df[df['total_days'] <= days] for df in paper_dataframes]
    paper_time_points = filtered_paper_dfs[0]['total_days'].values
    all_paper_cell_counts = []
    for df_paper in filtered_paper_dfs:
        cell_counts = np.interp(paper_time_points, df_paper['total_days'], df_paper['num_tumor_cells'])
        all_paper_cell_counts.append(cell_counts)
    all_paper_cell_counts = np.array(all_paper_cell_counts)
    paper_mean_cells = np.mean(all_paper_cell_counts, axis=0)
    paper_std_cells = np.std(all_paper_cell_counts, axis=0)

fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.set_xlabel('Time (days)')
ax1.set_ylabel('Number of Cells')

if csv_dataframes:
    ax1.plot(csv_time_points, csv_mean_cells, 
             color='red', linestyle='-', linewidth=2,
             label='CARTopiaX Tumor Cells (Mean)')
    ax1.fill_between(csv_time_points, 
                     csv_mean_cells - csv_std_cells, 
                     csv_mean_cells + csv_std_cells,
                     color='red', alpha=0.2)
    # Plot alive CART cells
    all_cart_counts = []
    for df_csv in filtered_csv_dfs:
        cart_counts = np.interp(csv_time_points, df_csv['total_days'], df_csv['num_alive_cart'])
        all_cart_counts.append(cart_counts)
    all_cart_counts = np.array(all_cart_counts)
    mean_cart = np.mean(all_cart_counts, axis=0)
    std_cart = np.std(all_cart_counts, axis=0)
    ax1.plot(csv_time_points, mean_cart, color='green', linestyle='-', linewidth=2, label='CARTopiaX Alive CART Cells (Mean)')
    ax1.fill_between(csv_time_points, mean_cart - std_cart, mean_cart + std_cart,
                     color='green', alpha=0.2)

# Plot Nature paper data (tumor cells)
if paper_dataframes:
    ax1.plot(paper_time_points, paper_mean_cells, 
             color='red', linestyle='--', linewidth=2,
             label='Nature Paper Tumor Cells (Mean)')
    ax1.fill_between(paper_time_points, 
                     paper_mean_cells - paper_std_cells, 
                     paper_mean_cells + paper_std_cells,
                     color='red', alpha=0.2)
    # Plot alive CART cells
    all_cart_counts_paper = []
    for df_paper in filtered_paper_dfs:
        cart_counts_paper = np.interp(paper_time_points, df_paper['total_days'], df_paper['num_alive_cart'])
        all_cart_counts_paper.append(cart_counts_paper)
    all_cart_counts_paper = np.array(all_cart_counts_paper)
    mean_cart_paper = np.mean(all_cart_counts_paper, axis=0)
    std_cart_paper = np.std(all_cart_counts_paper, axis=0)
    ax1.plot(paper_time_points, mean_cart_paper, color='green', linestyle='--', linewidth=2, label='Nature Paper Alive CART Cells (Mean)')
    ax1.fill_between(paper_time_points, mean_cart_paper - std_cart_paper, mean_cart_paper + std_cart_paper,
                     color='green', alpha=0.2)

ax1.legend(loc='best')
ax1.grid(True, linestyle='--', alpha=0.7)

plt.title('Tumor & Alive CART Cells Over Time: CARTopiaX vs Nature Paper Model')
plt.tight_layout()

plt.savefig('./out/num_cells.png', dpi=300, bbox_inches='tight')
plt.show()

cell_types = [
    ('tumor_cells_type1', 'Type 1'),
    ('tumor_cells_type2', 'Type 2'),
    ('tumor_cells_type3', 'Type 3'),
    ('tumor_cells_type4', 'Type 4'),
    ('tumor_cells_type5_dead', 'Type 5 (Dead)')
]

colors_CARTopiaX = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
colors_paper = ['#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6']

# --- Absolute number of each cell type ---
fig, ax_abs = plt.subplots(figsize=(12, 7))
for idx, (col, label) in enumerate(cell_types):
    # CARTopiaX: absolute number of each cell type
    if csv_dataframes:
        all_type_counts = []
        for df_csv in filtered_csv_dfs:
            counts = np.interp(
                csv_time_points,
                df_csv['total_days'],
                df_csv[col]
            )
            all_type_counts.append(counts)
        all_type_counts = np.array(all_type_counts)
        mean_counts = np.mean(all_type_counts, axis=0)
        std_counts = np.std(all_type_counts, axis=0)
        ax_abs.plot(csv_time_points, mean_counts, color=colors_CARTopiaX[idx], linestyle='-', linewidth=2, label=f'CARTopiaX {label} (Abs)')
        ax_abs.fill_between(csv_time_points, mean_counts - std_counts, mean_counts + std_counts,
                            color=colors_CARTopiaX[idx], alpha=0.2)

    # Paper model: absolute number of each cell type
    if paper_dataframes:
        all_type_counts_paper = []
        for df_paper in filtered_paper_dfs:
            counts_paper = np.interp(
                paper_time_points,
                df_paper['total_days'],
                df_paper[col]
            )
            all_type_counts_paper.append(counts_paper)
        all_type_counts_paper = np.array(all_type_counts_paper)
        mean_counts_paper = np.mean(all_type_counts_paper, axis=0)
        std_counts_paper = np.std(all_type_counts_paper, axis=0)
        ax_abs.plot(paper_time_points, mean_counts_paper, color=colors_paper[idx], linestyle='--', linewidth=2, label=f'Nature Paper {label} (Abs)')
        ax_abs.fill_between(paper_time_points, mean_counts_paper - std_counts_paper, mean_counts_paper + std_counts_paper,
                            color=colors_paper[idx], alpha=0.2)

ax_abs.set_xlabel('Time (days)')
ax_abs.set_ylabel('Number of Cells')
ax_abs.set_title('Absolute Number of Each Tumor Cell Type Over Time')
ax_abs.legend(loc='best')
ax_abs.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('./out/type_of_cells_absolute_numbers.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Percentage of each cell type ---
fig, ax_pct = plt.subplots(figsize=(12, 7))
for idx, (col, label) in enumerate(cell_types):
    # CARTopiaX: percentage of each cell type
    if csv_dataframes:
        all_type_percent = []
        for df_csv in filtered_csv_dfs:
            percent = np.interp(
                csv_time_points,
                df_csv['total_days'],
                100 * df_csv[col] / df_csv['num_tumor_cells']
            )
            all_type_percent.append(percent)
        all_type_percent = np.array(all_type_percent)
        mean_percent = np.mean(all_type_percent, axis=0)
        std_percent = np.std(all_type_percent, axis=0)
        ax_pct.plot(csv_time_points, mean_percent, color=colors_CARTopiaX[idx], linestyle='-', linewidth=2, label=f'CARTopiaX {label} (%)')
        ax_pct.fill_between(csv_time_points, mean_percent - std_percent, mean_percent + std_percent,
                            color=colors_CARTopiaX[idx], alpha=0.2)

    # Paper model: percentage of each cell type
    if paper_dataframes:
        all_type_percent_paper = []
        for df_paper in filtered_paper_dfs:
            percent_paper = np.interp(
                paper_time_points,
                df_paper['total_days'],
                100 * df_paper[col] / df_paper['num_tumor_cells']
            )
            all_type_percent_paper.append(percent_paper)
        all_type_percent_paper = np.array(all_type_percent_paper)
        mean_percent_paper = np.mean(all_type_percent_paper, axis=0)
        std_percent_paper = np.std(all_type_percent_paper, axis=0)
        ax_pct.plot(paper_time_points, mean_percent_paper, color=colors_paper[idx], linestyle='--', linewidth=2, label=f'Nature Paper {label} (%)')
        ax_pct.fill_between(paper_time_points, mean_percent_paper - std_percent_paper, mean_percent_paper + std_percent_paper,
                            color=colors_paper[idx], alpha=0.2)

ax_pct.set_xlabel('Time (days)')
ax_pct.set_ylabel('Percentage of Tumor Cells (%)')
ax_pct.set_title('Percentage of Each Tumor Cell Type Over Time')
ax_pct.legend(loc='best')
ax_pct.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('./out/type_of_cells_porcentage_populations.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Oncoprotein ---
fig, ax_onco = plt.subplots(figsize=(10, 6))
ax_oxy = ax_onco.twinx()  # Secondary y-axis

# --- Oncoprotein (left y-axis) ---
if csv_dataframes:
    all_onco = []
    for df_csv in filtered_csv_dfs:
        onco = np.interp(csv_time_points, df_csv['total_days'], df_csv['average_oncoprotein'])
        all_onco.append(onco)
    all_onco = np.array(all_onco)
    mean_onco = np.mean(all_onco, axis=0)
    std_onco = np.std(all_onco, axis=0)
    ax_onco.plot(csv_time_points, mean_onco, color='#e41a1c', linestyle='-', linewidth=2, label='CARTopiaX Oncoprotein (Mean)')
    ax_onco.fill_between(csv_time_points, mean_onco - std_onco, mean_onco + std_onco,
                   color='#e41a1c', alpha=0.2)
if paper_dataframes:
    all_onco_paper = []
    for df_paper in filtered_paper_dfs:
        onco_paper = np.interp(paper_time_points, df_paper['total_days'], df_paper['average_oncoprotein'])
        all_onco_paper.append(onco_paper)
    all_onco_paper = np.array(all_onco_paper)
    mean_onco_paper = np.mean(all_onco_paper, axis=0)
    std_onco_paper = np.std(all_onco_paper, axis=0)
    ax_onco.plot(paper_time_points, mean_onco_paper, color='#e41a1c', linestyle='--', linewidth=2, label='Paper Oncoprotein (Mean)')
    ax_onco.fill_between(paper_time_points, mean_onco_paper - std_onco_paper, mean_onco_paper + std_onco_paper,
                   color='#e41a1c', alpha=0.2)

# --- Oxygen (right y-axis) ---
if csv_dataframes:
    all_oxy = []
    for df_csv in filtered_csv_dfs:
        oxy = np.interp(csv_time_points, df_csv['total_days'], df_csv['average_oxygen_cancer_cells'])
        all_oxy.append(oxy)
    all_oxy = np.array(all_oxy)
    mean_oxy = np.mean(all_oxy, axis=0)
    std_oxy = np.std(all_oxy, axis=0)
    ax_oxy.plot(csv_time_points, mean_oxy, color='#377eb8', linestyle='-', linewidth=2, label='CARTopiaX Oxygen (Mean)')
    ax_oxy.fill_between(csv_time_points, mean_oxy - std_oxy, mean_oxy + std_oxy,
                   color='#377eb8', alpha=0.2)
if paper_dataframes:
    all_oxy_paper = []
    for df_paper in filtered_paper_dfs:
        oxy_paper = np.interp(paper_time_points, df_paper['total_days'], df_paper['average_level_of_oxygen_cancer_cells'])
        all_oxy_paper.append(oxy_paper)
    all_oxy_paper = np.array(all_oxy_paper)
    mean_oxy_paper = np.mean(all_oxy_paper, axis=0)
    std_oxy_paper = np.std(all_oxy_paper, axis=0)
    ax_oxy.plot(paper_time_points, mean_oxy_paper, color='#377eb8', linestyle='--', linewidth=2, label='Paper Oxygen (Mean)')
    ax_oxy.fill_between(paper_time_points, mean_oxy_paper - std_oxy_paper, mean_oxy_paper + std_oxy_paper,
                   color='#377eb8', alpha=0.2)

ax_onco.set_xlabel('Time (days)')
ax_onco.set_ylabel('Average Oncoprotein Level', color='#e41a1c')
ax_oxy.set_ylabel('Average Oxygen Level', color='#377eb8')
ax_onco.tick_params(axis='y', labelcolor='#e41a1c')
ax_oxy.tick_params(axis='y', labelcolor='#377eb8')
ax_onco.set_title('Average Oncoprotein & Oxygen Levels Over Time')

# Legends for both axes
lines_onco, labels_onco = ax_onco.get_legend_handles_labels()
lines_oxy, labels_oxy = ax_oxy.get_legend_handles_labels()
ax_onco.legend(lines_onco + lines_oxy, labels_onco + labels_oxy, loc='best')

ax_onco.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('./out/oncoprotein_and_oxygen.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Tumor Cells and Tumor Radius Over Time ---
fig, ax_cells = plt.subplots(figsize=(10, 6))
ax_radius = ax_cells.twinx()  # Secondary y-axis for radius

# --- Number of tumor cells (left y-axis) ---
if csv_dataframes:
    ax_cells.plot(csv_time_points, csv_mean_cells, 
                  color='red', linestyle='-', linewidth=2, label='CARTopiaX Tumor Cells (Mean)')
    ax_cells.fill_between(csv_time_points, 
                         csv_mean_cells - csv_std_cells, 
                         csv_mean_cells + csv_std_cells,
                         color='red', alpha=0.2)
if paper_dataframes:
    ax_cells.plot(paper_time_points, paper_mean_cells, 
                  color='red', linestyle='--', linewidth=2, label='Nature Paper Tumor Cells (Mean)')
    ax_cells.fill_between(paper_time_points, 
                         paper_mean_cells - paper_std_cells, 
                         paper_mean_cells + paper_std_cells,
                         color='red', alpha=0.2)

# --- Tumor radius (right y-axis) ---
if csv_dataframes:
    all_radius = []
    for df_csv in filtered_csv_dfs:
        radius = np.interp(csv_time_points, df_csv['total_days'], df_csv['tumor_radius'])
        all_radius.append(radius)
    all_radius = np.array(all_radius)
    mean_radius = np.mean(all_radius, axis=0)
    std_radius = np.std(all_radius, axis=0)
    ax_radius.plot(csv_time_points, mean_radius, color='purple', linestyle='-', linewidth=2, label='CARTopiaX Tumor Radius (Mean)')
    ax_radius.fill_between(csv_time_points, mean_radius - std_radius, mean_radius + std_radius,
                          color='purple', alpha=0.2)
if paper_dataframes:
    all_radius_paper = []
    for df_paper in filtered_paper_dfs:
        radius_paper = np.interp(paper_time_points, df_paper['total_days'], df_paper['tumor_radius'])
        all_radius_paper.append(radius_paper)
    all_radius_paper = np.array(all_radius_paper)
    mean_radius_paper = np.mean(all_radius_paper, axis=0)
    std_radius_paper = np.std(all_radius_paper, axis=0)
    ax_radius.plot(paper_time_points, mean_radius_paper, color='purple', linestyle='--', linewidth=2, label='Nature Paper Tumor Radius (Mean)')
    ax_radius.fill_between(paper_time_points, mean_radius_paper - std_radius_paper, mean_radius_paper + std_radius_paper,
                          color='purple', alpha=0.2)

ax_cells.set_xlabel('Time (days)')
ax_cells.set_ylabel('Number of Tumor Cells', color='red')
ax_radius.set_ylabel('Tumor Radius', color='purple')
ax_cells.tick_params(axis='y', labelcolor='red')
ax_radius.tick_params(axis='y', labelcolor='purple')
ax_cells.set_title('Tumor Cells and Tumor Radius Over Time')

# Combine legends
lines_cells, labels_cells = ax_cells.get_legend_handles_labels()
lines_radius, labels_radius = ax_radius.get_legend_handles_labels()
ax_cells.legend(lines_cells + lines_radius, labels_cells + labels_radius, loc='best')

ax_cells.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('./out/num_cells_and_tumor_radius.png', dpi=300, bbox_inches='tight')
plt.show()

print("Comparison plots generated and saved in the './out/' directory.")