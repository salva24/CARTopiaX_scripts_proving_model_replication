# -----------------------------------------------------------------------------
# Copyright (C) 2026 Salvador de la Torre Gonzalez
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


import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT_FILE = "data/no_treatment_no_cup_28000_72h.csv"
POLYNOMIAL_DEGREE = 3
NORMALIZE_CYLINDER = True

X_MIN = 0
X_MAX = 3000
Y_MIN = 0
Y_MAX = 200

N_SAMPLES = 20
#the implicit number of sections that are present in the original data for scaling
CALIBRATION_N_SECTIONS = 100

COMPUTE_TOTAL_NUMBER = False

Y_MIN_SCALED = 0
Y_MAX_SCALED = None

rescale_factor = CALIBRATION_N_SECTIONS / N_SAMPLES #1.0 for oxygen levels

df = pd.read_csv(
    INPUT_FILE,
    sep=";",
    decimal=",",
    header=None,
    names=["X", "Y"]
)

x = df["X"].to_numpy()
y = df["Y"].to_numpy()

x = np.clip(x, 0, 1)
y = np.clip(y, 0, 1)

x = X_MIN + x * (X_MAX - X_MIN)
y = Y_MIN + y * (Y_MAX - Y_MIN)
order = np.argsort(x)
x = x[order]
y = y[order]

coeffs = np.polyfit(x, y, POLYNOMIAL_DEGREE)
model = np.poly1d(coeffs)

x_sample = np.linspace(X_MIN, X_MAX, N_SAMPLES)
y_sample = model(x_sample)
y_sample = np.clip(y_sample, Y_MIN, None)

plt.figure(figsize=(6, 4))
plt.scatter(x, y, s=10, c="r", label="Data")
plt.plot(x_sample, y_sample, color="green", lw=2, label="Polynomial fit")
plt.xlim(X_MIN, X_MAX)
plt.ylim(Y_MIN, Y_MAX)
plt.xlabel("X")
plt.ylabel("Y")
plt.plot(x_sample, y_sample, color="green", lw=2, label=f"Polynomial (degree={POLYNOMIAL_DEGREE})")
plt.grid(True)
plt.title(os.path.splitext(INPUT_FILE)[0]+" - Polynomial Fit")
#store the image
plt.savefig(os.path.splitext(INPUT_FILE)[0] + "_polynomial_fit.png", dpi=300, bbox_inches='tight')

#if the N_samples is different from the calibration sections, we need to rescale the y_sample values
y_sample_scaled = y_sample * rescale_factor

output_file = os.path.splitext(INPUT_FILE)[0] + "_clean.csv"

pd.DataFrame({
    "X": x_sample,
    "Y": y_sample_scaled
}).to_csv(output_file, index=False)

print(f"Saved: {output_file}")

# Plot the new scaled data
plt.figure(figsize=(6, 4))
plt.plot(x_sample, y_sample_scaled, color="green", lw=2, marker="o", label=f"Scaled ({N_SAMPLES} samples)")
plt.xlim(X_MIN, X_MAX)
plt.xlabel("X")
plt.ylabel("Y (scaled)")
plt.title(os.path.splitext(INPUT_FILE)[0] + f" - Scaled ({N_SAMPLES} samples)")
plt.grid(True)
if Y_MIN_SCALED is not None or Y_MAX_SCALED is not None:
    plt.ylim(bottom=Y_MIN_SCALED, top=Y_MAX_SCALED)
plt.legend()
scaled_plot_file = os.path.splitext(INPUT_FILE)[0] + "_scaled_" + str(N_SAMPLES) + "_samples.png"
plt.savefig(scaled_plot_file, dpi=300, bbox_inches='tight')
print(f"Saved: {scaled_plot_file}")

if NORMALIZE_CYLINDER:
    w = (X_MAX - X_MIN) / N_SAMPLES
    edges = X_MIN + w * np.arange(N_SAMPLES + 1)
    r_in = edges[:-1]
    r_out = edges[1:]
    ring_area = np.pi * (r_out**2 - r_in**2)

    y_sample_normalized = y_sample_scaled / ring_area

    plt.figure(figsize=(6, 4))
    plt.plot(x_sample, y_sample_normalized, color="green", lw=2)
    plt.title(os.path.splitext(INPUT_FILE)[0]+" - Density Distribution")
    plt.xlim(X_MIN, X_MAX)
    plt.xlabel("X (radius)")
    plt.ylabel("Density")
    plt.grid(True)
    #store the image
    plt.savefig(os.path.splitext(INPUT_FILE)[0] + "_density_distribution.png", dpi=300, bbox_inches='tight')


    output_file_normalized = os.path.splitext(INPUT_FILE)[0] + "_clean_normalized.csv"
    pd.DataFrame({
        "X": x_sample,
        "Y": y_sample_normalized
    }).to_csv(output_file_normalized, index=False)

    print(f"Saved: {output_file_normalized}")

if COMPUTE_TOTAL_NUMBER:
    num_samples=CALIBRATION_N_SECTIONS
    x_sample = np.linspace(X_MIN, X_MAX, num_samples)
    y_sample = model(x_sample)
    y_sample = np.clip(y_sample, Y_MIN, None)

    sum_values = np.sum(y_sample)

    output_file_sum = os.path.splitext(INPUT_FILE)[0] + "_sum_values_"+str(CALIBRATION_N_SECTIONS)+"_split.txt"
    with open(output_file_sum, "w") as f:
        f.write(f"Sum of values: {sum_values}\n")
