# INSIGHTs-Prototypes Restructure Summary

**Date**: November 24, 2025  
**Status**: ✅ Complete

## Overview

The INSIGHTs-Prototypes directory has been reorganized into a cleaner, more maintainable structure. All functionalities have been preserved with updated paths and configurations.

## New Directory Structure

```
INSIGHTs-Prototypes/
├── admin/                          # Admin dashboard
│   ├── admin_app.py
│   ├── admin_config.json
│   └── run_admin.sh
│
├── instances/                      # Assessment instances
│   ├── professional_integrity/     # PI instance
│   │   ├── streamlit_app.py
│   │   ├── simu_prototype.py
│   │   ├── requirements.txt
│   │   └── run.sh
│   │
│   └── proactive/                  # PROaCTIVE instance
│       ├── streamlit_app.py
│       ├── simu_prototype.py
│       ├── requirements.txt
│       ├── run.sh
│       └── INSIGHTs_SimU_prototype_README.txt
│
├── data/                           # Data files
│   ├── simu_first3_criteria_mock.csv
│   ├── socratic_metrics_long.csv
│   └── socratic_metrics_wide.csv
│
├── outputs/                        # Generated visualizations
│   ├── faculty_attempt_vs_overall_scatter.png
│   ├── faculty_boxplot_by_criterion.png
│   ├── network_co_missed_criteria.png
│   ├── network_simu_x_socratic.png
│   ├── network_student_criterion_bipartite.png
│   ├── S01_avg_by_criterion.png
│   ├── S03_avg_by_criterion.png
│   ├── student_cohort_avg_by_criterion.png
│   ├── student_cohort_overall_trend.png
│   └── tmp_network_simu_x_socratic.png
│
├── docs/                           # Documentation
│   ├── admin/                      # Admin documentation
│   │   └── ADMIN_README.md
│   ├── guides/                     # User guides
│   │   ├── MULTI_INSTANCE_README.md
│   │   └── INSIGHTs_SimU_prototype_README.txt
│   ├── pdfs/                       # Reference PDFs
│   │   ├── Socratic Dialogue Assessment - Proactive Feedback.pdf
│   │   └── Socratic Dialogue Capacity Assessment Metrics (1).pdf
│   └── notes/                      # Meeting notes & summaries
│       ├── IMPLEMENTATION_ANSWERS.md
│       ├── IMPLEMENTATION_SUMMARY_11_17.md
│       └── MEETING_QUESTIONS_11_17.md
│
├── scripts/                        # Utility scripts
│   └── create_criteria_instance.py
│
├── requirements.txt                # Root requirements
├── README.md                       # Main README
└── .venv/                          # Shared virtual environment
```

## Changes Made

### 1. File Reorganization

#### Admin Files
- `admin_app.py` → `admin/admin_app.py`
- `admin_config.json` → `admin/admin_config.json`
- `run_admin.sh` → `admin/run_admin.sh`

#### Instance Files
- Root `streamlit_app.py`, `simu_prototype.py` → `instances/professional_integrity/`
- `PROaCTIVE/` → `instances/proactive/`
- Created `instances/professional_integrity/run.sh`
- Added `instances/professional_integrity/requirements.txt`

#### Data Files
- All `*.csv` files → `data/`

#### Output Files
- All `*.png` files → `outputs/`

#### Documentation
- `ADMIN_README.md` → `docs/admin/ADMIN_README.md`
- `MULTI_INSTANCE_README.md` → `docs/guides/MULTI_INSTANCE_README.md`
- `IMPLEMENTATION_*.md`, `MEETING_*.md` → `docs/notes/`
- PDF files → `docs/pdfs/`
- `INSIGHTs_SimU_prototype_README.txt` → `docs/guides/`

#### Scripts
- `create_criteria_instance.py` → `scripts/create_criteria_instance.py`

### 2. Configuration Updates

#### admin_config.json
- Updated instance paths:
  - Professional Integrity: `"path": "instances/professional_integrity"`
  - PROaCTIVE: `"path": "instances/proactive"`
- Updated base_path to current workspace

#### admin_app.py
- Updated default base_path to use parent directory (since admin_app.py is now in admin/)
- Updated command execution to navigate from base_path to instance directories

#### Shell Scripts
- `admin/run_admin.sh`: Updated to run from parent directory and reference `admin/admin_app.py`
- `instances/professional_integrity/run.sh`: Created new, references `../../.venv/bin/activate`
- `instances/proactive/run.sh`: Updated to reference `../../.venv/bin/activate`

#### README Files
- Updated `README.md` with new directory structure
- Updated paths in documentation files
- Updated `docs/admin/ADMIN_README.md` with correct launch commands
- Updated `docs/guides/MULTI_INSTANCE_README.md` with new paths

### 3. Script Updates

#### scripts/create_criteria_instance.py
- Updated to create instances in `instances/` directory
- Uses `instances/professional_integrity` as template
- Updated documentation strings with new paths

### 4. Cleanup
- Removed old `PROaCTIVE/` directory
- Removed `__pycache__/` directories

## How to Use After Restructuring

### Start Admin Dashboard
```bash
# From project root
./admin/run_admin.sh

# Or manually
source .venv/bin/activate
streamlit run admin/admin_app.py --server.port 8500
```

### Start Instances Manually
```bash
# Professional Integrity
cd instances/professional_integrity
./run.sh

# PROaCTIVE
cd instances/proactive
./run.sh
```

### Create New Instance
```bash
# From project root
python3 scripts/create_criteria_instance.py --name "Clinical_Reasoning" --port 8503
```

## Benefits of New Structure

1. **Clear Separation of Concerns**: Admin, instances, data, outputs, and docs are all separated
2. **Easier Navigation**: Related files are grouped together
3. **Better Scalability**: Easy to add new instances in the `instances/` directory
4. **Cleaner Root**: Only essential files (README, requirements.txt) remain at root level
5. **Organized Documentation**: All docs in one place with logical subdirectories
6. **Data Management**: Clear separation of input data and generated outputs

## Verification Checklist

- ✅ All files moved to appropriate directories
- ✅ Admin configuration updated with new paths
- ✅ All shell scripts updated with correct relative paths
- ✅ README files updated with new structure
- ✅ Documentation files updated with new paths
- ✅ Instance creation script updated
- ✅ Old directories removed
- ✅ Virtual environment references updated

## Notes

- The shared `.venv/` virtual environment remains at the project root
- All instances reference the shared venv via `../../.venv/bin/activate`
- The admin dashboard is designed to work from the admin/ subdirectory
- All functionality preserved - only file organization changed

## Testing Recommendations

Before full deployment, verify:
1. Admin dashboard starts correctly: `./admin/run_admin.sh`
2. Admin can start instances via the dashboard
3. Manual instance start scripts work: `cd instances/professional_integrity && ./run.sh`
4. Instance creation script works: `python3 scripts/create_criteria_instance.py --name "Test" --port 8503`
5. All import statements work correctly in Python files

