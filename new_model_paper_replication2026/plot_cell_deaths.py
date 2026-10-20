import os

import matplotlib.pyplot as plt
import numpy as np

# Reuse the exact same loading / averaging logic (and plot style) as the
# single-attribute radius script, so values behave identically
from plots_new_model_dependent_on_radius import (
    load_executions,
    compute_mean_std_over_radius,
)

# ---------------------------------------------------------------------------
# CONFIGURATION: edit only this section
# ---------------------------------------------------------------------------

BASE_DIR = './data/last_no_treatment_cup'                # Base folder containing the subfolders
CSV_NAME = 'data_dependent_on_radius_tumor.csv'       # CSV filename inside each subfolder
FOLDER_PATTERN = 'execution_seed_*'                   # Pattern used to find the subfolders

TIME_COLUMN = 'total_minutes'                         # Column used to select the timestamp
MINUTE = 4320                                         # Timestamp (in minutes) to plot

DIVIDING_FACTOR = 1                                   # Divide values by this factor

# Death causes: column prefix -> legend label
DEATH_CAUSES = {
    "dead_tumor_cells_lack_of_oxygen_radius": "Lack of oxygen",
    "dead_tumor_cells_lack_of_glucose_radius": "Lack of glucose",
    "dead_tumor_cells_random_natural_causes_radius": "Random natural causes",
    "dead_tumor_cells_cartcell_kill_radius": "CAR-T kill",
}

# Plots generated in order: first absolute counts, then densities (per um^2)
PLOTS = [
    {
        'name': 'absolute',
        'APPLY_RADIAL_NORMALIZATION': False,
        'X_MIN': 0,
        'Y_MIN': 0,
        'Y_MAX': 180,
    },
    {
        'name': 'relative',
        'APPLY_RADIAL_NORMALIZATION': True,
        'X_MIN': 150,       # Avoid the noisy inner points when normalizing
        'Y_MIN': 0,
        'Y_MAX': 0.0004,
    },
]

# Third plot: percentage of deaths of each cause per radius (sums to 100%)
PERCENTAGE_X_MIN = 150

OUTPUT_DIR = './out'                                  # Folder where the figures are saved

# ---------------------------------------------------------------------------


def plot_death_percentages(dataframes, x_min):
    """For each radius, plot the share of deaths of each cause (computed from
    the mean absolute counts over seeds). Radii without deaths give 0% for all."""
    means = {}
    radii = None
    for attribute, label in DEATH_CAUSES.items():
        radii, mean_values, _ = compute_mean_std_over_radius(
            dataframes, TIME_COLUMN, MINUTE, attribute, False, DIVIDING_FACTOR
        )
        means[label] = mean_values

    total = np.sum(list(means.values()), axis=0)
    safe_total = np.where(total > 0, total, 1)

    if x_min is not None:
        x_mask = radii >= x_min
    else:
        x_mask = np.ones_like(radii, dtype=bool)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for label, mean_values in means.items():
        percentages = np.where(total > 0, 100 * mean_values / safe_total, 0)
        ax.plot(radii[x_mask], percentages[x_mask], marker='o', linewidth=2, label=label)

    print("Plot: percentage")
    print(f"Minute: {MINUTE}")
    print(f"Radii without deaths (all causes 0%): {int(np.sum(total[x_mask] == 0))}")

    ax.set_xlabel('Radius (um)')
    ax.set_ylabel('Share of tumor cell deaths (%)')
    ax.set_title(f'Tumor cell death causes (%) vs radius - minute {MINUTE}')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)

    if x_min is not None:
        ax.set_xlim(left=x_min)
        # Explicitly mark where the X axis starts
        x_ticks = [t for t in ax.get_xticks() if x_min < t <= ax.get_xlim()[1]]
        ax.set_xticks([x_min] + x_ticks)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f'cell_death_causes_vs_radius_minute_{MINUTE}_percentage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")


def plot_death_causes(dataframes, apply_radial_normalization, x_min, y_min, y_max, name):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    radii = None

    for attribute, label in DEATH_CAUSES.items():
        radii, mean_values, std_values = compute_mean_std_over_radius(
            dataframes, TIME_COLUMN, MINUTE, attribute,
            apply_radial_normalization, DIVIDING_FACTOR
        )

        if x_min is not None:
            x_mask = radii >= x_min
            radii, mean_values, std_values = radii[x_mask], mean_values[x_mask], std_values[x_mask]

        line, = ax.plot(radii, mean_values, marker='o', linewidth=2, label=label)
        ax.fill_between(radii,
                        mean_values - std_values,
                        mean_values + std_values,
                        color=line.get_color(), alpha=0.2)

    print(f"Plot: {name}")
    print(f"Minute: {MINUTE}")
    print(f"Radius range with data: {radii[0]} to {radii[-1]}")
    print(f"Number of radius points: {len(radii)}")
    print(f"Radial normalization applied: {apply_radial_normalization}")

    ax.set_xlabel('Radius (um)')
    ax.set_ylabel('Dead tumor cells' + (' (per um^2)' if apply_radial_normalization else ''))
    ax.set_title(f'Tumor cell deaths by cause vs radius - minute {MINUTE}')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    if y_min is not None or y_max is not None:
        ax.set_ylim(bottom=y_min, top=y_max)

    if x_min is not None:
        ax.set_xlim(left=x_min)
        # Explicitly mark where the X axis starts
        x_ticks = [t for t in ax.get_xticks() if x_min < t <= ax.get_xlim()[1]]
        ax.set_xticks([x_min] + x_ticks)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f'cell_death_causes_vs_radius_minute_{MINUTE}_{name}.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dataframes = load_executions(BASE_DIR, FOLDER_PATTERN, CSV_NAME)
    if not dataframes:
        print("No data found to plot.")
        return

    for cfg in PLOTS:
        plot_death_causes(
            dataframes,
            cfg['APPLY_RADIAL_NORMALIZATION'],
            cfg['X_MIN'], cfg['Y_MIN'], cfg['Y_MAX'],
            cfg['name'],
        )

    plot_death_percentages(dataframes, PERCENTAGE_X_MIN)

    plt.show()


if __name__ == '__main__':
    main()
