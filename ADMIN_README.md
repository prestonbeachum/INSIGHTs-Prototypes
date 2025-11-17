# INSIGHTs Admin Dashboard

Central administration interface for managing multiple INSIGHTs assessment instances.

## Overview

The Admin Dashboard provides a unified control panel for:
- Managing multiple assessment instances (PI, PROaCTIVE, etc.)
- Starting/stopping instances
- Configuring system settings
- Monitoring instance health and status
- Creating new instances
- (Future) User management and analytics

## Quick Start

### Starting the Admin Dashboard

```bash
# Option 1: Use the launch script
./run_admin.sh

# Option 2: Manual command
source .venv/bin/activate
streamlit run admin_app.py --server.port 8500
```

The admin dashboard will be available at: **http://localhost:8500**

## Port Allocation

- **8500**: Admin Dashboard (this application)
- **8501**: Professional Integrity (PI) instance
- **8502**: PROaCTIVE instance
- **8503+**: Additional instances as created

## Features

### 1. Dashboard (Home)
- **System Overview**: Quick stats on total, running, and stopped instances
- **Instance Status Cards**: Visual cards showing status of each instance
  - 🟢 Green = Running and healthy
  - 🔴 Red = Stopped
  - ⚠️ Yellow = Running but health check failed
- **Quick Actions**:
  - Start/Stop individual instances
  - Open instance in browser
  - Refresh status

### 2. Instance Management
- **Active Instances Tab**: Configure existing instances
  - Edit name, port, description
  - Enable/disable instances
  - Remove instances
- **Create New Instance Tab**: Set up new assessment instances
  - Specify name, port, criteria count
  - Generates command to run duplication script
- **Import/Export Tab**: Backup and restore configuration
  - Export configuration to JSON
  - Import configuration from file

### 3. User Management (Coming Soon)
Planned features:
- Create and manage user accounts
- Assign users to specific instances
- Role-based access control (Student, Faculty, Admin)
- Activity tracking and audit logs

### 4. Configuration
- **System Settings**:
  - Base path configuration
  - Python environment settings
  - Auto-start on boot option
  - Log level configuration
- **Default Rubrics**:
  - Configure default rubric scales
  - Set thresholds for all instances
- **Backup & Restore**:
  - Full system backups
  - Restore from backup files

### 5. Analytics (Coming Soon)
Planned features:
- Cross-instance comparative analytics
- Aggregate performance metrics
- Usage trends and adoption rates
- Student performance correlation
- Custom report builder

### 6. System Logs (Coming Soon)
- Application logs with filtering
- Access logs and audit trail
- Error tracking and debugging

## Configuration File

The admin dashboard uses `admin_config.json` to store:
- Instance definitions (name, port, path, description)
- User accounts (future)
- System settings

### Configuration Structure

```json
{
  "instances": [
    {
      "name": "Professional Integrity",
      "short_name": "PI",
      "path": ".",
      "port": 8501,
      "description": "Professional Integrity Assessment",
      "criteria_count": 4,
      "enabled": true
    }
  ],
  "users": [],
  "settings": {
    "base_path": "/path/to/INSIGHTs_SIMU_Proto",
    "python_env": ".venv/bin/activate",
    "auto_start": false,
    "log_level": "INFO"
  }
}
```

## Creating New Instances

1. **Via Admin Dashboard**:
   - Go to "Instance Management" → "Create New Instance"
   - Fill in the instance details
   - Click "Create Instance"
   - Run the displayed duplication command

2. **Manual Process**:
   ```bash
   # Create the instance files
   python3 create_criteria_instance.py --name "Clinical Reasoning" --port 8503
   
   # Add to admin config
   # Edit admin_config.json and add the new instance
   ```

## Starting/Stopping Instances

### Via Admin Dashboard
1. Navigate to the Dashboard
2. Find the instance card
3. Click "▶️ Start" or "⏹️ Stop"

### Manual Commands
```bash
# Start an instance
cd /path/to/instance
source ../.venv/bin/activate
streamlit run streamlit_app.py --server.port 8501 &

# Stop an instance
lsof -ti:8501 | xargs kill
```

## Admin Rights & Permissions

The admin dashboard has the following capabilities:

### ✅ Currently Implemented
- Start/stop all instances
- View instance status and health
- Modify instance configuration
- Create new instance templates
- Export/import configuration
- Manage system settings

### 🚧 Planned Features
- User authentication and authorization
- Role-based access control
- Audit logging
- Data backup and restore
- Cross-instance analytics
- Email notifications
- Scheduled tasks (auto-start, backups)

## Security Considerations

### Current State
- No authentication required (intended for local development)
- Admin has full system access
- All instances run under same user context

### Recommended for Production
- Implement authentication (OAuth, LDAP, etc.)
- Add HTTPS/SSL encryption
- Separate user permissions per instance
- Implement audit logging
- Run instances in isolated containers
- Regular backup schedules

## Troubleshooting

### Admin Dashboard Won't Start
```bash
# Check if port 8500 is already in use
lsof -ti:8500

# Kill existing process
lsof -ti:8500 | xargs kill

# Restart
./run_admin.sh
```

### Can't Start/Stop Instances
- Verify the instance path in configuration
- Check virtual environment activation
- Ensure ports are not already in use
- Check file permissions

### Instance Shows as Running but Health Check Fails
- The instance process is running but not responding to HTTP
- Try stopping and restarting the instance
- Check the instance logs for errors

## Directory Structure

```
INSIGHTs_SIMU_Proto/
├── admin_app.py              # Admin dashboard application
├── admin_config.json         # Configuration file
├── run_admin.sh             # Launch script
├── ADMIN_README.md          # This file
├── streamlit_app.py         # PI instance
├── simu_prototype.py        # PI data generation
├── PROaCTIVE/               # PROaCTIVE instance
│   ├── streamlit_app.py
│   └── simu_prototype.py
└── .venv/                   # Shared virtual environment
```

## Development Roadmap

### Phase 1 (Current)
- ✅ Basic instance management
- ✅ Start/stop functionality
- ✅ Status monitoring
- ✅ Configuration management

### Phase 2 (Next)
- 🔲 User authentication
- 🔲 Role-based access control
- 🔲 Database integration
- 🔲 Session management

### Phase 3 (Future)
- 🔲 Cross-instance analytics
- 🔲 Automated backups
- 🔲 Email notifications
- 🔲 Advanced monitoring

### Phase 4 (Advanced)
- 🔲 API endpoints
- 🔲 Mobile-responsive design
- 🔲 Multi-tenant support
- 🔲 Cloud deployment options

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review instance-specific README files
3. Check application logs
4. Verify configuration file syntax

## License

Part of the INSIGHTs assessment platform.
