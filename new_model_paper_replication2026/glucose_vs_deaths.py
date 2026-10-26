import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# CONFIGURATION: edit only this section
# ---------------------------------------------------------------------------

RUNS = [                                             # (base folder containing the subfolders, panel title), left to right
    ('./data/last_no_treatment_cap', 'Without treatment'),
    ('./data/last_treatment_cap', 'With treatment'),
]
CSV_NAME = 'final_data.csv'                          # CSV filename inside each subfolder
COUNT_FIELDS = {                                     # Fields plotted on the left Y axis (cell counts)
    "dead_tumor_cells_lack_of_glucose": 'red',
    "tumor_cells_type5_dead": 'black',
}
LEFT_YMAX = 4600                                     # Fixed upper limit of the left Y axis
GLUCOSE_FIELD = "average_glucose_all_cells"          # Field plotted on the right Y axis
GLUCOSE_COLOR = 'blue'
TIME_FIELD = 'total_days'                            # Time column

FOLDER_PATTERN = 'execution_seed_*'                  # Pattern used to find the subfolders
OUTPUT_DIR = './out'                                 # Folder where the figure is saved
OUTPUT_NAME = 'glucose_vs_deaths_mean.png'           # Output file name

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


def plot_run(ax, dataframes, title):
    """Draw the dead-cell counts (left Y axis) and the average glucose
    (right Y axis) of one set of executions on the given axes."""
    handles = []

    # Cell counts on the left Y axis
    for field, color in COUNT_FIELDS.items():
        time_points, mean_values, _ = compute_mean_std(
            dataframes, TIME_FIELD, field
        )
        line, = ax.plot(time_points, mean_values, color=color, linewidth=2,
                        label=field)
        handles.append(line)

    ax.set_xlabel('Time (days)')
    ax.set_ylabel('Number of dead cells')
    ax.set_ylim(0, LEFT_YMAX)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Average glucose on the right Y axis (different scale)
    ax_glucose = ax.twinx()
    time_points, mean_values, _ = compute_mean_std(
        dataframes, TIME_FIELD, GLUCOSE_FIELD
    )
    line, = ax_glucose.plot(time_points, mean_values, color=GLUCOSE_COLOR,
                            linewidth=2, linestyle='--', label=GLUCOSE_FIELD)
    handles.append(line)
    ax_glucose.set_ylabel(GLUCOSE_FIELD, color=GLUCOSE_COLOR)
    ax_glucose.tick_params(axis='y', labelcolor=GLUCOSE_COLOR)

    ax.set_title(title)
    ax.legend(handles=handles, loc='best')


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, len(RUNS), figsize=(8 * len(RUNS), 6))
    for ax, (base_dir, title) in zip(axes, RUNS):
        dataframes = load_executions(base_dir, FOLDER_PATTERN, CSV_NAME)
        if not dataframes:
            print(f"No data found to plot for '{base_dir}'.")
            ax.set_title(f'{title} (no data)')
            continue
        plot_run(ax, dataframes, title)

    fig.suptitle('Glucose and cell deaths over time (mean across seeds)')
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Figure saved to: {output_path}")


if __name__ == '__main__':
    main()