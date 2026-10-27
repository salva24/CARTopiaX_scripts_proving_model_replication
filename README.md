# CARTopiaX vs CART-ABM: Model Comparison

This repository contains the scripts used to validate and compare simulation results between [CARTopiaX](https://github.com/compiler-research/CARTopiaX.git) and its foundational model, [CART-ABM](https://github.com/salva24/CART-ABM_for_comparison_with_CARTopiaX).  
These tools ensure the **scientific validity** and **reproducibility** of the performance evaluation and figures associated with the **CARTopiaX** project, developed during **Google Summer of Code 2025** with the **CERN HEP Software Foundation (HSF)**.  
This allows users to independently verify that the reported improvements are objectively supported by the data.

> **Update, GSoC 2026:** the folder [`new_model_paper_replication2026/`](new_model_paper_replication2026/) contains the scripts for the follow-up work of **Google Summer of Code 2026**, in which CARTopiaX is extended to replicate the wet lab experiments of [Ando et al., *Evaluating CAR-T Cell Therapy in a Hypoxic 3D Tumor Model*, Advanced Healthcare Materials (2019)](https://doi.org/10.1002/adhm.201900001):
>
> - `dataset_values_preprocessing.py`: fits a spline to the data digitized from the paper, resamples it into radial sections and then normalizes it by the area of each ring (density per um²) so it is comparable with the simulation output.
> - `run_several_simulations.py`: runs CARTopiaX with several seeds and stores each execution in `out/execution_seed_<seed>/` (set `NUMBER_EXECUTIONS`, `EXPORT_VISUALIZATION` and `BIODYNAMO_ENV_SCRIPT` at the top; it restores `params.json` and `bdm.toml` afterwards).
> - `plots_new_model_final_data.py`: mean (and std) over seeds of a final-data field over time.
> - `plots_new_model_dependent_on_radius.py`: mean and std over seeds of a field as a function of radius, in absolute counts or normalized by ring area.
> - `plot_cell_deaths.py`: tumor cell deaths by cause vs radius (absolute, per um² and percentage).
> - `glucose_vs_deaths.py`: average glucose against dead cells over time, with and without treatment.
> - `cartopiax_vs_paper_gsoc2026.py`: compares the simulated dead tumor cells against the paper (raw points and area-normalized spline) at 24h, 48h and 72h.
> - `replication_plots_and_data.zip`: data (`data_paper` and the four simulated scenarios) and plots of this work. Extract it into `new_model_paper_replication2026/`.
>
> The rest of this README describes the original GSoC 2025 comparison with CART-ABM.

## Overview

The comparison evaluates both **accuracy** (results alignment) and **performance** (execution time) between the two CAR T-cell therapy simulation models.

## Replication Data

The repository includes `./replication_plots_and_data.zip`, which contains the original experimental data, results, and plots used in our comparison. This allows you to:
- Verify our findings without re-running lengthy simulations
- Use as a reference for expected output format
- Compare with your own experimental results

## Results Comparison

### 1. Generate Simulation Data

Run both models multiple times with different random seeds following their respective README instructions. Save the CSV summary files for each execution.

### 2. Organize Output Files

**CARTopiaX results:**
- Place files in `./data/data_results_CARTopiaX/`
- Name files sequentially: `final_data1.csv`, `final_data2.csv`, ..., `final_dataN.csv`

**CART-ABM results (Nature paper model):**
- Place files in `./data/data_results_CART-ABM/`
- Name files sequentially: `datos_finales1.csv`, `datos_finales2.csv`, ..., `datos_finalesM.csv`

### 3. Run Comparison Script

Edit `./results_comparison.py` to set:
- `num_csv_files_CARTopiaX = N` (number of CARTopiaX runs)
- `num_csv_files_paper = M` (number of CART-ABM runs)
- `days` parameter (default for a 30-days evolution, adjust if your simulations use a different duration)

Execute the script:
```bash
python results_comparison.py
```

Comparison plots will be generated in `./out/`.

## Performance Comparison

### 1. Measure Execution Times

Use the `time` command to measure execution duration for each model run:
```bash
time <model_execution_command>
```

Run each model multiple times with different seeds under identical conditions and hardware.

### 2. Record Timing Data

Create `./data/execution_times.csv` with the following format:
```csv
0doses_CARTopiaX,1dose_CARTopiaX,2doses_CARTopiaX,0doses_Nature,1dose_Nature,2doses_Nature
"517m13,098s","274m13,034s","251m3,333s","1129m16,431s","724m57,608s","650m42,150s"
```

### 3. Generate Performance Plots

Run the performance comparison script:
```bash
python execution_times.py
```

Performance comparison plots will be generated showing execution time differences between models.

## Repository Structure
```
.
├── data/
│   ├── data_results_CARTopiaX/     # CARTopiaX output CSVs
│   ├── data_results_CART-ABM/      # CART-ABM output CSVs
│   └── execution_times.csv         # Performance timing data
├── out/                             # Generated comparison plots
├── new_model_paper_replication2026/ # GSoC 2026: replication of Ando et al. (2019)
├── replication_plots_and_data.zip   # Experimental data and plots
├── results_comparison.py            # Results comparison script
└── execution_times.py               # Performance comparison script
```

## Requirements

**Python ≥ 3.9.1** with the following packages:

- pandas ≥ 2.3.2  
- matplotlib ≥ 3.9.4  
- numpy ≥ 2.0.2

Install dependencies:
```bash
pip install "pandas>=2.3.2" "matplotlib>=3.9.4" "numpy>=2.0.2"
```

## Model links

- [CARTopiaX](https://github.com/compiler-research/CARTopiaX.git): Public model under the Princeton University Compiler Research Group.
- [CART-ABM](https://github.com/salva24/CART-ABM_for_comparison_with_CARTopiaX): This fork contains the original model, with a minimal modification in `main.cpp` to export the execution summary to a CSV file in the required format for comparison. No behavioral changes have been introduced — there is **no falsification of results** nor any modification that could affect performance or slow down the original model.

## License

Licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.


## Author Contact Information
Author: Salvador de la Torre Gonzalez
You can check my profile at Princeton University's [Compiler Research Team](https://compiler-research.org/team/SalvadordelaTorreGonzalez). Do not hesitate to reach out in case of having questions, email: delatorregonzalezsalvador at gmail.com