"""INSIGHTs Admin Dashboard

Central management interface for all INSIGHTs instances.
Provides instance management, user administration, and cross-instance analytics.

Run:
    streamlit run admin_app.py --server.port 8500
"""

import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import psutil
import requests
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="INSIGHTs Admin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #e0e0e0;
        margin-bottom: 2rem;
    }
    .instance-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        background: #f8f9fa;
    }
    .instance-running {
        border-color: #1e6f3d;
        background: #1e4d2b;
        color: #ffffff;
    }
    .instance-running h3 {
        color: #ffffff;
    }
    .instance-running p {
        color: #e0e0e0;
    }
    .instance-stopped {
        border-color: #dc3545;
        background: #2d1a1f;
        color: #ffffff;
    }
    .instance-stopped h3 {
        color: #ffffff;
    }
    .instance-stopped p {
        color: #e0e0e0;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        background: #2d4a3e;
        color: white;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    /* Dark green background for main content */
    .main .block-container {
        background: linear-gradient(135deg, #1a3d2e 0%, #0d2818 100%);
        padding: 2rem;
        border-radius: 10px;
    }
    /* Style section headers */
    .main h3 {
        color: #ffffff;
    }
    .main h2 {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "admin_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "instances": [
        {
            "name": "Professional Integrity",
            "short_name": "PI",
            "path": ".",
            "port": 8501,
            "description": "Professional Integrity Assessment",
            "criteria_count": 4,
            "enabled": True
        },
        {
            "name": "PROaCTIVE",
            "short_name": "PRO",
            "path": "PROaCTIVE",
            "port": 8502,
            "description": "Socratic Dialogue Analytics",
            "criteria_count": 4,
            "enabled": True
        }
    ],
    "users": [],
    "settings": {
        "base_path": str(Path(__file__).parent),
        "python_env": ".venv/bin/activate",
        "auto_start": False,
        "log_level": "INFO"
    }
}

# Load or create configuration
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# Check if a port is in use
def is_port_in_use(port):
    """Check if a specific port has a process listening on it."""
    try:
        # Use lsof command instead of psutil to avoid permission issues
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return result.returncode == 0 and result.stdout.strip() != ''
    except:
        return False

# Get process running on port
def get_process_on_port(port):
    """Get the process ID running on a specific port."""
    try:
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().split('\n')[0])
        return None
    except:
        return None

# Check if instance is accessible
def check_instance_health(port):
    """Check if instance is running and accessible."""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return response.status_code == 200
    except:
        return False

# Start instance
def start_instance(instance, base_path):
    """Start a Streamlit instance."""
    path = Path(base_path) / instance['path']
    port = instance['port']
    
    # Check if already running
    if is_port_in_use(port):
        return False, f"Port {port} is already in use"
    
    try:
        # Build command
        cmd = f"cd {path} && source ../.venv/bin/activate && streamlit run streamlit_app.py --server.port {port} > /dev/null 2>&1 &"
        subprocess.Popen(cmd, shell=True, executable='/bin/zsh')
        return True, f"Instance started on port {port}"
    except Exception as e:
        return False, str(e)

# Stop instance
def stop_instance(port):
    """Stop a Streamlit instance running on specified port."""
    pid = get_process_on_port(port)
    if pid:
        try:
            # Use kill command to terminate the process
            subprocess.run(['kill', str(pid)], check=True, timeout=3)
            # Wait a moment for process to stop
            subprocess.run(['sleep', '1'])
            # Verify it stopped
            if not is_port_in_use(port):
                return True, f"Instance on port {port} stopped"
            else:
                return False, f"Process may still be running on port {port}"
        except Exception as e:
            return False, str(e)
    return False, f"No process found on port {port}"

# Load configuration
config = load_config()
base_path = config['settings']['base_path']

# Sidebar
with st.sidebar:
    st.markdown("### Admin Controls")
    st.markdown("---")
    
    admin_section = st.radio(
        "Navigation",
        ["Dashboard", "Instance Management", "User Management", "Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Quick Actions**")
    
    if st.button("Refresh Status", use_container_width=True):
        st.rerun()
    
    if st.button("Save Config", use_container_width=True):
        save_config(config)
        st.success("Configuration saved!")
    
    st.markdown("---")
    st.markdown(f"**Last Updated**  \n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main content
st.markdown('<div class="main-header">INSIGHTs Administration</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Central Management Dashboard</div>', unsafe_allow_html=True)

# Dashboard View
if admin_section == "Dashboard":
    st.markdown("### System Overview")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    running_count = sum(1 for inst in config['instances'] if is_port_in_use(inst['port']))
    total_count = len(config['instances'])
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{total_count}</div>
            <div class="stat-label">Total Instances</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box" style="background: #1e4d2b;">
            <div class="stat-value">{running_count}</div>
            <div class="stat-label">Running</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box" style="background: #4d1e1e;">
            <div class="stat-value">{total_count - running_count}</div>
            <div class="stat-label">Stopped</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box" style="background: #1e3a4d;">
            <div class="stat-value">{len(config.get('users', []))}</div>
            <div class="stat-label">Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Instance Status Cards
    st.markdown("### Instance Status")
    
    for instance in config['instances']:
        port = instance['port']
        is_running = is_port_in_use(port)
        is_healthy = check_instance_health(port) if is_running else False
        
        card_class = "instance-running" if is_running else "instance-stopped"
        status_text = "[RUNNING]" if is_running else "[STOPPED]"
        health_text = "[HEALTHY]" if is_healthy else "[WARNING]" if is_running else "[OFFLINE]"
        
        st.markdown(f"""
        <div class="instance-card {card_class}">
            <h3>{status_text} {instance['name']} ({instance['short_name']})</h3>
            <p><strong>Description:</strong> {instance['description']}</p>
            <p><strong>Port:</strong> {port} | <strong>Criteria:</strong> {instance['criteria_count']} | <strong>Health:</strong> {health_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            if is_running:
                if st.button(f"Stop", key=f"stop_{port}"):
                    success, msg = stop_instance(port)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
            else:
                if st.button(f"Start", key=f"start_{port}"):
                    success, msg = start_instance(instance, base_path)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()
        
        with col2:
            if is_running:
                st.link_button("Open", f"http://localhost:{port}", use_container_width=True)
        
        st.markdown("")

# Instance Management
elif admin_section == "Instance Management":
    st.markdown("### Instance Management")
    
    tab1, tab2, tab3 = st.tabs(["Active Instances", "Create New Instance", "Import/Export"])
    
    with tab1:
        st.markdown("#### Manage Existing Instances")
        
        for idx, instance in enumerate(config['instances']):
            with st.expander(f"{instance['name']} - Port {instance['port']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    instance['name'] = st.text_input("Name", instance['name'], key=f"name_{idx}")
                    instance['short_name'] = st.text_input("Short Name", instance['short_name'], key=f"short_{idx}")
                    instance['port'] = st.number_input("Port", value=instance['port'], key=f"port_{idx}")
                
                with col2:
                    instance['path'] = st.text_input("Path", instance['path'], key=f"path_{idx}")
                    instance['description'] = st.text_input("Description", instance['description'], key=f"desc_{idx}")
                    instance['criteria_count'] = st.number_input("Criteria Count", value=instance['criteria_count'], key=f"crit_{idx}")
                
                instance['enabled'] = st.checkbox("Enabled", instance['enabled'], key=f"enabled_{idx}")
                
                if st.button("Remove Instance", key=f"remove_{idx}"):
                    config['instances'].pop(idx)
                    save_config(config)
                    st.success(f"Removed {instance['name']}")
                    st.rerun()
    
    with tab2:
        st.markdown("#### Create New Instance")
        
        st.info("Use the duplication script to create a new instance with specific criteria.")
        
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Instance Name", placeholder="e.g., Clinical Reasoning")
            new_short = st.text_input("Short Name", placeholder="e.g., CR")
            new_port = st.number_input("Port", value=8503, min_value=8500, max_value=9000)
        
        with col2:
            new_desc = st.text_area("Description", placeholder="Brief description of the instance")
            new_criteria_count = st.number_input("Number of Criteria", value=4, min_value=1, max_value=10)
        
        if st.button("Create Instance", type="primary"):
            if new_name and new_short:
                # Add to config
                new_instance = {
                    "name": new_name,
                    "short_name": new_short,
                    "path": new_short,
                    "port": new_port,
                    "description": new_desc,
                    "criteria_count": new_criteria_count,
                    "enabled": True
                }
                config['instances'].append(new_instance)
                save_config(config)
                
                st.success(f"Instance '{new_name}' created! Now run the duplication script to set up the files.")
                st.code(f"python3 create_criteria_instance.py --name '{new_name}' --port {new_port}")
            else:
                st.error("Please provide at least a name and short name.")
    
    with tab3:
        st.markdown("#### Import/Export Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export Configuration**")
            config_json = json.dumps(config, indent=2)
            st.download_button(
                "Download Config",
                config_json,
                file_name="insights_admin_config.json",
                mime="application/json"
            )
        
        with col2:
            st.markdown("**Import Configuration**")
            uploaded_file = st.file_uploader("Upload Config JSON", type=['json'])
            if uploaded_file:
                try:
                    imported_config = json.load(uploaded_file)
                    if st.button("Import Configuration"):
                        save_config(imported_config)
                        st.success("Configuration imported successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error importing config: {e}")

# User Management
elif admin_section == "User Management":
    st.markdown("### User Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Users", "Add User", "Roles & Permissions", "Activity Log"])
    
    with tab1:
        st.markdown("#### All Users")
        
        # Search and filter
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            search_query = st.text_input("Search users", placeholder="Name, email, or ID")
        with col2:
            filter_role = st.selectbox("Filter by Role", ["All", "Admin", "Faculty", "Student"])
        with col3:
            filter_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        
        # Get or initialize users
        if 'users' not in config or not config['users']:
            config['users'] = []
        
        users = config['users']
        
        # Filter users
        filtered_users = users
        if search_query:
            filtered_users = [u for u in filtered_users if 
                            search_query.lower() in u.get('name', '').lower() or 
                            search_query.lower() in u.get('email', '').lower() or
                            search_query.lower() in u.get('user_id', '').lower()]
        if filter_role != "All":
            filtered_users = [u for u in filtered_users if u.get('role') == filter_role]
        if filter_status != "All":
            filtered_users = [u for u in filtered_users if u.get('status') == filter_status]
        
        st.markdown(f"**Showing {len(filtered_users)} of {len(users)} users**")
        
        if len(filtered_users) > 0:
            # Create user table
            for idx, user in enumerate(filtered_users):
                with st.expander(f"{user.get('name', 'Unknown')} ({user.get('role', 'N/A')}) - {user.get('email', '')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**User ID:** {user.get('user_id', 'N/A')}")
                        st.markdown(f"**Role:** {user.get('role', 'N/A')}")
                        st.markdown(f"**Status:** {user.get('status', 'N/A')}")
                        st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**Created:** {user.get('created_at', 'N/A')}")
                        st.markdown(f"**Last Login:** {user.get('last_login', 'Never')}")
                        
                        # Assigned instances
                        assigned = user.get('assigned_instances', [])
                        if assigned:
                            st.markdown(f"**Assigned Instances:** {', '.join(assigned)}")
                        else:
                            st.markdown("**Assigned Instances:** None")
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Edit", key=f"edit_user_{user.get('user_id')}"):
                            st.session_state[f'editing_user_{user.get("user_id")}'] = True
                    with col2:
                        new_status = "Inactive" if user.get('status') == 'Active' else "Active"
                        if st.button(f"{'Deactivate' if user.get('status') == 'Active' else 'Activate'}", 
                                   key=f"toggle_user_{user.get('user_id')}"):
                            user['status'] = new_status
                            save_config(config)
                            st.success(f"User {new_status.lower()}d")
                            st.rerun()
                    with col3:
                        if st.button("Delete", key=f"delete_user_{user.get('user_id')}"):
                            config['users'] = [u for u in config['users'] if u.get('user_id') != user.get('user_id')]
                            save_config(config)
                            st.success("User deleted")
                            st.rerun()
        else:
            st.info("No users found. Add users in the 'Add User' tab.")
    
    with tab2:
        st.markdown("#### Add New User")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_user_name = st.text_input("Full Name *", placeholder="John Doe")
                new_user_email = st.text_input("Email Address *", placeholder="john.doe@university.edu")
                new_user_role = st.selectbox("Role *", ["Student", "Faculty", "Admin"])
            
            with col2:
                new_user_id = st.text_input("User ID *", placeholder="JD001")
                new_user_password = st.text_input("Password *", type="password", placeholder="Temporary password")
                new_user_status = st.selectbox("Status", ["Active", "Inactive"])
            
            # Instance assignment
            st.markdown("**Assign to Instances**")
            available_instances = [inst['short_name'] for inst in config['instances']]
            new_user_instances = st.multiselect(
                "Select instances",
                available_instances,
                help="User will have access to these instances"
            )
            
            submitted = st.form_submit_button("Add User", type="primary", use_container_width=True)
            
            if submitted:
                if new_user_name and new_user_email and new_user_id:
                    new_user = {
                        'user_id': new_user_id,
                        'name': new_user_name,
                        'email': new_user_email,
                        'role': new_user_role,
                        'status': new_user_status,
                        'assigned_instances': new_user_instances,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'last_login': 'Never',
                        'password_hash': new_user_password  # In production, use proper hashing
                    }
                    config['users'].append(new_user)
                    save_config(config)
                    st.success(f"User '{new_user_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.markdown("#### Roles & Permissions")
        
        # Role statistics
        col1, col2, col3 = st.columns(3)
        admin_count = len([u for u in users if u.get('role') == 'Admin'])
        faculty_count = len([u for u in users if u.get('role') == 'Faculty'])
        student_count = len([u for u in users if u.get('role') == 'Student'])
        
        with col1:
            st.metric("Admins", admin_count)
        with col2:
            st.metric("Faculty", faculty_count)
        with col3:
            st.metric("Students", student_count)
        
        st.markdown("---")
        
        # Permission matrix
        st.markdown("#### Permission Matrix")
        
        permissions_data = {
            'Permission': [
                'View Dashboard',
                'Start/Stop Instances',
                'Create Instances',
                'Manage Users',
                'View All Students',
                'View Own Data',
                'Export Data',
                'Modify Settings'
            ],
            'Admin': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
            'Faculty': ['Yes', 'No', 'No', 'No', 'Yes', 'Yes', 'Yes', 'No'],
            'Student': ['Yes', 'No', 'No', 'No', 'No', 'Yes', 'Yes', 'No']
        }
        
        permissions_df = pd.DataFrame(permissions_data)
        st.dataframe(permissions_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Role descriptions
        st.markdown("#### Role Descriptions")
        
        with st.expander("Admin"):
            st.markdown("""
            **Full System Access**
            - Manage all instances (start, stop, create, delete)
            - Manage all users and permissions
            - Access all data across instances
            - Configure system settings
            - View analytics and reports
            """)
        
        with st.expander("Faculty"):
            st.markdown("""
            **Assessment & Analytics Access**
            - View student performance data
            - Access faculty analytics views
            - Export assessment data
            - View cohort comparisons
            - Cannot modify system settings or users
            """)
        
        with st.expander("Student"):
            st.markdown("""
            **Personal Data Access**
            - View own performance data
            - Track personal progress
            - Export own data
            - Cannot view other students' data
            - Cannot access admin features
            """)
    
    with tab4:
        st.markdown("#### User Activity Log")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", datetime.now().date())
        with col2:
            end_date = st.date_input("To Date", datetime.now().date())
        
        # Activity type filter
        activity_filter = st.multiselect(
            "Activity Type",
            ["Login", "Logout", "Data Export", "Instance Access", "Configuration Change"],
            default=["Login", "Logout"]
        )
        
        # Mock activity data (in production, this would come from a database)
        st.info("Activity logging will be implemented with user authentication. Currently showing sample data.")
        
        sample_activities = pd.DataFrame({
            'Timestamp': [
                '2025-11-02 10:23:15',
                '2025-11-02 09:45:32',
                '2025-11-01 16:20:10',
                '2025-11-01 14:15:45'
            ],
            'User': ['John Doe (JD001)', 'Jane Smith (JS002)', 'Bob Johnson (BJ003)', 'John Doe (JD001)'],
            'Role': ['Faculty', 'Student', 'Admin', 'Faculty'],
            'Activity': ['Login', 'Data Export', 'Instance Started', 'Login'],
            'Instance': ['PI', 'PRO', 'PI', 'PRO'],
            'IP Address': ['192.168.1.100', '192.168.1.105', '192.168.1.1', '192.168.1.100']
        })
        
        st.dataframe(sample_activities, hide_index=True, use_container_width=True)
        
        if st.button("Export Activity Log"):
            csv = sample_activities.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                file_name=f"activity_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Analytics
elif admin_section == "Analytics":
    st.markdown("### Cross-Instance Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Performance Comparison", "Usage Statistics", "Correlation Analysis"])
    
    with tab1:
        st.markdown("#### Analytics Overview")
        
        # Generate mock analytics data
        @st.cache_data
        def generate_analytics_data():
            # Mock data for demonstration
            instances_data = []
            for inst in config['instances']:
                n_students = 12
                n_attempts = 5
                instances_data.append({
                    'instance': inst['short_name'],
                    'total_students': n_students,
                    'avg_score': round(2.5 + (hash(inst['short_name']) % 10) / 10, 2),
                    'completion_rate': round(85 + (hash(inst['short_name']) % 15), 1),
                    'total_assessments': n_students * n_attempts
                })
            return pd.DataFrame(instances_data)
        
        analytics_df = generate_analytics_data()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_students = analytics_df['total_students'].sum()
            st.metric("Total Students", total_students)
        
        with col2:
            total_assessments = analytics_df['total_assessments'].sum()
            st.metric("Total Assessments", total_assessments)
        
        with col3:
            avg_score = analytics_df['avg_score'].mean()
            st.metric("Avg Score (All)", f"{avg_score:.2f}/4.0")
        
        with col4:
            avg_completion = analytics_df['completion_rate'].mean()
            st.metric("Avg Completion", f"{avg_completion:.1f}%")
        
        st.markdown("---")
        
        # Instance comparison table
        st.markdown("#### Instance Summary")
        
        display_df = analytics_df.copy()
        display_df.columns = ['Instance', 'Students', 'Avg Score', 'Completion %', 'Assessments']
        st.dataframe(display_df, hide_index=True, use_container_width=True)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            "Download Summary",
            csv,
            file_name=f"analytics_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.markdown("#### Performance Comparison")
        
        # Select instances to compare
        available_instances = [inst['short_name'] for inst in config['instances']]
        selected_instances = st.multiselect(
            "Select instances to compare",
            available_instances,
            default=available_instances[:2] if len(available_instances) >= 2 else available_instances
        )
        
        if len(selected_instances) > 0:
            # Generate comparison data
            import plotly.graph_objects as go
            import numpy as np
            
            # Mock performance data over attempts
            attempts = list(range(1, 6))
            fig = go.Figure()
            
            for inst_name in selected_instances:
                # Generate mock trend data
                base_score = 2.0 + (hash(inst_name) % 10) / 10
                scores = [base_score + i * 0.15 + np.random.uniform(-0.1, 0.1) for i in range(5)]
                
                fig.add_trace(go.Scatter(
                    x=attempts,
                    y=scores,
                    mode='lines+markers',
                    name=inst_name,
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                title="Performance Trend Across Attempts",
                xaxis_title="Attempt",
                yaxis_title="Average Score (0-4)",
                yaxis=dict(range=[0, 4]),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistical comparison
            st.markdown("#### Statistical Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Score Distribution**")
                comparison_data = []
                for inst_name in selected_instances:
                    base = 2.0 + (hash(inst_name) % 10) / 10
                    comparison_data.append({
                        'Instance': inst_name,
                        'Mean': f"{base + 0.3:.2f}",
                        'Median': f"{base + 0.25:.2f}",
                        'Std Dev': f"{0.4 + (hash(inst_name) % 3) / 10:.2f}"
                    })
                st.dataframe(pd.DataFrame(comparison_data), hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("**Achievement Rates**")
                achievement_data = []
                for inst_name in selected_instances:
                    base = 70 + (hash(inst_name) % 20)
                    achievement_data.append({
                        'Instance': inst_name,
                        'Proficient+': f"{base}%",
                        'Developing': f"{100-base-10}%",
                        'Below': f"{10}%"
                    })
                st.dataframe(pd.DataFrame(achievement_data), hide_index=True, use_container_width=True)
        else:
            st.info("Select at least one instance to view comparison.")
    
    with tab3:
        st.markdown("#### Usage Statistics")
        
        # Time period selection
        time_period = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        
        # Usage metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Active Users**")
            active_users = len([u for u in config.get('users', []) if u.get('status') == 'Active'])
            st.metric("Current", active_users, "+3 from last period")
        
        with col2:
            st.markdown("**Total Logins**")
            st.metric("Count", "247", "+18%")
        
        with col3:
            st.markdown("**Avg Session**")
            st.metric("Duration", "23 min", "+2 min")
        
        st.markdown("---")
        
        # Instance usage chart
        st.markdown("#### Instance Access Frequency")
        
        import plotly.express as px
        
        # Mock usage data
        usage_data = []
        for inst in config['instances']:
            for day in range(7):
                usage_data.append({
                    'Date': f"Day {day+1}",
                    'Instance': inst['short_name'],
                    'Access Count': 15 + (hash(f"{inst['short_name']}{day}") % 25)
                })
        
        usage_df = pd.DataFrame(usage_data)
        
        fig = px.bar(
            usage_df,
            x='Date',
            y='Access Count',
            color='Instance',
            barmode='group',
            title="Daily Access by Instance"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Peak usage times
        st.markdown("#### Peak Usage Times")
        
        col1, col2 = st.columns(2)
        
        with col1:
            peak_data = pd.DataFrame({
                'Time': ['8-10 AM', '10-12 PM', '12-2 PM', '2-4 PM', '4-6 PM'],
                'Access Count': [45, 78, 92, 65, 43]
            })
            st.dataframe(peak_data, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("**Busiest Day:** Monday (134 accesses)")
            st.markdown("**Peak Hour:** 12-2 PM (92 accesses)")
            st.markdown("**Most Used Instance:** " + (config['instances'][0]['short_name'] if config['instances'] else "N/A"))
    
    with tab4:
        st.markdown("#### Correlation Analysis")
        
        st.info("This analysis examines relationships between performance across different assessment instances.")
        
        # Instance selection for correlation
        col1, col2 = st.columns(2)
        
        instances_list = [inst['short_name'] for inst in config['instances']]
        
        with col1:
            inst_a = st.selectbox("Instance A", instances_list, key="corr_inst_a")
        with col2:
            inst_b = st.selectbox("Instance B", instances_list[1:] if len(instances_list) > 1 else instances_list, key="corr_inst_b")
        
        if inst_a and inst_b and inst_a != inst_b:
            # Generate mock correlation data
            np.random.seed(42)
            n_students = 30
            
            # Create correlated data
            base_performance = np.random.normal(2.5, 0.6, n_students)
            inst_a_scores = base_performance + np.random.normal(0, 0.3, n_students)
            inst_b_scores = base_performance + np.random.normal(0, 0.3, n_students)
            
            # Ensure scores are in 0-4 range
            inst_a_scores = np.clip(inst_a_scores, 0, 4)
            inst_b_scores = np.clip(inst_b_scores, 0, 4)
            
            corr_data = pd.DataFrame({
                f'{inst_a} Score': inst_a_scores,
                f'{inst_b} Score': inst_b_scores
            })
            
            # Calculate correlation
            correlation = corr_data.corr().iloc[0, 1]
            
            # Display correlation metric
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Pearson Correlation", f"{correlation:.3f}")
            with col2:
                strength = "Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.4 else "Weak"
                st.metric("Correlation Strength", strength)
            with col3:
                direction = "Positive" if correlation > 0 else "Negative"
                st.metric("Direction", direction)
            
            st.markdown("---")
            
            # Scatter plot
            fig = px.scatter(
                corr_data,
                x=f'{inst_a} Score',
                y=f'{inst_b} Score',
                title=f"Performance Correlation: {inst_a} vs {inst_b}",
                trendline="ols"
            )
            fig.update_layout(height=500)
            fig.update_xaxes(range=[0, 4])
            fig.update_yaxes(range=[0, 4])
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Interpretation
            st.markdown("#### Interpretation")
            
            if abs(correlation) > 0.7:
                interpretation = f"There is a **strong {direction.lower()} correlation** between {inst_a} and {inst_b}. Students who perform well in {inst_a} tend to {'also perform well' if correlation > 0 else 'struggle'} in {inst_b}."
            elif abs(correlation) > 0.4:
                interpretation = f"There is a **moderate {direction.lower()} correlation** between {inst_a} and {inst_b}. Some relationship exists between performance in these assessments."
            else:
                interpretation = f"There is a **weak correlation** between {inst_a} and {inst_b}. Performance in one assessment is not strongly predictive of performance in the other."
            
            st.info(interpretation)
            
            # Download correlation data
            csv = corr_data.to_csv(index=False)
            st.download_button(
                "Download Correlation Data",
                csv,
                file_name=f"correlation_{inst_a}_{inst_b}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please select two different instances to analyze correlation.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>INSIGHTs Admin Dashboard v1.0</strong></p>
    <p>Centralized Management for INSIGHTs Assessment Instances</p>
</div>
""", unsafe_allow_html=True)
