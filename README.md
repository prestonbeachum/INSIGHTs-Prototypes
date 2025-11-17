# INSIGHTs Assessment Platform

Multi-instance assessment and analytics platform for educational institutions.

## 🎯 Overview

INSIGHTs is a comprehensive assessment platform that supports multiple criteria-based evaluation systems. The platform uses a parent-child architecture:

- **Admin Dashboard** (Port 8500): Central control panel for managing all instances
- **Instance Applications**: Individual assessment tools for specific criteria sets
  - Professional Integrity (Port 8501)
  - PROaCTIVE - Socratic Dialogue (Port 8502)
  - Additional instances as needed

## 🚀 Quick Start

### 1. Start the Admin Dashboard
```bash
./run_admin.sh
# Or manually:
source .venv/bin/activate
streamlit run admin_app.py --server.port 8500
```
Access at: http://localhost:8500

### 2. Start Individual Instances via Admin
- Open the Admin Dashboard
- Navigate to the Dashboard
- Click "▶️ Start" on any instance card

### 3. Or Start Instances Manually
```bash
# Professional Integrity
source .venv/bin/activate
streamlit run streamlit_app.py --server.port 8501

# PROaCTIVE
cd PROaCTIVE
source ../.venv/bin/activate
streamlit run streamlit_app.py --server.port 8502
```

## 📊 Applications

### Admin Dashboard (Port 8500)
**Purpose**: Central management and control

**Features**:
- Start/stop all instances
- Monitor instance health and status
- Create new assessment instances
- Configure system settings
- User management (future)
- Cross-instance analytics (future)

**Access**: http://localhost:8500

---

### Professional Integrity (Port 8501)
**Purpose**: Professional behavior and integrity assessment

**Criteria** (4 groups, 16 elements):
- PI_01: Foster Integrity
- PI_02: Safe Learning Environment
- PI_03: Foster Inclusive Environment
- PI_04: Maintain Confidentiality

**Views**:
- Student Dashboard: Individual performance tracking
- Faculty Analytics: Cohort comparison, network analysis

**Access**: http://localhost:8501

---

### PROaCTIVE (Port 8502)
**Purpose**: Socratic Dialogue assessment (Promoting Reflective and Observable Capacity Through Interactive Verbal Exchange)

**Criteria** (4 groups, 16 elements):
- PRO_01: Question Formulation
- PRO_02: Response Quality
- PRO_03: Critical Thinking
- PRO_04: Assumption Recognition

**Views**:
- Student Dashboard: Performance tracking (no assessment mode filter)
- Faculty Analytics: Cohort comparison, network analysis

**Access**: http://localhost:8502

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Admin Dashboard (Port 8500)         │
│   ⚙️ Central Management & Control       │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│ PI (8501)      │  │ PROaCTIVE (8502)│
│ Professional   │  │ Socratic        │
│ Integrity      │  │ Dialogue        │
└────────────────┘  └─────────────────┘
```

## 📁 Directory Structure

```
INSIGHTs_SIMU_Proto/
├── admin_app.py                    # Admin dashboard
├── admin_config.json               # Admin configuration
├── run_admin.sh                    # Admin launch script
├── ADMIN_README.md                 # Admin documentation
├── README.md                       # This file
│
├── streamlit_app.py                # PI application
├── simu_prototype.py               # PI data generation
├── run.sh                          # PI launch script
│
├── PROaCTIVE/                      # PROaCTIVE instance
│   ├── streamlit_app.py
│   ├── simu_prototype.py
│   └── run.sh
│
├── create_criteria_instance.py     # Instance duplication script
├── MULTI_INSTANCE_README.md        # Multi-instance guide
│
└── .venv/                          # Shared virtual environment
    └── (Python packages)
```

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- Virtual environment support
- macOS, Linux, or Windows

### Setup
```bash
# Clone or navigate to the project
cd INSIGHTs_SIMU_Proto

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install streamlit pandas plotly networkx matplotlib scipy psutil requests

# Make scripts executable
chmod +x run_admin.sh run.sh PROaCTIVE/run.sh
```

## 📖 Usage Guides

### For Administrators
See **[ADMIN_README.md](ADMIN_README.md)** for:
- Admin dashboard features
- Instance management
- User management (future)
- System configuration
- Troubleshooting

### For Creating New Instances
See **[MULTI_INSTANCE_README.md](MULTI_INSTANCE_README.md)** for:
- Using the duplication script
- Customizing criteria
- Setting up new assessments

### For Faculty/Users
Each instance has its own interface:
- Student Dashboard: Individual performance tracking
- Faculty Analytics: Comparative analysis and insights

## 🎨 Features by View

### Admin Dashboard Features
- ✅ Instance status monitoring (running/stopped)
- ✅ Start/stop instances with one click
- ✅ Health checks for each instance
- ✅ Create new instances
- ✅ Configuration management
- ✅ Import/export settings
- 🚧 User management
- 🚧 Cross-instance analytics
- 🚧 Audit logs

### Student Dashboard Features
- Performance tracking across attempts
- Rubric element scoring (0-4 scale)
- Trend analysis over time
- Scenario-based filtering
- Mock data generation for testing

### Faculty Analytics Features
- Cohort comparison (A vs B)
- Multiple rubric support (Simulation vs Socratic)
- Network centrality analysis
- Correlation networks
- Time window filtering
- Focus metric filtering
- Statistical summaries

## 🔧 Creating New Assessment Instances

### Option 1: Via Admin Dashboard
1. Open Admin Dashboard (http://localhost:8500)
2. Go to "Instance Management" → "Create New Instance"
3. Fill in details and click "Create Instance"
4. Run the generated command

### Option 2: Via Command Line
```bash
python3 create_criteria_instance.py --name "Clinical Reasoning" --port 8503
```

This will:
- Copy template files
- Create instance directory
- Update configuration
- Generate launch script

## 🔌 Port Management

Default port assignments:
- **8500**: Admin Dashboard ⚙️
- **8501**: Professional Integrity 👔
- **8502**: PROaCTIVE 💭
- **8503+**: Additional instances

To check if a port is in use:
```bash
lsof -ti:8500  # Replace 8500 with your port
```

To stop a process on a port:
```bash
lsof -ti:8500 | xargs kill
```

## 📊 Data Structure

All instances use the same data structure:
- **Student ID**: Unique identifier
- **Attempt**: 1-5 (multiple attempts per student)
- **Scenario**: 3 scenario options
- **Mode**: Socratic or Verbal (for applicable instances)
- **Element Scores**: 16 elements rated 0-4
  - 0 = Not observed
  - 1 = Unsatisfactory
  - 2 = Developing
  - 3 = Proficient
  - 4 = Exemplary

## 🔐 Security Notes

**Current Setup** (Development):
- No authentication required
- All instances run under same user
- Suitable for local development only

**Production Recommendations**:
- Implement authentication (OAuth, SSO)
- Add HTTPS/SSL
- Use role-based access control
- Enable audit logging
- Run in containerized environment
- Regular backups

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process
lsof -ti:8500 | xargs kill

# Or use admin dashboard to stop
```

### Instance Won't Start
1. Check virtual environment is activated
2. Verify port is available
3. Check file permissions
4. Review error logs

### Admin Dashboard Permission Errors
- The dashboard uses `lsof` instead of `psutil` to avoid permission issues
- Ensure you have permission to run `lsof` and `kill` commands

### Changes Not Appearing
- Stop and restart the affected instance
- Clear browser cache
- Check if correct port is being accessed

## 📝 Development Workflow

1. **Start Admin Dashboard** for central control
2. **Use Admin Dashboard** to start/stop instances
3. **Make changes** to individual instance files
4. **Restart instances** via Admin Dashboard
5. **Test changes** in browser
6. **Save configuration** via Admin Dashboard

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- Multi-instance architecture
- Basic instance management
- Admin dashboard
- Start/stop functionality

### Phase 2: Enhancement 🚧
- User authentication
- Role-based permissions
- Database integration
- Enhanced monitoring

### Phase 3: Analytics 📋
- Cross-instance analytics
- Performance dashboards
- Comparative reporting
- Export functionality

### Phase 4: Production 🎯
- Cloud deployment
- API endpoints
- Mobile optimization
- Advanced security

## 📚 Documentation

- **[ADMIN_README.md](ADMIN_README.md)**: Admin dashboard guide
- **[MULTI_INSTANCE_README.md](MULTI_INSTANCE_README.md)**: Multi-instance setup
- **Individual READMEs**: Each instance folder contains specific documentation

## 🤝 Contributing

To add new features:
1. Create feature in admin dashboard or instance
2. Update relevant README
3. Test with existing instances
4. Document configuration changes

## 📄 License

Part of the INSIGHTs assessment platform.

## 🆘 Support

For help:
1. Check relevant README file
2. Review troubleshooting section
3. Check instance logs
4. Verify configuration files

---

**Last Updated**: November 2025  
**Platform Version**: 1.0.0  
**Admin Dashboard**: Port 8500
