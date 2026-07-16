import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from numpy.polynomial import Polynomial

INPUT_FILE = "no_treatment_with_cup_28000_24h.csv"
POLYNOMIAL_DEGREE = 3
NORMALIZE_CYLINDER = True

X_MIN = 0
X_MAX = 3000
Y_MIN = 0
Y_MAX = 200

N_SAMPLES = 20

COMPUTE_TOTAL_NUMBER = True


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
plt.scatter(x, y, s=10, label="Data")
plt.plot(x_sample, y_sample, "r", lw=2, label="Polynomial fit")
plt.xlim(X_MIN, X_MAX)
plt.ylim(Y_MIN, Y_MAX)
plt.xlabel("X")
plt.ylabel("Y")
plt.plot(x_sample, y_sample, "r", lw=2, label=f"Polynomial (degree={POLYNOMIAL_DEGREE})")
plt.grid(True)
plt.title(os.path.splitext(INPUT_FILE)[0]+" - Polynomial Fit")
#store the image
plt.savefig(os.path.splitext(INPUT_FILE)[0] + "_polynomial_fit.png", dpi=300, bbox_inches='tight')

output_file = os.path.splitext(INPUT_FILE)[0] + "_clean.csv"

pd.DataFrame({
    "X": x_sample,
    "Y": y_sample
}).to_csv(output_file, index=False)

print(f"Saved: {output_file}")

if NORMALIZE_CYLINDER:
    w = (X_MAX - X_MIN) / N_SAMPLES
    edges = X_MIN + w * np.arange(N_SAMPLES + 1)
    r_in = edges[:-1]
    r_out = edges[1:]
    ring_area = np.pi * (r_out**2 - r_in**2)

    y_sample_normalized = y_sample / ring_area

    plt.figure(figsize=(6, 4))
    plt.plot(x_sample, y_sample_normalized, "g", lw=2)
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
    num_samples=100
    x_sample = np.linspace(X_MIN, X_MAX, num_samples)
    y_sample = model(x_sample)
    y_sample = np.clip(y_sample, Y_MIN, None)

    sum_values = np.sum(y_sample)

    output_file_sum = os.path.splitext(INPUT_FILE)[0] + "_sum_values_100_split.txt"
    with open(output_file_sum, "w") as f:
        f.write(f"Sum of values: {sum_values}\n")



    
        

