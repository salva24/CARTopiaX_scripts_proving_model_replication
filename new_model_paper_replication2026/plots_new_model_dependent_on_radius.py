import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
# ---------------------------------------------------------------------------
# CONFIGURATION: edit only this section
# ---------------------------------------------------------------------------
 
BASE_DIR = './data/temp2_allCart_no_cup'      # Base folder containing the subfolders
CSV_NAME = 'data_dependent_on_radius_tumor.csv'       # CSV filename inside each subfolder
FOLDER_PATTERN = 'execution_seed_*'                   # Pattern used to find the subfolders
 
TIME_COLUMN = 'total_minutes'                         # Column used to select the timestamp
MINUTE = 4320                                         # Timestamp (in minutes) to plot
 
ATTRIBUTE = 'tumor_cells_type5_dead_radius' # "num_alive_cart_cells_radius"  #'tumor_cells_type5_dead_radius'           # Attribute (column prefix) to plot
# Other examples: "average_oxygen_all_cells_radius", "average_oxygen_cancer_cells_radius",
# "num_alive_cells_radius", "num_alive_tumor_cells_radius", etc. 'num_dead_cells_radius'  

DIVIDING_FACTOR =1 # 585                                  # Divide values by this factor #585 to convert from mmHg to mol/m3
APPLY_RADIAL_NORMALIZATION = False                    # Divide each value by its ring area (per um^2)
 
Y_MIN = 0
Y_MAX = None
 
OUTPUT_DIR = './out'                                  # Folder where the figure is saved
OUTPUT_NAME = f'{ATTRIBUTE}_vs_radius_mean_std{"_relative" if APPLY_RADIAL_NORMALIZATION else "_absolute"}.png'   # Output file name
 
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
 
 
def extract_radial_profile(df, time_column, minute, attribute, apply_radial_normalization):
    """Extract the radial profile of `attribute` at the given `minute` from a
    single dataframe. Returns (radii, values), sorted by radius."""
    matching_rows = df[df[time_column] == minute]
    if matching_rows.empty:
        raise ValueError(f"No row found with {time_column} == {minute}")
    row = matching_rows.iloc[0]
 
    pattern = re.compile(rf"^{re.escape(attribute)}_(\d+)_to_(\d+)$")
    points = []
    for col in df.columns:
        m = pattern.match(col)
        if m and pd.notna(row[col]):
            x_start, x_end = int(m.group(1)), int(m.group(2))
            radius = (x_start + x_end) / 2
            points.append((radius, x_start, x_end, row[col]))
 
    if not points:
        raise ValueError(f"No columns found matching attribute '{attribute}'")
 
    points.sort(key=lambda p: p[0])
    radii = np.array([p[0] for p in points], dtype=float)
    raw_values = np.array([p[3] for p in points], dtype=float)
 
    if apply_radial_normalization:
        r_in = np.array([p[1] for p in points], dtype=float)
        r_out = np.array([p[2] for p in points], dtype=float)
        ring_area = np.pi * (r_out ** 2 - r_in ** 2)
        raw_values = raw_values / ring_area
 
    return radii, raw_values
 
 
def compute_mean_std_over_radius(dataframes, time_column, minute, attribute,
                                  apply_radial_normalization, dividing_factor):
    """Compute the radial profile for every dataframe (seed), interpolate them
    onto a common radius axis, and return the mean and standard deviation."""
    if not dataframes:
        return None, None, None
 
    # The radius axis of the first execution is used as reference
    reference_radii, _ = extract_radial_profile(
        dataframes[0], time_column, minute, attribute, apply_radial_normalization
    )
 
    all_values = []
    for df in dataframes:
        radii, values = extract_radial_profile(
            df, time_column, minute, attribute, apply_radial_normalization
        )
        interpolated = np.interp(reference_radii, radii, values)
        all_values.append(interpolated)
 
    all_values = np.array(all_values) / dividing_factor
    mean_values = np.mean(all_values, axis=0)
    std_values = np.std(all_values, axis=0)
 
    return reference_radii, mean_values, std_values
 
 
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    dataframes = load_executions(BASE_DIR, FOLDER_PATTERN, CSV_NAME)
    radii, mean_values, std_values = compute_mean_std_over_radius(
        dataframes, TIME_COLUMN, MINUTE, ATTRIBUTE,
        APPLY_RADIAL_NORMALIZATION, DIVIDING_FACTOR
    )
 
    if radii is None:
        print("No data found to plot.")
        return
 
    print(f"Attribute: {ATTRIBUTE}")
    print(f"Minute: {MINUTE}")
    print(f"Radius range with data: {radii[0]} to {radii[-1]}")
    print(f"Number of radius points: {len(radii)}")
    print(f"Radial normalization applied: {APPLY_RADIAL_NORMALIZATION}")
 
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(radii, mean_values, marker='o', color='blue', linewidth=2,
            label=f'{ATTRIBUTE} (Mean)')
    ax.fill_between(radii,
                     mean_values - std_values,
                     mean_values + std_values,
                     color='blue', alpha=0.2, label='Mean ± Std')
 
    ax.set_xlabel('Radius (um)')
    ylabel = ATTRIBUTE + (' (per um^2)' if APPLY_RADIAL_NORMALIZATION else '')
    ax.set_ylabel(ylabel)
    ax.set_title(f'{ATTRIBUTE} vs radius - minute {MINUTE}')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
 
    if Y_MIN is not None or Y_MAX is not None:
        ax.set_ylim(bottom=Y_MIN, top=Y_MAX)
 
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_NAME)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.show()
 
    print(f"Figure saved to: {output_path}")
 
 
if __name__ == '__main__':
    main()