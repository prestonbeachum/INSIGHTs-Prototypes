# INSIGHTs SIM-U - Multi-Criteria Instance Generator

This directory contains a script to create separate instances of the SIM-U application for different criteria sets.

## Quick Start

### Create a New Instance

```bash
cd /path/to/INSIGHTs-Prototypes
python3 scripts/create_criteria_instance.py --name "Clinical_Reasoning" --port 8503
```

This will:
1. ✅ Create a new directory: `instances/clinical_reasoning/`
2. ✅ Copy all application files from professional_integrity template
3. ✅ Use the shared virtual environment
4. ✅ Generate a `run.sh` launch script
5. ✅ Update page titles and add placeholder criteria

### What You Need to Customize

After creating the new instance, edit these files:

#### 1. **`simu_prototype.py`** - Update the GROUPS dictionary

Replace the placeholder criteria with your actual criteria and elements:

```python
GROUPS = {
    "CR_01_Data_Collection": [
        "history_taking",
        "physical_exam",
        "diagnostic_tests",
        "information_synthesis",
    ],
    "CR_02_Clinical_Reasoning": [
        "hypothesis_generation",
        "differential_diagnosis",
        "clinical_decision_making",
        "evidence_integration",
    ],
    # ... add more criteria
}
```

**Important:** 
- Keys are criterion names (will appear in charts)
- Values are lists of element names (column names in data)
- Total elements should match your rubric structure

#### 2. **`streamlit_app.py`** - Update the schema description

Find this line (around line 281):
```python
st.info("**Schema**: 12 element-level columns from 3 Clinical_Reasoning criteria (update this message)")
```

Update it to describe your actual criteria structure.

## Running Multiple Instances

Each instance runs on a different port:

```bash
# Instance 1: Professional Integrity (port 8501)
cd INSIGHTs_SIMU_Proto
source .venv/bin/activate
streamlit run streamlit_app.py --server.port 8501

# Instance 2: Clinical Reasoning (port 8502)
cd ../Clinical_Reasoning
./run.sh  # or: source .venv/bin/activate && streamlit run streamlit_app.py --server.port 8502

# Instance 3: Communication (port 8503)
cd ../Communication
./run.sh
```

## Directory Structure

```
/Users/prestonbeachum/
├── INSIGHTs_SIMU_Proto/           # Original (Professional Integrity)
│   ├── streamlit_app.py
│   ├── simu_prototype.py
│   ├── create_criteria_instance.py
│   ├── .venv/
│   └── requirements.txt
│
├── Clinical_Reasoning/             # New instance (port 8502)
│   ├── streamlit_app.py
│   ├── simu_prototype.py
│   ├── run.sh
│   ├── .venv/
│   └── requirements.txt
│
└── Communication/                  # Another instance (port 8503)
    ├── streamlit_app.py
    ├── simu_prototype.py
    ├── run.sh
    ├── .venv/
    └── requirements.txt
```

## Command Reference

### Create Instance
```bash
python3 create_criteria_instance.py --name "YourCriteriaName" --port 8502
```

### Launch Instance
```bash
cd ../YourCriteriaName
./run.sh
```

### Stop Instance
```bash
# Press Ctrl+C in the terminal, or:
pkill -f "streamlit run.*port 8502"
```

### Update Requirements
```bash
cd ../YourCriteriaName
source .venv/bin/activate
pip install -r requirements.txt
```

## Tips

- **Port numbers:** Use 8501, 8502, 8503, etc. for different instances
- **Browser access:** Each instance has its own URL (http://localhost:PORT)
- **Data isolation:** Each instance has its own mock data generated from its GROUPS
- **Independent updates:** Update each instance separately
- **Shared bugs:** Bug fixes need to be applied to each instance manually

## Troubleshooting

### Port already in use
```bash
lsof -ti:8502 | xargs kill -9
```

### Virtual environment issues
```bash
cd YourCriteriaName
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Data not updating
- Change `schema_version` in `streamlit_app.py` (around line 257)
- Restart Streamlit

## Example: Creating a Clinical Reasoning Instance

```bash
# 1. Create the instance
python3 create_criteria_instance.py --name "Clinical_Reasoning" --port 8502

# 2. Navigate to it
cd ../Clinical_Reasoning

# 3. Edit the criteria
code simu_prototype.py  # or use your preferred editor

# 4. Update GROUPS dictionary with your criteria
# (see simu_prototype.py for the placeholder structure)

# 5. Launch it
./run.sh

# 6. Open in browser
open http://localhost:8502
```

---

**Created:** October 30, 2025  
**For questions:** Check the INSIGHTs_SimU_prototype_README.txt in each instance
