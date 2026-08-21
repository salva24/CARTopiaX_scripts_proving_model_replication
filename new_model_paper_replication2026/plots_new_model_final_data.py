import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# CONFIGURATION: edit only this section
# ---------------------------------------------------------------------------

BASE_DIR = './data/no_cup_no_aging_2800_real_oxygen'                                        # Base folder containing the subfolders 
CSV_NAME = 'final_data.csv'                          # CSV filename inside each subfolder
FIELD = 'num_tumor_cells'                            # Column (field) to plot
TIME_FIELD = 'total_days'                            # Time column

FOLDER_PATTERN = 'execution_seed_*'                  # Pattern used to find the subfolders
OUTPUT_DIR = './out'                                 # Folder where the figure is saved
OUTPUT_NAME = f'{FIELD}_mean_std.png'         

# ---------------------------------------------------------------------------
       # Output file name
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 14,
    'figure.titlesize': 22
})


def load_executions(base_dir, folder_pattern, csv_name):
    """Find all subfolders matching the pattern and load their CSV file."""
    search_path = os.path.join(base_dir, folder_pattern)
    execution_folders = sorted(glob.glob(search_path))

    dataframes = []
    for folder in execution_folders:
        csv_path = os.path.join(folder, csv_name)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            dataframes.append(df)
            print(f"Loaded: {csv_path}")
        else:
            print(f"Warning: {csv_path} not found")

    print(f"Loaded {len(dataframes)} executions from '{search_path}'")
    return dataframes


def compute_mean_std(dataframes, time_field, field):
    """Interpolate all executions onto a common time axis and compute the
    mean and standard deviation of the given field."""
    if not dataframes:
        return None, None, None

    # The time axis of the first execution is used as reference
    time_points = dataframes[0][time_field].values

    all_values = []
    for df in dataframes:
        values = np.interp(time_points, df[time_field], df[field])
        all_values.append(values)

    all_values = np.array(all_values)
    mean_values = np.mean(all_values, axis=0)
    std_values = np.std(all_values, axis=0)

    return time_points, mean_values, std_values


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dataframes = load_executions(BASE_DIR, FOLDER_PATTERN, CSV_NAME)
    time_points, mean_values, std_values = compute_mean_std(
        dataframes, TIME_FIELD, FIELD
    )

    if time_points is None:
        print("No data found to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_points, mean_values, color='blue', linewidth=2,
            label=f'{FIELD} (Mean)')
    ax.fill_between(time_points,
                     mean_values - std_values,
                     mean_values + std_values,
                     color='blue', alpha=0.2, label='Mean ± Std')

    ax.set_xlabel('Time (days)')
    ax.set_ylabel(FIELD)
    ax.set_title(f'{FIELD} over time (mean across seeds)')
    ax.legend(loc='best')
    ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Figure saved to: {output_path}")


if __name__ == '__main__':
    main()