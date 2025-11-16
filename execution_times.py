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
import numpy as np
import re

df = pd.read_csv('./data/execution_times.csv')

# Function to parse time and convert to total minutes
def parse_time_to_minutes(time_str):
    match = re.match(r"(\d+)m([\d,\.]+)s", time_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2).replace(',', '.'))  # Replace ',' with '.' for decimals
        return minutes + seconds / 60  # Convert seconds to minutes
    else:
        raise ValueError(f"Invalid time format: {time_str}")

data_to_plot = []
positions = []
colors = []

dose_categories = ['0doses', '1dose', '2doses']
sources = ['CARTopiaX', 'Nature']

for i, dose in enumerate(dose_categories):
    for j, source in enumerate(sources):
        col_name = f"{dose}_{source}"
        times = df[col_name].apply(parse_time_to_minutes).values  # Convert to minutes
        data_to_plot.append(times)
        positions.append(i)  # Same position for same dose
        colors.append('royalblue' if source == 'CARTopiaX' else 'crimson')

fig, ax = plt.subplots(figsize=(10, 6))

cartopia_means = [np.mean(data) for data, color in zip(data_to_plot, colors) if color == 'royalblue']
nature_means = [np.mean(data) for data, color in zip(data_to_plot, colors) if color == 'crimson']
cartopia_stds = [np.std(data) for data, color in zip(data_to_plot, colors) if color == 'royalblue']
nature_stds = [np.std(data) for data, color in zip(data_to_plot, colors) if color == 'crimson']

if len(cartopia_means) != len(nature_means):
    raise ValueError("The lists of means for CARTopiaX and Nature do not match in length.")

x = np.arange(len(cartopia_means))
width = 0.35

bars1 = ax.bar(x - width / 2, cartopia_means, width, label='CARTopiaX', color='#cc781f')
bars2 = ax.bar(x + width / 2, nature_means, width, label='ABM Nature Paper', color='#2a9aeb')

ax.errorbar(x - width / 2, cartopia_means, yerr=cartopia_stds, fmt='o', color='black', capsize=10, capthick=2)
ax.errorbar(x + width / 2, nature_means, yerr=nature_stds, fmt='o', color='black', capsize=10, capthick=2)

ax.set_ylabel('Execution Time (minutes)', fontsize=16)
ax.set_title('CARTopiaX vs ABM Nature Paper - mean execution time ± SD', fontsize=20)
ax.set_xticks(x)
ax.set_xticklabels(["Control", "1 dose (1:1)", "2 doses (1:1)"], fontsize=16)
ax.tick_params(axis='y', labelsize=14)
ax.legend(fontsize=14)

ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

plt.tight_layout()
plt.savefig('./out/execution_times_comparison.png', dpi=300)