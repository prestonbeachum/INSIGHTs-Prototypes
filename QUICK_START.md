# INSIGHTs-Prototypes - Quick Start Guide

## 📂 New Organized Structure

The project has been reorganized for better maintainability:

```
INSIGHTs-Prototypes/
├── 📁 admin/              - Admin dashboard application
├── 📁 instances/          - All assessment instances
│   ├── professional_integrity/
│   └── proactive/
├── 📁 data/               - CSV data files
├── 📁 outputs/            - Generated visualizations (PNG)
├── 📁 docs/               - All documentation
│   ├── admin/
│   ├── guides/
│   ├── pdfs/
│   └── notes/
├── 📁 scripts/            - Utility scripts
└── 📄 README.md           - Main documentation
```

## 🚀 Getting Started

### 1️⃣ Start the Admin Dashboard (Recommended)

```bash
./admin/run_admin.sh
```

Then open: **http://localhost:8500**

From the admin dashboard, you can:
- ✅ Start/stop all instances with one click
- ✅ Monitor instance health
- ✅ Create new instances

### 2️⃣ Start Individual Instances

**Professional Integrity (Port 8501):**
```bash
cd instances/professional_integrity
./run.sh
```

**PROaCTIVE (Port 8502):**
```bash
cd instances/proactive
./run.sh
```

### 3️⃣ Create a New Instance

```bash
python3 scripts/create_criteria_instance.py --name "Clinical_Reasoning" --port 8503
```

## 🔧 What Changed?

### Before (Messy):
```
INSIGHTs-Prototypes/
├── admin_app.py
├── streamlit_app.py
├── simu_prototype.py
├── *.png (scattered)
├── *.csv (scattered)
├── *.md (scattered)
└── PROaCTIVE/
```

### After (Organized):
```
INSIGHTs-Prototypes/
├── admin/              (all admin files)
├── instances/          (all instances)
├── data/              (all data files)
├── outputs/           (all outputs)
├── docs/              (all documentation)
└── scripts/           (utility scripts)
```

## ✅ All Functionality Preserved

- ✅ Admin dashboard works with updated paths
- ✅ All instances work with updated shell scripts
- ✅ Instance creation script updated for new structure
- ✅ All documentation updated
- ✅ Shared virtual environment still at root level

## 📚 Documentation

- **Main README**: [README.md](README.md)
- **Admin Guide**: [docs/admin/ADMIN_README.md](docs/admin/ADMIN_README.md)
- **Instance Creation**: [docs/guides/MULTI_INSTANCE_README.md](docs/guides/MULTI_INSTANCE_README.md)
- **Restructure Details**: [RESTRUCTURE_SUMMARY.md](RESTRUCTURE_SUMMARY.md)

## 🧪 Testing Your Setup

Run these commands to verify everything works:

```bash
# 1. Check admin dashboard starts
./admin/run_admin.sh

# 2. In another terminal, test PI instance
cd instances/professional_integrity && ./run.sh

# 3. In another terminal, test PROaCTIVE instance
cd instances/proactive && ./run.sh

# 4. Test instance creation
python3 scripts/create_criteria_instance.py --name "Test_Instance" --port 8503
```

## 💡 Key Points

1. **All shell scripts are executable** - Just run `./run.sh`
2. **Shared virtual environment** - Located at root `.venv/`
3. **Admin dashboard is your friend** - Use it to manage all instances
4. **Clear organization** - Everything has its place

## 🆘 Need Help?

- Check [README.md](README.md) for detailed information
- Review [RESTRUCTURE_SUMMARY.md](RESTRUCTURE_SUMMARY.md) for all changes
- See [docs/admin/ADMIN_README.md](docs/admin/ADMIN_README.md) for admin features

---

**Last Updated**: November 24, 2025  
**Status**: ✅ Restructure Complete

