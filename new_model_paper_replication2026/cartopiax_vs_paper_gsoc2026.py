import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dataset_values_preprocessing as paper_cfg
from plots_new_model_dependent_on_radius import (
    CSV_NAME,
    FOLDER_PATTERN,
    TIME_COLUMN,
    compute_mean_std_over_radius,
    load_executions,
)

# ---------------------------------------------------------------------------
# CONFIGURATION: edit only this section
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
PAPER_DIR = os.path.join(DATA_DIR, 'data_paper')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'out')

ATTRIBUTE = 'tumor_cells_type5_dead_radius'

# (label, simulation folder, paper name prefix). The paper file is f'{prefix}_{hours}h'
SCENARIOS = [
    ('no_treatment_no_cap', 'last_no_treatment_no_cap', 'no_treatment_no_cap_28000'),
    ('no_treatment_cap', 'last_no_treatment_cap', 'no_treatment_with_cap_28000'),
    ('treatment_no_cap', 'last_treatment_no_cap', '20_1_CART_treatment_no_cap_28000'),
    ('treatment_cap', 'last_treatment_cap', '20_1_CART_treatment_with_cap_28000'),
]
HOURS = [24, 48, 72]

# Absolute plot
X_MIN_ABSOLUTE = 0
X_MAX = 3000
Y_MIN_ABSOLUTE = 0
Y_MAX_ABSOLUTE = 180

# Normalized (per um^2) plot
X_MIN_NORMALIZED = 150
Y_MIN_NORMALIZED = 0
Y_MAX_NORMALIZED = 0.0004

# ---------------------------------------------------------------------------

plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 14,
    'figure.titlesize': 22
})


def load_paper_points(paper_name):
    """Raw points digitized from the paper, rescaled to (radius, value) the same
    way dataset_values_preprocessing does. Returns None if the file is missing."""
    path = os.path.join(PAPER_DIR, paper_name + '.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, sep=';', decimal=',', header=None, names=['X', 'Y'])
    x = paper_cfg.X_MIN + np.clip(df['X'].to_numpy(), 0, 1) * (paper_cfg.X_MAX - paper_cfg.X_MIN)
    y = paper_cfg.Y_MIN + np.clip(df['Y'].to_numpy(), 0, 1) * (paper_cfg.Y_MAX - paper_cfg.Y_MIN)
    order = np.argsort(x)
    return x[order], y[order]


def load_paper_spline_normalized(paper_name):
    """Spline of the paper data already normalized by ring area. Returns None if missing."""
    path = os.path.join(PAPER_DIR, paper_name, paper_name + '_clean_normalized.csv')
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    return df['X'].to_numpy(), df['Y'].to_numpy()


def apply_x_range(x_min, *arrays):
    mask = (arrays[0] >= x_min) & (arrays[0] <= X_MAX)
    return tuple(a[mask] for a in arrays)


def plot_comparison(radii, mean_values, std_values, paper_x, paper_y, normalized,
                    title, output_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(radii, mean_values, marker='o', color='blue', linewidth=2, label='CARTopiaX (Mean)')
    ax.fill_between(radii, mean_values - std_values, mean_values + std_values,
                    color='blue', alpha=0.2, label='Mean ± Std')
    if normalized:
        ax.plot(paper_x, paper_y, color='red', linewidth=2, label='Paper (spline)')
    else:
        ax.scatter(paper_x, paper_y, s=20, color='red', zorder=3, label='Paper (points)')

    x_min = X_MIN_NORMALIZED if normalized else X_MIN_ABSOLUTE
    ax.set_xlabel('Radius (um)')
    ax.set_ylabel('Dead tumor cells' + (' (per um^2)' if normalized else ''))
    ax.set_title(title)
    ax.set_xlim(x_min, X_MAX)
    ax.set_ylim(Y_MIN_NORMALIZED if normalized else Y_MIN_ABSOLUTE,
                Y_MAX_NORMALIZED if normalized else Y_MAX_ABSOLUTE)
    if normalized:
        # Explicitly mark where the X axis starts
        x_ticks = [t for t in ax.get_xticks() if x_min + 300 < t <= X_MAX]
        ax.set_xticks([x_min] + x_ticks)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Figure saved to: {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for label, sim_folder, paper_prefix in SCENARIOS:
        dataframes = load_executions(os.path.join(DATA_DIR, sim_folder), FOLDER_PATTERN, CSV_NAME)
        if not dataframes:
            print(f"Skipping {label}: no simulation data")
            continue

        for hours in HOURS:
            paper_name = f'{paper_prefix}_{hours}h'
            minute = hours * 60

            for normalized in (False, True):
                kind = 'relative' if normalized else 'absolute'
                paper = (load_paper_spline_normalized(paper_name) if normalized
                         else load_paper_points(paper_name))
                if paper is None:
                    print(f"Skipping {label} {hours}h {kind}: paper data '{paper_name}' not found")
                    continue

                radii, mean_values, std_values = compute_mean_std_over_radius(
                    dataframes, TIME_COLUMN, minute, ATTRIBUTE, normalized, 1
                )
                x_min = X_MIN_NORMALIZED if normalized else X_MIN_ABSOLUTE
                radii, mean_values, std_values = apply_x_range(x_min, radii, mean_values, std_values)
                paper_x, paper_y = apply_x_range(x_min, *paper)

                plot_comparison(
                    radii, mean_values, std_values, paper_x, paper_y, normalized,
                    f'{label} - {hours}h',
                    os.path.join(OUTPUT_DIR, f'{ATTRIBUTE}_{label}_{hours}h_vs_paper_{kind}.png'),
                )


if __name__ == '__main__':
    main()
