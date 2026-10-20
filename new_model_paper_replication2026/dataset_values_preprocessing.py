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
from scipy.interpolate import UnivariateSpline

INPUT_DIR = "data/data_paper"
SPLINE_DEGREE = 3
#smoothing factor: 0 interpolates every point, larger values give smoother curves, None uses scipy's default
SPLINE_SMOOTHING = 1000
NORMALIZE_CYLINDER = True # False for oxygen

X_MIN = 0
X_MAX = 3000
Y_MIN = 0
Y_MAX = 200 #0.2 for oxygen

Y_MIN_SCALED = 0
Y_MAX_SCALED = 180 #0.2 for oxygen

Y_MIN_SPLINE_FIT = 0
Y_MAX_SPLINE_FIT = 180 #0.2 for oxygen

Y_MIN_NORMALIZED = 0
Y_MAX_NORMALIZED = 0.0004
#the density plot ignores the points with X below this value
X_MIN_DENSITY = 150

N_SAMPLES = 100
#the implicit number of sections that are present in the original data for scaling
CALIBRATION_N_SECTIONS = 100

COMPUTE_TOTAL_NUMBER = True

rescale_factor = CALIBRATION_N_SECTIONS / N_SAMPLES


def process_file(input_file):
    name = os.path.splitext(os.path.basename(input_file))[0]
    #outputs are stored in a subfolder named after the input file
    output_dir = os.path.join(os.path.dirname(input_file), name)
    os.makedirs(output_dir, exist_ok=True)
    output_prefix = os.path.join(output_dir, name)

    df = pd.read_csv(
        input_file,
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

    #outside the data range the spline keeps the boundary value instead of extrapolating
    model = UnivariateSpline(x, y, k=SPLINE_DEGREE, s=SPLINE_SMOOTHING, ext="const")

    x_sample = np.linspace(X_MIN, X_MAX, N_SAMPLES)
    y_sample = model(x_sample)
    y_sample = np.clip(y_sample, Y_MIN, None)

    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, s=10, c="r", label="Data")
    plt.plot(x_sample, y_sample, color="green", lw=2, label=f"Spline (degree={SPLINE_DEGREE}, s={SPLINE_SMOOTHING})")
    plt.xlim(X_MIN, X_MAX)
    plt.ylim(Y_MIN_SPLINE_FIT, Y_MAX_SPLINE_FIT)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.legend()
    plt.title(name+" - Spline Fit")
    #store the image
    plt.savefig(output_prefix + "_spline_fit.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_prefix + '_spline_fit.png'}")

    #if the N_samples is different from the calibration sections, we need to rescale the y_sample values
    y_sample_scaled = y_sample * rescale_factor

    output_file = output_prefix + "_clean.csv"

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
    plt.title(name + f" - Scaled ({N_SAMPLES} samples)")
    plt.grid(True)
    if Y_MIN_SCALED is not None or Y_MAX_SCALED is not None:
        plt.ylim(bottom=Y_MIN_SCALED, top=Y_MAX_SCALED)
    plt.legend()
    scaled_plot_file = output_prefix + "_scaled_" + str(N_SAMPLES) + "_samples.png"
    plt.savefig(scaled_plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {scaled_plot_file}")

    if NORMALIZE_CYLINDER:
        w = (X_MAX - X_MIN) / N_SAMPLES
        edges = X_MIN + w * np.arange(N_SAMPLES + 1)
        r_in = edges[:-1]
        r_out = edges[1:]
        ring_area = np.pi * (r_out**2 - r_in**2)

        y_sample_normalized = y_sample_scaled / ring_area

        plt.figure(figsize=(6, 4))
        density_mask = x_sample >= X_MIN_DENSITY
        plt.plot(x_sample[density_mask], y_sample_normalized[density_mask], color="green", lw=2)
        plt.title(name+" - Density Distribution")
        plt.xlim(X_MIN_DENSITY, X_MAX)
        #explicitly mark where the X axis starts
        density_ticks = [t for t in plt.xticks()[0] if X_MIN_DENSITY < t <= X_MAX]
        plt.xticks([X_MIN_DENSITY] + density_ticks)
        plt.ylim(Y_MIN_NORMALIZED, Y_MAX_NORMALIZED)
        plt.xlabel("X (radius)")
        plt.ylabel("Density")
        plt.grid(True)
        #store the image
        plt.savefig(output_prefix + "_density_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {output_prefix + '_density_distribution.png'}")

        output_file_normalized = output_prefix + "_clean_normalized.csv"
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

        output_file_sum = output_prefix + "_sum_values_"+str(CALIBRATION_N_SECTIONS)+"_split.txt"
        with open(output_file_sum, "w") as f:
            f.write(f"Sum of values: {sum_values}\n")


if __name__ == "__main__":
    for file_name in sorted(os.listdir(INPUT_DIR)):
        if file_name.lower().endswith(".csv"):
            print(f"Processing: {file_name}")
            process_file(os.path.join(INPUT_DIR, file_name))
