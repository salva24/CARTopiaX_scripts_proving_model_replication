"""
Copyright 2026 compiler-research.org, Salvador de la Torre Gonzalez
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
    SPDX-License-Identifier: Apache-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This script reads the per-radius bin values for a given attribute/minute,
fits a polynomial to those points (same approach as the standalone
polynomial-fit script), resamples the model at N_SAMPLES points, and sums
the resampled values to obtain the total number of dead cells.
"""

import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---- settings ----
CSV_PATH = "./new_model_paper_replication2026/with_cup_no_aging_28000_real_oxygen/execution_seed_1/data_dependent_on_radius_tumor.csv"
MINUTE = 4320  # change this to the minute you want to compute the total for
ATTRIBUTE = "tumor_cells_type5_dead_radius"  # change this to the attribute you want to sum
# other examples: "average_oncoprotein_radius", "average_oxygen_cancer_cells_radius",
# "num_alive_cells_radius", "num_alive_tumor_cells_radius", etc.

EXPECTED_N_BINS = 20  # sanity check: number of radial bins/coronas expected in the data

POLYNOMIAL_DEGREE = 3
N_SAMPLES = 20  # number of points to resample from the fitted polynomial
Y_MIN = 0  # lower clip for the fitted/sampled values (cell counts can't be negative)

OUTPUT_DIR = "./draft"

# ---- load data ----
df = pd.read_csv(CSV_PATH)
row = df[df["total_minutes"] == MINUTE].iloc[0]

# ---- find columns for the chosen attribute ----
pattern = re.compile(rf"^{re.escape(ATTRIBUTE)}_(\d+)_to_(\d+)$")
points = []
for col in df.columns:
    m = pattern.match(col)
    if m and pd.notna(row[col]):
        x_start, x_end = int(m.group(1)), int(m.group(2))
        radius = (x_start + x_end) / 2
        points.append((radius, x_start, x_end, row[col]))

if not points:
    raise SystemExit(f"No columns found matching attribute '{ATTRIBUTE}'")

points.sort(key=lambda p: p[0])
radii = np.array([p[0] for p in points], dtype=float)
raw_values = np.array([p[3] for p in points], dtype=float)
bin_starts = np.array([p[1] for p in points], dtype=float)
bin_ends = np.array([p[2] for p in points], dtype=float)

n_bins = len(points)
if n_bins != EXPECTED_N_BINS:
    print(
        f"Warning: found {n_bins} radial bins for attribute '{ATTRIBUTE}', "
        f"expected {EXPECTED_N_BINS}."
    )

X_MIN = bin_starts.min()
X_MAX = bin_ends.max()

# ---- fit polynomial to the raw (radius, value) points ----
coeffs = np.polyfit(radii, raw_values, POLYNOMIAL_DEGREE)
model = np.poly1d(coeffs)

# ---- resample the model at N_SAMPLES points ----
x_sample = np.linspace(X_MIN, X_MAX, N_SAMPLES)
y_sample = model(x_sample)
y_sample = np.clip(y_sample, Y_MIN, None)

# ---- compute total number of dead cells (sum of the resampled points) ----
total_dead_cells = np.sum(y_sample)

print(f"Attribute: {ATTRIBUTE}")
print(f"Minute: {MINUTE}")
print(f"Radius range with data: {radii[0]} to {radii[-1]}")
print(f"Number of original radial bins: {n_bins}")
print(f"Number of resampled points: {N_SAMPLES}")
print(f"Total dead cells (sum of resampled polynomial): {total_dead_cells}")

# ---- plot: raw points vs polynomial fit ----
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.figure(figsize=(6, 4))
plt.scatter(radii, raw_values, s=20, c="r", label="Data (bins)")
plt.plot(x_sample, y_sample, color="green", lw=2, label=f"Polynomial (degree={POLYNOMIAL_DEGREE})")
plt.xlim(X_MIN, X_MAX)
plt.xlabel("Radius (um)")
plt.ylabel(ATTRIBUTE)
plt.title(f"{ATTRIBUTE} - Polynomial Fit (minute {MINUTE})")
plt.grid(True)
plt.legend()
fit_plot_file = os.path.join(OUTPUT_DIR, f"{ATTRIBUTE}_minute_{MINUTE}_polynomial_fit.png")
plt.savefig(fit_plot_file, dpi=300, bbox_inches="tight")
print(f"Saved: {fit_plot_file}")

# ---- save result ----
output_file = os.path.join(OUTPUT_DIR, f"{ATTRIBUTE}_total_dead_cells_minute_{MINUTE}.txt")
with open(output_file, "w") as f:
    f.write(f"Attribute: {ATTRIBUTE}\n")
    f.write(f"Minute: {MINUTE}\n")
    f.write(f"Number of original radial bins: {n_bins}\n")
    f.write(f"Number of resampled points: {N_SAMPLES}\n")
    f.write(f"Total dead cells (sum of resampled polynomial): {total_dead_cells}\n")

print(f"Saved: {output_file}")