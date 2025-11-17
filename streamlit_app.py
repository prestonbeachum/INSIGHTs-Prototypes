"""Interactive Streamlit dashboard for the INSIGHTs Sim-U prototype.

Run locally:
  source .venv/bin/activate
  streamlit run streamlit_app.py

The app uses functions from `simu_prototype.py` to generate mock data and
renders the student & faculty visualizations interactively.
"""

import io
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm
import plotly.graph_objects as go
import plotly.express as px
import scipy.stats as stats

from simu_prototype import generate_mock_data, GROUPS, ELEMENTS, generate_socratic_metrics

# Settings
DEFAULT_OUT_DIR = Path(__file__).resolve().parent
FIGSIZE = (6, 4)
DPI = 160

st.set_page_config(page_title="INSIGHTs Sim-U Demo", layout="wide", initial_sidebar_state="expanded")

st.title("INSIGHTs — Sim-U Professional Integrity Analytics")
st.markdown("Interactive prototype demonstrating student and faculty dashboards for the first three Sim-U criteria")

# Initialize session state for active tab if not exists
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Student View"

# Sidebar controls - dynamic based on context
with st.sidebar:
    # View Mode Toggle - styled with custom CSS
    st.markdown("""
        <style>
        .view-toggle {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        .filter-section {
            /* match dark sidebar: make section transparent and remove white bar */
            background-color: transparent;
            padding: 8px 6px;
            border-radius: 6px;
            margin: 6px 0;
            border-left: 0px none;
        }
        .filter-label {
            color: #ffffff; /* white text for dark sidebar */
            font-weight: 600;
            font-size: 0.95em;
            margin-bottom: 6px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    view_mode = st.radio("", ["Student Dashboard", "Faculty Analytics"], 
                         key="view_mode", horizontal=True)
    
    st.markdown("---")
    
    if view_mode == "Student Dashboard":
        # STUDENT VIEW SIDEBAR
        st.markdown("### INSIGHTs SIM-U")
        st.caption("*Student Performance Dashboard*")
        
        st.markdown("---")
        
        # SIM-U Name dropdown
        st.markdown('<div class="filter-label">SIM-U Scenario</div>', unsafe_allow_html=True)
        sim_u_name = st.selectbox("SIM-U Name", ["SIM-U : Cardio A", "SIM-U : Cardio B", "SIM-U : Respiratory"], 
                                  key="sim_u_name", label_visibility="collapsed")
        
        st.markdown("")
        
        # Mode selection
        st.markdown('<div class="filter-label">Assessment Mode</div>', unsafe_allow_html=True)
        mode_sim_u = st.multiselect("Mode", ["Socratic", "Verbal"], default=[], 
                                    key="mode_sim_u", label_visibility="collapsed")
        
        st.markdown("")
        
        # Iteration dropdown
        st.markdown('<div class="filter-label">Iteration/Attempt</div>', unsafe_allow_html=True)
        iteration = st.selectbox("Iteration", list(range(1, 6)), 
                                key="iteration", label_visibility="collapsed",
                                help="Select which attempt to view")
        
        st.markdown("---")
        
        # Export and View buttons - styled
        col1, col2 = st.columns(2)
        with col1:
            st.button("Export PDF", use_container_width=True, key="export_pdf", type="secondary")
        with col2:
            st.button("View Details", use_container_width=True, key="view_attempt", type="secondary")
        
        # Hidden settings for data generation
        with st.expander("Advanced Settings", expanded=False):
            st.markdown("**Data Generation**")
            n_students = st.slider("Number of students", 6, 30, 12, key="student_n_students")
            n_attempts = st.slider("Attempts per student", 1, 8, 5, key="student_n_attempts")
            seed = st.number_input("Random seed", value=42, step=1, key="student_seed")
            
            st.markdown("**Student Selection**")
            students = [f"S{str(i).zfill(2)}" for i in range(1, n_students + 1)]
            selected_student = st.selectbox("Student ID", students, index=0, key="student_selected")
            
            st.markdown("**Analysis Thresholds**")
            miss_threshold = st.slider("Miss threshold (below = miss)", 0.0, 4.0, 2.0, step=0.1, format="%.1f", key="student_miss_threshold",
                                      help="Scores below this value are considered 'misses' (0-4 rubric scale)")
            min_misses = st.slider("Min co-misses for network edge", 1, 10, 2, key="student_min_misses")
            
            regenerate = st.button("Regenerate All Data", type="primary", use_container_width=True)
    
    else:
        # FACULTY VIEW SIDEBAR
        st.markdown("### INSIGHTs Faculty Analytics")
        st.caption("*Performance Analysis Dashboard*")
        
        st.markdown("---")
        
        # Time Window
        st.markdown('<div class="filter-label">⏱️ Time Window</div>', unsafe_allow_html=True)
        time_window = st.selectbox("Select Time Window", ["Attempts 1-5", "All Attempts", "Recent 3"], 
                                   key="time_window", label_visibility="collapsed",
                                   help="Filter data by attempt range")
        
        st.markdown("")
        
        # Aggregate Level
        st.markdown('<div class="filter-label">Aggregate Level</div>', unsafe_allow_html=True)
        aggregate_mode = st.radio("Aggregate Mode", ["Domain", "Node"], 
                                  key="aggregate_mode", horizontal=True, label_visibility="collapsed",
                                  help="View by domain groups or individual nodes")
        
        st.markdown("---")
        
        # Rubric Selection
        st.markdown('<div class="filter-label">Rubric Comparison</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.caption("**Rubric A**")
            rubric_a = st.selectbox("Select Rubric A", ["SIM-U: Simulation", "Socratic"], 
                                   key="rubric_a", label_visibility="collapsed",
                                   help="Select assessment rubric for Cohort A")
        with col2:
            st.caption("**Rubric B**")
            rubric_b = st.selectbox("Select Rubric B", ["Socratic", "SIM-U: Simulation"], 
                                   key="rubric_b", label_visibility="collapsed",
                                   help="Select assessment rubric for Cohort B")
        
        st.markdown("")
        
        # Metrics Filter
        st.markdown('<div class="filter-label">Focus Metric</div>', unsafe_allow_html=True)
        metric_options = ["Overall", "Communication", "Clinical Reasoning"]
        selected_metric = st.radio("Select Metric", metric_options, key="selected_metric", 
                                   label_visibility="collapsed", horizontal=True,
                                   help="Filter analysis by specific criterion")
        
        st.markdown("---")
        
        # Student Lookup
        st.markdown('<div class="filter-label">Student Lookup</div>', unsafe_allow_html=True)
        lookup_student_id = st.text_input("Student ID", placeholder="Enter Student ID (e.g., A123456)", 
                                         key="lookup_student_id", label_visibility="collapsed")
        if st.button("View Student", use_container_width=True, type="primary"):
            st.session_state.show_student_lookup = True
        
        st.markdown("---")
        
        # Network & Analysis Thresholds (moved out of expander so they work)
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown("#### Analysis Settings")
        
        miss_threshold = st.slider("Miss threshold (score below = miss)", 0.0, 4.0, 2.0, step=0.1, format="%.1f",
                                   help="Scores below this value are considered 'misses' for network analysis (0-4 rubric scale)")
        min_misses = st.slider("Min co-misses for network edge", 1, 10, 2,
                               help="Minimum number of co-occurrences needed to draw a connection in network")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Hidden settings for data generation
        with st.expander("Advanced Settings", expanded=False):
            st.markdown("**Data Generation**")
            n_students = st.slider("Number of students", 6, 30, 12)
            n_attempts = st.slider("Attempts per student", 1, 8, 5)
            seed = st.number_input("Random seed", value=42, step=1)
            
            st.markdown("**Student View**")
            students = [f"S{str(i).zfill(2)}" for i in range(1, n_students + 1)]
            selected_student = st.selectbox("Student ID", students, index=0)
            
            regenerate = st.button("Regenerate All Data", type="primary", use_container_width=True)
    
    # Ensure variables exist for backward compatibility
    if 'students' not in locals():
        n_students = 12
        students = [f"S{str(i).zfill(2)}" for i in range(1, n_students + 1)]
        n_attempts = 5
        seed = 42
        selected_student = students[0]
        regenerate = False
    
    # Ensure threshold variables exist (set defaults if not defined in current view)
    if 'miss_threshold' not in locals():
        miss_threshold = 2.0
    if 'min_misses' not in locals():
        min_misses = 2
    
    # Set defaults for faculty-only variables when in student mode
    if view_mode == "Student Dashboard":
        cohort_a = "All"
        cohort_b = "All"
        time_window = "Attempts 1-5"
        aggregate_mode = "Node"
        rubric_a = "SIM-U: Simulation"
        rubric_b = "Socratic"
        selected_metric = "Overall"
        lookup_student_id = ""
    else:
        # Set defaults for student-only variables when in faculty mode
        sim_u_name = "SIM-U : Cardio A"
        mode_sim_u = []  # Empty list means show all modes
        iteration = 1
        # Set cohort defaults since UI controls were removed
        if 'cohort_a' not in locals():
            cohort_a = "All"
        if 'cohort_b' not in locals():
            cohort_b = "All"

# Cached data generation
@st.cache_data
def get_data(students, attempts, seed, schema_version=3):
    """Generate mock data. schema_version parameter forces cache refresh when schema changes."""
    return generate_mock_data(students, attempts, seed)

# Generate or load data
attempts = list(range(1, n_attempts + 1))
if regenerate:
    # clear cache and regenerate
    get_data.clear()

df = get_data(students, attempts, seed, schema_version=3)

# Generate socratic metrics
soc_long, soc_wide = generate_socratic_metrics(students, seed)

# Tabs for better organization
tab1, tab2, tab3 = st.tabs(["Data Overview", "Student View", "Faculty View"])

# Tab 1: Data Overview
with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("**Schema**: 12 element-level columns from 3 Professional Integrity criteria (PI_01, PI_02, PI_03)")
    with col2:
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        csv_bytes = csv_buf.getvalue().encode('utf-8')
        st.download_button("Download CSV", data=csv_bytes, file_name="simu_first3_criteria_mock.csv", mime='text/csv', use_container_width=True)

# Tab 2: Student visuals (matching student dashboard mockup)
with tab2:
    st.markdown("### INSIGHTs SIM-U — Student Dashboard")
    
    # Show selected filters
    if view_mode == "Student Dashboard":
        mode_display = ', '.join(mode_sim_u) if mode_sim_u else 'All'
        st.caption(f"**{sim_u_name}** | Iteration: {iteration} | Mode: {mode_display}")
    
    # Use sidebar-selected student
    student_df = df[df['student_id'] == selected_student]
    
    # Filter by scenario if selected (Student Dashboard only)
    if view_mode == "Student Dashboard" and 'scenario' in student_df.columns:
        student_df = student_df[student_df['scenario'] == sim_u_name]
    
    # Filter by mode if selected (Student Dashboard only)
    if view_mode == "Student Dashboard" and 'mode' in student_df.columns:
        if mode_sim_u:  # If specific modes selected, filter to those
            student_df = student_df[student_df['mode'].isin(mode_sim_u)]
        # Otherwise show all modes
    
    # Filter by iteration if selected
    if view_mode == "Student Dashboard" and iteration:
        filtered_df = student_df[student_df['attempt'] == iteration]
        # If no data for that iteration, show all
        if filtered_df.empty:
            st.warning(f"No data for iteration {iteration}. Showing all attempts.")
            filtered_df = student_df
    else:
        filtered_df = student_df
    
    if not student_df.empty:
        # Summary metrics section
        st.markdown("---")
        st.markdown("#### Summary")
        col1, col2, col3 = st.columns(3)
        
        total_attempts = len(student_df)
        overall_avg = student_df[ELEMENTS].mean().mean()
        
        # Use filtered data for last score if iteration is selected
        if view_mode == "Student Dashboard" and iteration and not filtered_df.empty:
            last_score = filtered_df[ELEMENTS].mean().mean()
        else:
            last_score = student_df.sort_values('attempt', ascending=False).iloc[0][ELEMENTS].mean()
        
        with col1:
            st.metric("Attempts", total_attempts)
        with col2:
            st.metric("Overall average", f"{overall_avg:.0f}")
        with col3:
            st.metric("Last Score", f"{last_score:.0f}")
        
        # Scores section - horizontal bar chart
        st.markdown("---")
        st.markdown("#### Scores")
        
        # Use iteration-specific data if selected
        display_df = filtered_df if (view_mode == "Student Dashboard" and iteration and not filtered_df.empty) else student_df
        
        # Get per-attempt scores for each group
        student_copy = display_df.copy()
        for gname, elements in GROUPS.items():
            student_copy[gname] = student_copy[elements].mean(axis=1)
        
        # Create horizontal bar chart for latest/selected attempt
        latest_attempt = student_copy.sort_values('attempt', ascending=False).iloc[0]
        group_scores = {g.replace('PI_', '').replace('_', ' '): latest_attempt[g] for g in GROUPS.keys()}
        
        # Define colors for all 4 criteria
        criterion_colors = ['#2ECC71', '#3498DB', '#9B59B6', '#E67E22']
        
        fig = go.Figure()
        for i, (group_name, score) in enumerate(group_scores.items()):
            fig.add_trace(go.Bar(
                y=[group_name],
                x=[score],
                orientation='h',
                marker_color=criterion_colors[i],
                text=f"{score:.0f}",
                textposition='inside',
                textfont=dict(color='white', size=14),
                hovertemplate=f'<b>{group_name}</b><br>Score: {score:.1f}<extra></extra>',
                showlegend=False
            ))
        
        fig.update_layout(
            xaxis_range=[0, 4],
            xaxis_title='Score (0-4 rubric scale)',
            yaxis_title='',
            height=250,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Qualitative Feedback section
        st.markdown("---")
        st.markdown("#### Qualitative Feedback (AI)")
        
        # Show which iteration is being analyzed
        if view_mode == "Student Dashboard" and iteration:
            st.caption(f"*Feedback for Iteration {iteration}*")
        
        # Generate mock feedback based on scores (0-4 rubric scale)
        feedback_items = []
        for gname, elements in GROUPS.items():
            avg_score = latest_attempt[gname]
            group_label = gname.replace('PI_', '').replace('_', ' ')
            
            if avg_score >= 3.5:  # Exemplary
                feedback_items.append(f"**{group_label}**: Strong performance - identified key elements effectively")
            elif avg_score >= 2.5:  # Proficient
                feedback_items.append(f"**{group_label}**: Good understanding - minor areas for improvement")
            else:  # Developing or below
                feedback_items.append(f"**{group_label}**: Review recommended - focus on core principles")
        
        # Add mode-specific feedback
        if view_mode == "Student Dashboard":
            if "Socratic" in mode_sim_u:
                feedback_items.append(f"**Communication**: Socratic dialogue skills demonstrate effective questioning")
            if "Verbal" in mode_sim_u:
                feedback_items.append(f"**Clinical Reasoning**: Verbal communication shows clear thought process")
        
        feedback_items.append(f"**Next steps**: Review rubric nodes and practice scenarios before next attempt")
        
        for item in feedback_items:
            st.markdown(f"• {item}")
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.button("Export PDF", use_container_width=True)
        with col2:
            st.button("View attempt details", use_container_width=True)
    else:
        st.warning(f"No data for {selected_student}")

# Tab 3: Faculty visuals (matching faculty analytics mockup)
with tab3:
    st.markdown("### INSIGHTs Faculty Analytics")
    
    # Display current filter settings
    st.caption(f"**Time Window:** {time_window} | **Rubrics:** {rubric_a} vs {rubric_b}")
    st.caption(f"**Analysis Settings:** Miss Threshold: {miss_threshold} | Min Co-Misses: {min_misses}")
    st.markdown("---")
    
    # Apply cohort filters - split data based on selection
    if cohort_a == "Undergrad":
        cohort_a_data = df[df['student_id'].isin(students[:len(students)//2])]
    elif cohort_a == "Graduate":
        cohort_a_data = df[df['student_id'].isin(students[len(students)//2:])]
    else:  # All
        cohort_a_data = df.copy()
    
    if cohort_b == "Graduate":
        cohort_b_data = df[df['student_id'].isin(students[len(students)//2:])]
    elif cohort_b == "Undergrad":
        cohort_b_data = df[df['student_id'].isin(students[:len(students)//2])]
    else:  # All
        cohort_b_data = df.copy()
    
    # Apply time window filters
    if time_window == "Attempts 1-5":
        cohort_a_data = cohort_a_data[cohort_a_data['attempt'] <= 5]
        cohort_b_data = cohort_b_data[cohort_b_data['attempt'] <= 5]
    elif time_window == "Recent 3":
        max_attempt = df['attempt'].max()
        cohort_a_data = cohort_a_data[cohort_a_data['attempt'] >= max_attempt - 2]
        cohort_b_data = cohort_b_data[cohort_b_data['attempt'] >= max_attempt - 2]
    # "All Attempts" - no filter needed
    
    # Determine which data source and elements to use based on rubric and metric filters
    # Rubric determines the data source, Metric filters which columns within that source
    
    # For Cohort A - determine data source and elements based on rubric
    if rubric_a == "SIM-U: Simulation":
        # Use SIM-U elements
        if selected_metric == "Overall":
            stat_elements_a = ELEMENTS
        elif selected_metric == "Communication":
            stat_elements_a = GROUPS['PI_01_Foster_Integrity']
        elif selected_metric == "Clinical Reasoning":
            stat_elements_a = GROUPS['PI_02_Safe_Learning_Environment']
        else:
            stat_elements_a = ELEMENTS
        cohort_a_scores = cohort_a_data
    else:  # Socratic
        # Use Socratic metrics - merge with socratic data
        stat_elements_a = [col for col in soc_wide.columns if col.startswith('socratic_')]
        # Merge cohort_a student IDs with socratic scores and apply time window
        cohort_a_students = cohort_a_data['student_id'].unique()
        cohort_a_scores = soc_wide[soc_wide['student_id'].isin(cohort_a_students)]
        
        # Apply time window filter to socratic data
        if time_window == "Attempts 1-5":
            cohort_a_scores = cohort_a_scores[cohort_a_scores['attempt'] <= 5]
        elif time_window == "Recent 3":
            max_attempt = soc_wide['attempt'].max()
            cohort_a_scores = cohort_a_scores[cohort_a_scores['attempt'] >= max_attempt - 2]
    
    # For Cohort B - determine data source and elements based on rubric
    if rubric_b == "SIM-U: Simulation":
        # Use SIM-U elements
        if selected_metric == "Overall":
            stat_elements_b = ELEMENTS
        elif selected_metric == "Communication":
            stat_elements_b = GROUPS['PI_01_Foster_Integrity']
        elif selected_metric == "Clinical Reasoning":
            stat_elements_b = GROUPS['PI_02_Safe_Learning_Environment']
        else:
            stat_elements_b = ELEMENTS
        cohort_b_scores = cohort_b_data
    else:  # Socratic
        # Use Socratic metrics
        stat_elements_b = [col for col in soc_wide.columns if col.startswith('socratic_')]
        cohort_b_students = cohort_b_data['student_id'].unique()
        cohort_b_scores = soc_wide[soc_wide['student_id'].isin(cohort_b_students)]
        
        # Apply time window filter to socratic data
        if time_window == "Attempts 1-5":
            cohort_b_scores = cohort_b_scores[cohort_b_scores['attempt'] <= 5]
        elif time_window == "Recent 3":
            max_attempt = soc_wide['attempt'].max()
            cohort_b_scores = cohort_b_scores[cohort_b_scores['attempt'] >= max_attempt - 2]
    
    # Cohort Size and Statistics
    st.markdown("#### Cohort Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Cohort Size**")
        st.markdown(f"**A ({cohort_a}):** {len(cohort_a_data['student_id'].unique())}")
        st.markdown(f"**B ({cohort_b}):** {len(cohort_b_data['student_id'].unique())}")
    
    with col2:
        st.markdown(f"**Mean score ({selected_metric})**")
        st.caption(f"A: {rubric_a.split(':')[0].strip()} | B: {rubric_b.split(':')[0].strip()}")
        
        # Calculate means based on rubric selection
        if len(cohort_a_scores) > 0:
            mean_a = cohort_a_scores[stat_elements_a].mean().mean()
        else:
            mean_a = 0
            
        if len(cohort_b_scores) > 0:
            mean_b = cohort_b_scores[stat_elements_b].mean().mean()
        else:
            mean_b = 0
            
        st.markdown(f"**A:** {mean_a:.1f}")
        st.markdown(f"**B:** {mean_b:.1f}")
    
    with col3:
        st.markdown("**Mean from 1st to recent**")
        
        # For Cohort A - calculate change based on rubric
        if rubric_a == "SIM-U: Simulation" and len(cohort_a_data) > 0:
            first_a = cohort_a_data[cohort_a_data['attempt'] == cohort_a_data['attempt'].min()][stat_elements_a].mean().mean()
            last_a = cohort_a_data[cohort_a_data['attempt'] == cohort_a_data['attempt'].max()][stat_elements_a].mean().mean()
            change_a = last_a - first_a
        elif rubric_a == "Socratic" and len(cohort_a_scores) > 0:
            first_a = cohort_a_scores[cohort_a_scores['attempt'] == cohort_a_scores['attempt'].min()][stat_elements_a].mean().mean()
            last_a = cohort_a_scores[cohort_a_scores['attempt'] == cohort_a_scores['attempt'].max()][stat_elements_a].mean().mean()
            change_a = last_a - first_a
        else:
            change_a = 0
        
        # For Cohort B - calculate change based on rubric
        if rubric_b == "SIM-U: Simulation" and len(cohort_b_data) > 0:
            first_b = cohort_b_data[cohort_b_data['attempt'] == cohort_b_data['attempt'].min()][stat_elements_b].mean().mean()
            last_b = cohort_b_data[cohort_b_data['attempt'] == cohort_b_data['attempt'].max()][stat_elements_b].mean().mean()
            change_b = last_b - first_b
        elif rubric_b == "Socratic" and len(cohort_b_scores) > 0:
            first_b = cohort_b_scores[cohort_b_scores['attempt'] == cohort_b_scores['attempt'].min()][stat_elements_b].mean().mean()
            last_b = cohort_b_scores[cohort_b_scores['attempt'] == cohort_b_scores['attempt'].max()][stat_elements_b].mean().mean()
            change_b = last_b - first_b
        else:
            change_b = 0
        
        st.markdown(f"**A:** {'+' if change_a >= 0 else ''}{change_a:.1f}")
        st.markdown(f"**B:** {'+' if change_b >= 0 else ''}{change_b:.1f}")
    
    st.markdown("---")
    
    # Attempts Overall Score Trend
    st.markdown(f"#### {time_window} — Overall Score Trend")
    st.caption(f"Cohort A: {rubric_a} | Cohort B: {rubric_b}")
    
    # Calculate trend data based on rubric selection for each cohort
    # Cohort A trend
    if rubric_a == "SIM-U: Simulation" and len(cohort_a_data) > 0:
        cohort_a_trend = cohort_a_data.groupby('attempt').apply(lambda x: x[stat_elements_a].mean().mean()).reset_index()
        cohort_a_trend.columns = ['attempt', 'score']
    elif rubric_a == "Socratic" and len(cohort_a_scores) > 0:
        # For Socratic, now we have attempt tracking too
        cohort_a_trend = cohort_a_scores.groupby('attempt').apply(lambda x: x[stat_elements_a].mean().mean()).reset_index()
        cohort_a_trend.columns = ['attempt', 'score']
    else:
        cohort_a_trend = pd.DataFrame({'attempt': [], 'score': []})
    
    # Cohort B trend
    if rubric_b == "SIM-U: Simulation" and len(cohort_b_data) > 0:
        cohort_b_trend = cohort_b_data.groupby('attempt').apply(lambda x: x[stat_elements_b].mean().mean()).reset_index()
        cohort_b_trend.columns = ['attempt', 'score']
    elif rubric_b == "Socratic" and len(cohort_b_scores) > 0:
        # For Socratic, now we have attempt tracking too
        cohort_b_trend = cohort_b_scores.groupby('attempt').apply(lambda x: x[stat_elements_b].mean().mean()).reset_index()
        cohort_b_trend.columns = ['attempt', 'score']
    else:
        cohort_b_trend = pd.DataFrame({'attempt': [], 'score': []})
    
    fig = go.Figure()
    if not cohort_a_trend.empty:
        fig.add_trace(go.Scatter(
            x=cohort_a_trend['attempt'], y=cohort_a_trend['score'],
            mode='lines+markers',
            name=f"{cohort_a} ({rubric_a.split(':')[0].strip()})",
            line=dict(color='#3498DB', width=3),
            marker=dict(size=8)
        ))
    if not cohort_b_trend.empty:
        fig.add_trace(go.Scatter(
            x=cohort_b_trend['attempt'], y=cohort_b_trend['score'],
            mode='lines+markers',
            name=f"{cohort_b} ({rubric_b.split(':')[0].strip()})",
            line=dict(color='#E67E22', width=3),
            marker=dict(size=8)
        ))
    fig.update_layout(
        xaxis_title='Attempt #',
        yaxis_title=f'{selected_metric} score (0-4 rubric scale)',
        height=350,
        yaxis_range=[0, 4],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # First row: Centrality plots
    st.markdown("**Centrality Plot**")
    st.caption(f"Identify most influential {aggregate_mode.lower()}s based on co-miss patterns • Metric: {selected_metric}")
    
    # Combine both cohorts for centrality analysis (respecting rubric filters)
    # For centrality, we analyze the combined filtered data from both cohorts
    if rubric_a == "SIM-U: Simulation" and rubric_b == "SIM-U: Simulation":
        # Both using SIM-U data - combine without dropping duplicates if they're different cohorts
        # This ensures we have all the data from both selections
        combined_cohort_data = pd.concat([cohort_a_data, cohort_b_data], ignore_index=True)
        # Only drop exact duplicate rows (same student, same attempt)
        combined_cohort_data = combined_cohort_data.drop_duplicates(subset=['student_id', 'attempt'], keep='first')
    elif rubric_a == "SIM-U: Simulation":
        # Only Cohort A uses SIM-U, use just that
        combined_cohort_data = cohort_a_data.copy()
    elif rubric_b == "SIM-U: Simulation":
        # Only Cohort B uses SIM-U, use just that
        combined_cohort_data = cohort_b_data.copy()
    else:
        # Neither using SIM-U (both Socratic) - can't do centrality on Socratic data
        combined_cohort_data = pd.DataFrame()
        st.info("Network centrality analysis requires at least one cohort using SIM-U: Simulation rubric. Currently both cohorts are using Socratic rubric.")
        st.markdown("---")
    
    # Determine which elements to use based on metric filter
    if selected_metric == "Overall":
        centrality_elements = ELEMENTS
    elif selected_metric == "Communication":
        centrality_elements = GROUPS['PI_01_Foster_Integrity']
    elif selected_metric == "Clinical Reasoning":
        centrality_elements = GROUPS['PI_02_Safe_Learning_Environment']
    else:
        centrality_elements = ELEMENTS
    
    # Build co-occurrence network for centrality analysis using filtered cohort data
    cohort_misses = combined_cohort_data.copy()
    
    # Debug info
    if len(cohort_misses) == 0:
        st.warning(f"No data available after filtering. Cohort A size: {len(cohort_a_data)}, Cohort B size: {len(cohort_b_data)}. Selected rubrics: {rubric_a} vs {rubric_b}")
    else:
        # Show debug info about filtering
        st.caption(f"Debug: Analyzing {len(centrality_elements)} elements from {selected_metric} metric. Data rows: {len(cohort_misses)}")
    
    # Convert scores to miss indicators (True if below threshold)
    for c in centrality_elements:
        if c in cohort_misses.columns:
            cohort_misses[c] = cohort_misses[c] < miss_threshold
    
    G_central = nx.Graph()
    
    # Adaptive threshold: use lower threshold for filtered metrics with fewer elements
    # This ensures networks can still be visualized when focusing on specific criteria
    if len(centrality_elements) <= 4:
        # For single criterion (4 elements), use minimum threshold of 1
        effective_min_misses = max(1, min(min_misses, 1))
        if min_misses > 1:
            st.caption(f"Note: Using relaxed threshold ({effective_min_misses} co-miss) for focused metric analysis with {len(centrality_elements)} elements")
    else:
        effective_min_misses = min_misses
    
    
    # Only build centrality if we have valid data
    if len(cohort_misses) > 0 and len(centrality_elements) > 0:
        if aggregate_mode == "Domain":
            # Aggregate by domain (group level)
            for group_name, group_elements in GROUPS.items():
                # Only include groups that overlap with centrality_elements
                group_overlap = [e for e in group_elements if e in centrality_elements]
                if group_overlap:
                    miss_count = cohort_misses[group_overlap].apply(lambda row: row.sum(), axis=1).sum()
                    G_central.add_node(group_name, miss_count=miss_count)
            
            # Create edges between domains using student-level co-misses
            if 'student_id' in cohort_misses.columns:
                student_misses = cohort_misses.groupby('student_id')[centrality_elements].any()
                
                group_names = list(G_central.nodes())
                for i, g1 in enumerate(group_names):
                    for g2 in group_names[i+1:]:
                        g1_elements = [e for e in GROUPS[g1] if e in centrality_elements]
                        g2_elements = [e for e in GROUPS[g2] if e in centrality_elements]
                        
                        if g1_elements and g2_elements:
                            # Count students who missed elements from both domains
                            co_miss = 0
                            for e1 in g1_elements:
                                for e2 in g2_elements:
                                    if e1 in student_misses.columns and e2 in student_misses.columns:
                                        co_miss += (student_misses[e1] & student_misses[e2]).sum()
                            
                            if co_miss >= effective_min_misses * len(g1_elements) * len(g2_elements) / 4:
                                G_central.add_edge(g1, g2, weight=co_miss)
            else:
                # Fallback to old method
                group_names = list(G_central.nodes())
                for i, g1 in enumerate(group_names):
                    for g2 in group_names[i+1:]:
                        g1_elements = [e for e in GROUPS[g1] if e in centrality_elements]
                        g2_elements = [e for e in GROUPS[g2] if e in centrality_elements]
                        
                        if g1_elements and g2_elements:
                            # Count co-misses across domains
                            co_miss = 0
                            for e1 in g1_elements:
                                for e2 in g2_elements:
                                    co_miss += ((cohort_misses[e1]) & (cohort_misses[e2])).sum()
                            
                            if co_miss >= effective_min_misses * len(g1_elements) * len(g2_elements) / 4:
                                G_central.add_edge(g1, g2, weight=co_miss)
        else:
            # Node level (element level)
            for c in centrality_elements:
                if c in cohort_misses.columns:
                    miss_count = cohort_misses[c].sum()
                    G_central.add_node(c, miss_count=miss_count)
            
            # NEW APPROACH: Count students who miss both elements (across any of their attempts)
            # This is more educationally meaningful than requiring simultaneous misses in same attempt
            if 'student_id' in cohort_misses.columns:
                # Group by student and check if they missed each element at least once
                student_misses = cohort_misses.groupby('student_id')[centrality_elements].any()
                
                for i, c1 in enumerate(centrality_elements):
                    for c2 in centrality_elements[i+1:]:
                        if c1 in student_misses.columns and c2 in student_misses.columns:
                            # Count students who missed BOTH elements (in any attempt)
                            co_miss = (student_misses[c1] & student_misses[c2]).sum()
                            if co_miss >= effective_min_misses:
                                G_central.add_edge(c1, c2, weight=co_miss)
            else:
                # Fallback to old method if student_id not available
                for i, c1 in enumerate(centrality_elements):
                    for c2 in centrality_elements[i+1:]:
                        if c1 in cohort_misses.columns and c2 in cohort_misses.columns:
                            co_miss = ((cohort_misses[c1]) & (cohort_misses[c2])).sum()
                            if co_miss >= effective_min_misses:
                                G_central.add_edge(c1, c2, weight=co_miss)
    
    if len(G_central.edges()) > 0:
        # Create tabs for better organization
        net_tab1, net_tab2, net_tab3 = st.tabs(["Centrality Plot", "Network Visualizations", "Correlation Plot"])
        
        with net_tab1:
            # Calculate centrality measures
            degree_centrality = nx.degree_centrality(G_central)
            betweenness_centrality = nx.betweenness_centrality(G_central)
            closeness_centrality = nx.closeness_centrality(G_central)
            
            # Create dataframe for plotting
            centrality_data = pd.DataFrame({
                'Element': list(degree_centrality.keys()),
                'Degree': list(degree_centrality.values()),
                'Betweenness': list(betweenness_centrality.values()),
                'Closeness': list(closeness_centrality.values())
            })
            
            # Format labels based on aggregate mode
            if aggregate_mode == "Domain":
                centrality_data['Element_Label'] = centrality_data['Element'].str.replace('PI_0', '').str.replace('_', ' ')
            else:
                centrality_data['Element_Label'] = centrality_data['Element'].str.replace('_', ' ').str.title()
            
            centrality_data = centrality_data.sort_values('Degree', ascending=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Degree Centrality**")
                st.caption("Direct connections strength")
                fig_degree = go.Figure()
                fig_degree.add_trace(go.Bar(
                    y=centrality_data['Element_Label'],
                    x=centrality_data['Degree'],
                    orientation='h',
                    marker=dict(
                        color=centrality_data['Degree'],
                        colorscale=[[0, '#E3F2FD'], [0.5, '#42A5F5'], [1, '#0D47A1']],
                        showscale=False,
                        line=dict(color='#1976D2', width=1)
                    ),
                    text=centrality_data['Degree'].apply(lambda x: f'{x:.2f}'),
                    textposition='outside',
                    textfont=dict(size=11, color='#000000', family='Arial, sans-serif'),
                    hovertemplate='<b>%{y}</b><br>Degree: %{x:.3f}<br><i>Number of connections</i><extra></extra>'
                ))
                fig_degree.update_layout(
                    height=450,
                    margin=dict(l=10, r=70, t=20, b=40),
                    xaxis_title='',
                    yaxis_title='',
                    plot_bgcolor='#FAFAFA',
                    paper_bgcolor='white',
                    font=dict(size=12, color='#000000', family='Arial, sans-serif'),
                    xaxis=dict(
                        showgrid=True, 
                        gridcolor='#E0E0E0',
                        gridwidth=1,
                        zeroline=True,
                        zerolinecolor='#BDBDBD',
                        zerolinewidth=2,
                        tickfont=dict(size=11, color='#000000')
                    ),
                    yaxis=dict(
                        showgrid=False,
                        tickfont=dict(size=11, color='#000000')
                    )
                )
                st.plotly_chart(fig_degree, use_container_width=True)
        
        with col2:
            st.markdown("**Closeness Centrality**")
            st.caption("Proximity to all nodes")
            centrality_data_close = centrality_data.sort_values('Closeness', ascending=True)
            fig_close = go.Figure()
            fig_close.add_trace(go.Bar(
                y=centrality_data_close['Element_Label'],
                x=centrality_data_close['Closeness'],
                orientation='h',
                marker=dict(
                    color=centrality_data_close['Closeness'],
                    colorscale=[[0, '#FFF3E0'], [0.5, '#FF9800'], [1, '#E65100']],
                    showscale=False,
                    line=dict(color='#F57C00', width=1)
                ),
                text=centrality_data_close['Closeness'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                textfont=dict(size=11, color='#000000', family='Arial, sans-serif'),
                hovertemplate='<b>%{y}</b><br>Closeness: %{x:.3f}<br><i>Average path distance</i><extra></extra>'
            ))
            fig_close.update_layout(
                height=450,
                margin=dict(l=10, r=70, t=20, b=40),
                xaxis_title='',
                yaxis_title='',
                plot_bgcolor='#FAFAFA',
                paper_bgcolor='white',
                font=dict(size=12, color='#000000', family='Arial, sans-serif'),
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#E0E0E0',
                    gridwidth=1,
                    zeroline=True,
                    zerolinecolor='#BDBDBD',
                    zerolinewidth=2,
                    tickfont=dict(size=11, color='#000000')
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11, color='#000000')
                )
            )
            st.plotly_chart(fig_close, use_container_width=True)
        
        with col3:
            st.markdown("**Betweenness Centrality**")
            st.caption("Bridge between clusters")
            centrality_data_between = centrality_data.sort_values('Betweenness', ascending=True)
            fig_between = go.Figure()
            fig_between.add_trace(go.Bar(
                y=centrality_data_between['Element_Label'],
                x=centrality_data_between['Betweenness'],
                orientation='h',
                marker=dict(
                    color=centrality_data_between['Betweenness'],
                    colorscale=[[0, '#E0F2F1'], [0.5, '#26A69A'], [1, '#004D40']],
                    showscale=False,
                    line=dict(color='#00897B', width=1)
                ),
                text=centrality_data_between['Betweenness'].apply(lambda x: f'{x:.2f}'),
                textposition='outside',
                textfont=dict(size=11, color='#000000', family='Arial, sans-serif'),
                hovertemplate='<b>%{y}</b><br>Betweenness: %{x:.3f}<br><i>Shortest path frequency</i><extra></extra>'
            ))
            fig_between.update_layout(
                height=450,
                margin=dict(l=10, r=70, t=20, b=40),
                xaxis_title='',
                yaxis_title='',
                plot_bgcolor='#FAFAFA',
                paper_bgcolor='white',
                font=dict(size=12, color='#000000', family='Arial, sans-serif'),
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#E0E0E0',
                    gridwidth=1,
                    zeroline=True,
                    zerolinecolor='#BDBDBD',
                    zerolinewidth=2,
                    tickfont=dict(size=11, color='#000000')
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11, color='#000000')
                )
            )
            st.plotly_chart(fig_between, use_container_width=True)
        
        with net_tab2:
            # Only show network visualizations if we have data
            if len(combined_cohort_data) > 0:
                # Build co-occurrence network using filtered cohort data
                cohort_network_misses = combined_cohort_data.copy()
                
                # Determine which elements to show based on aggregate mode and metric
                if aggregate_mode == "Domain":
                    network_elements = centrality_elements
                else:
                    network_elements = centrality_elements
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Static Network**")
                    st.caption("Fixed layout showing co-missed elements")
                    
                    G_static = nx.Graph()
                    
                    if len(cohort_network_misses) > 0:
                        for c in network_elements:
                            if c in cohort_network_misses.columns:
                                cohort_network_misses[c] = cohort_network_misses[c] < miss_threshold
                                miss_count = cohort_network_misses[c].sum()
                                G_static.add_node(c, miss_count=miss_count)
                        
                        # Use student-level co-misses for consistency
                        if 'student_id' in cohort_network_misses.columns:
                            student_misses_static = cohort_network_misses.groupby('student_id')[network_elements].any()
                            
                            for i, c1 in enumerate(network_elements):
                                for c2 in network_elements[i+1:]:
                                    if c1 in student_misses_static.columns and c2 in student_misses_static.columns:
                                        co_miss = (student_misses_static[c1] & student_misses_static[c2]).sum()
                                        # Use effective threshold for filtered metrics
                                        threshold_to_use = 1 if len(network_elements) <= 4 else min_misses
                                        if co_miss >= threshold_to_use:
                                            G_static.add_edge(c1, c2, weight=co_miss)
                        else:
                            # Fallback to attempt-level
                            for i, c1 in enumerate(network_elements):
                                for c2 in network_elements[i+1:]:
                                    if c1 in cohort_network_misses.columns and c2 in cohort_network_misses.columns:
                                        co_miss = ((cohort_network_misses[c1]) & (cohort_network_misses[c2])).sum()
                                        threshold_to_use = 1 if len(network_elements) <= 4 else min_misses
                                        if co_miss >= threshold_to_use:
                                            G_static.add_edge(c1, c2, weight=co_miss)
                    
                    if len(G_static.edges()) > 0:
                        # Use spring layout for static network
                        pos_static = nx.spring_layout(G_static, k=2, iterations=50, seed=42)
                        
                        # Create edges
                        edge_trace_static = []
                        for edge in G_static.edges(data=True):
                            x0, y0 = pos_static[edge[0]]
                            x1, y1 = pos_static[edge[1]]
                            edge_trace_static.append(go.Scatter(
                                x=[x0, x1, None],
                                y=[y0, y1, None],
                                mode='lines',
                                line=dict(width=2, color='#95A5A6'),
                                hoverinfo='skip',
                                showlegend=False
                            ))
                        
                        # Create nodes
                        node_x = []
                        node_y = []
                        node_text = []
                        node_colors = []
                        node_sizes = []
                        
                        for node in G_static.nodes(data=True):
                            x, y = pos_static[node[0]]
                            node_x.append(x)
                            node_y.append(y)
                            label = node[0].replace('PI_0', '').replace('_', ' ')
                            node_text.append(label)
                            miss_count = node[1]['miss_count']
                            node_colors.append(miss_count)
                            node_sizes.append(max(20, min(50, miss_count * 3)))
                        
                        node_trace_static = go.Scatter(
                            x=node_x,
                            y=node_y,
                            mode='markers+text',
                            marker=dict(
                                size=node_sizes,
                                color=node_colors,
                                colorscale=['#3498DB', '#E67E22', '#E74C3C'],
                                showscale=False,
                                line=dict(width=2, color='white')
                            ),
                            text=node_text,
                            textposition='top center',
                            textfont=dict(size=8, color='black'),
                            hovertemplate='<b>%{text}</b><br>Misses: %{marker.color}<extra></extra>',
                            showlegend=False
                        )
                        
                        fig_static = go.Figure(data=edge_trace_static + [node_trace_static])
                        fig_static.update_layout(
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(l=0, r=0, t=0, b=0),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            plot_bgcolor='white',
                            height=500
                        )
                        
                        st.plotly_chart(fig_static, use_container_width=True)
                    else:
                        st.info(f"No network edges found (threshold ≥ {min_misses}). Try lowering the threshold or selecting more data.")
                
                with col2:
                    st.markdown("**Force-Directed Network**")
                    st.caption("Interactive - drag nodes to explore connections")
                    
                    # Build same network for force-directed using filtered data
                    G_force = nx.Graph()
                    
                    if len(cohort_network_misses) > 0:
                        for c in network_elements:
                            if c in cohort_network_misses.columns:
                                miss_count = cohort_network_misses[c].sum()
                                G_force.add_node(c, miss_count=miss_count)
                        
                        # Use student-level co-misses for consistency
                        if 'student_id' in cohort_network_misses.columns:
                            student_misses_force = cohort_network_misses.groupby('student_id')[network_elements].any()
                            
                            for i, c1 in enumerate(network_elements):
                                for c2 in network_elements[i+1:]:
                                    if c1 in student_misses_force.columns and c2 in student_misses_force.columns:
                                        co_miss = (student_misses_force[c1] & student_misses_force[c2]).sum()
                                        # Use effective threshold for filtered metrics
                                        threshold_to_use = 1 if len(network_elements) <= 4 else min_misses
                                        if co_miss >= threshold_to_use:
                                            G_force.add_edge(c1, c2, weight=co_miss)
                        else:
                            # Fallback to attempt-level
                            for i, c1 in enumerate(network_elements):
                                for c2 in network_elements[i+1:]:
                                    if c1 in cohort_network_misses.columns and c2 in cohort_network_misses.columns:
                                        co_miss = ((cohort_network_misses[c1]) & (cohort_network_misses[c2])).sum()
                                        threshold_to_use = 1 if len(network_elements) <= 4 else min_misses
                                        if co_miss >= threshold_to_use:
                                            G_force.add_edge(c1, c2, weight=co_miss)
                    
                    if len(G_force.edges()) > 0:
                        # Use spring layout as initial positions
                        pos_force = nx.spring_layout(G_force, k=2, iterations=50, seed=42)
                        
                        # Create edges with weights
                        edge_trace_force = []
                        for edge in G_force.edges(data=True):
                            x0, y0 = pos_force[edge[0]]
                            x1, y1 = pos_force[edge[1]]
                            weight = edge[2]['weight']
                            edge_trace_force.append(go.Scatter(
                                x=[x0, x1, None],
                                y=[y0, y1, None],
                                mode='lines',
                                line=dict(width=weight * 0.5, color='#BDC3C7'),
                                hovertemplate=f'Co-misses: {weight}<extra></extra>',
                                showlegend=False
                            ))
                        
                        # Create draggable nodes
                        node_x_force = []
                        node_y_force = []
                        node_text_force = []
                        node_colors_force = []
                        node_sizes_force = []
                        
                        for node in G_force.nodes(data=True):
                            x, y = pos_force[node[0]]
                            node_x_force.append(x)
                            node_y_force.append(y)
                            label = node[0].replace('PI_0', '').replace('_', ' ')
                            node_text_force.append(label)
                            miss_count = node[1]['miss_count']
                            node_colors_force.append(miss_count)
                            node_sizes_force.append(max(25, min(60, miss_count * 3)))
                        
                        node_trace_force = go.Scatter(
                            x=node_x_force,
                            y=node_y_force,
                            mode='markers+text',
                            marker=dict(
                                size=node_sizes_force,
                                color=node_colors_force,
                                colorscale='Viridis',
                                showscale=True,
                                colorbar=dict(title='Misses', thickness=15, len=0.5),
                                line=dict(width=2, color='white')
                            ),
                            text=node_text_force,
                            textposition='top center',
                            textfont=dict(size=9, color='black', family='Arial Black'),
                            hovertemplate='<b>%{text}</b><br>Misses: %{marker.color}<extra></extra>',
                            showlegend=False
                        )
                        
                        fig_force = go.Figure(data=edge_trace_force + [node_trace_force])
                        fig_force.update_layout(
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(l=0, r=0, t=0, b=0),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            plot_bgcolor='white',
                            height=500,
                            dragmode='pan'  # Enable dragging
                        )
                        
                        # Make nodes draggable by updating traces
                        fig_force.update_traces(selector=dict(mode='markers+text'))
                        
                        st.plotly_chart(fig_force, use_container_width=True)
                        st.caption("Click and drag nodes to rearrange the network")
                    else:
                        st.info(f"No network edges found (threshold ≥ {min_misses}). Try lowering the threshold or selecting more data.")
        
        with net_tab3:
            st.markdown("**Element Correlation Analysis**")
            st.caption("Pairwise correlations between elements with 95% confidence intervals")
            
            # Filter settings
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                corr_net_metric = st.selectbox(
                    "Focus Metric",
                    ["Overall", "Communication", "Clinical Reasoning"],
                    key="corr_net_metric",
                    help="Filter to specific metric or show all elements"
                )
            
            with col_filter2:
                max_p_value = st.slider(
                    "Maximum p-value",
                    min_value=0.001,
                    max_value=0.10,
                    value=0.05,
                    step=0.001,
                    format="%.3f",
                    key="max_p_value_net",
                    help="Only show correlations with p-value below this threshold (p < 0.05 = statistically significant)"
                )
            
            # Determine which elements to analyze based on metric filter
            if corr_net_metric == "Overall":
                corr_net_elements = ELEMENTS
            elif corr_net_metric == "Communication":
                corr_net_elements = GROUPS['PI_01_Foster_Integrity']
            elif corr_net_metric == "Clinical Reasoning":
                corr_net_elements = GROUPS['PI_02_Safe_Learning_Environment']
            else:
                corr_net_elements = ELEMENTS
            
            # Use the combined cohort data for correlation analysis
            if len(combined_cohort_data) > 0:
                correlation_pairs = []
                
                for i, elem1 in enumerate(corr_net_elements):
                    for elem2 in corr_net_elements[i+1:]:
                        if elem1 in combined_cohort_data.columns and elem2 in combined_cohort_data.columns:
                            # Calculate correlation with p-value
                            valid_data = combined_cohort_data[[elem1, elem2]].dropna()
                            if len(valid_data) > 3:  # Need at least 4 data points
                                # Use scipy.stats.pearsonr to get both r and p-value
                                corr, p_value = stats.pearsonr(valid_data[elem1], valid_data[elem2])
                                n = len(valid_data)
                                
                                # Calculate confidence interval using Fisher z-transformation
                                if abs(corr) < 0.999:  # Avoid division by zero
                                    z = np.arctanh(corr)
                                    se = 1 / np.sqrt(n - 3)
                                    ci = 1.96 * se  # 95% CI
                                    lower = np.tanh(z - ci)
                                    upper = np.tanh(z + ci)
                                else:
                                    lower = corr
                                    upper = corr
                                
                                # Filter by p-value instead of correlation threshold
                                if p_value < max_p_value:
                                    correlation_pairs.append({
                                        'Element 1': elem1.replace('_', ' ').title(),
                                        'Element 2': elem2.replace('_', ' ').title(),
                                        'Pair': f"{elem1.replace('_', ' ').title()} ~ {elem2.replace('_', ' ').title()}",
                                        'Correlation': corr,
                                        'P_Value': p_value,
                                        'CI_Lower': lower,
                                        'CI_Upper': upper,
                                        'N': n
                                    })
                
                if correlation_pairs:
                    corr_plot_df = pd.DataFrame(correlation_pairs).sort_values('Correlation', ascending=True)
                    
                    # Create the correlation plot
                    fig_corr = go.Figure()
                    
                    # Add confidence intervals as lines
                    for idx, row in corr_plot_df.iterrows():
                        fig_corr.add_trace(go.Scatter(
                            x=[row['CI_Lower'], row['CI_Upper']],
                            y=[row['Pair'], row['Pair']],
                            mode='lines',
                            line=dict(color='#7f8c8d', width=3),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                    
                    # Add correlation points
                    fig_corr.add_trace(go.Scatter(
                        x=corr_plot_df['Correlation'],
                        y=corr_plot_df['Pair'],
                        mode='markers',
                        marker=dict(
                            size=10,
                            color=corr_plot_df['Correlation'],
                            colorscale='RdBu',
                            cmin=-1,
                            cmax=1,
                            showscale=True,
                            colorbar=dict(
                                title="r",
                                thickness=15,
                                len=0.7
                            ),
                            line=dict(width=1, color='white')
                        ),
                        text=corr_plot_df.apply(lambda row: f"r = {row['Correlation']:.3f}, p = {row['P_Value']:.3f}", axis=1),
                        hovertemplate='<b>%{y}</b><br>Correlation: %{x:.3f}<br>p-value: %{customdata[0]:.4f}<br>N = %{customdata[1]}<extra></extra>',
                        customdata=corr_plot_df[['P_Value', 'N']].values,
                        showlegend=False
                    ))
                    
                    # Update layout
                    fig_corr.update_layout(
                        xaxis=dict(
                            title="Correlation Coefficient (r)",
                            title_font=dict(size=14, color='#000000', family='Arial, sans-serif'),
                            range=[-0.1, 1.0],
                            showgrid=True,
                            gridcolor='rgba(200, 200, 200, 0.5)',
                            zeroline=True,
                            zerolinecolor='#424242',
                            zerolinewidth=2,
                            tickfont=dict(size=12, color='#000000', family='Arial, sans-serif')
                        ),
                        yaxis=dict(
                            title="",
                            showgrid=False,
                            tickfont=dict(size=11, color='#000000', family='Arial, sans-serif')
                        ),
                        height=max(400, len(correlation_pairs) * 30),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(l=280, r=50, t=20, b=50),
                        hovermode='closest',
                        font=dict(size=12, color='#000000', family='Arial, sans-serif')
                    )
                    
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Pairs Shown", len(correlation_pairs))
                    with col2:
                        st.metric("Avg Correlation", f"{corr_plot_df['Correlation'].mean():.3f}")
                    with col3:
                        st.metric("Max Correlation", f"{corr_plot_df['Correlation'].max():.3f}")
                    
                else:
                    st.info(f"No significant correlations found with p < {max_p_value}. Try increasing the p-value threshold.")
            else:
                st.warning("No data available for correlation analysis with current filters.")
    else:
        # No edges in network - show helpful message
        st.warning(f"⚠️ No network connections found for **{selected_metric}** metric.")
        st.info(f"""
        **Possible reasons:**
        - Miss threshold ({miss_threshold}) may be too low or too high - adjust the slider in the sidebar
        - Minimum co-misses threshold ({min_misses}) may be too high - try lowering it to 1
        - Not enough students struggling with these {len(centrality_elements)} elements together
        - Try selecting "Overall" to see all {len(ELEMENTS)} elements
        
        **Tip:** Lower the miss threshold to {miss_threshold - 0.5:.1f} or set min co-misses to 1 to see more connections.
        """)
    
    st.markdown("---")
    
    # Student Lookup section
    
    # Student Lookup section
    st.markdown("#### Student Lookup")
    
    # Map the text input to actual student IDs
    # Check if user clicked View button or session state has student lookup
    show_lookup = st.session_state.get('show_student_lookup', False)
    
    # Use the sidebar filter for student lookup - convert A123456 format to internal student ID
    if lookup_student_id and lookup_student_id.strip() != "":
        # Try to find matching student or use first student as demo
        matched_student = None
        
        # Check if it matches our student format (S01, S02, etc.)
        if lookup_student_id in students:
            matched_student = lookup_student_id
        else:
            # Use first student as demo for any input
            matched_student = students[0] if len(students) > 0 else None
        
        if matched_student:
            student_data = df[df['student_id'] == matched_student]
        else:
            student_data = pd.DataFrame()
        
        if not student_data.empty:
            # Determine cohort
            cohort_label = "Undergraduate" if matched_student in students[:len(students)//2] else "Graduate"
            num_attempts = len(student_data)
            latest_attempt = student_data['attempt'].max()
            latest_score = student_data[student_data['attempt'] == latest_attempt][ELEMENTS].mean().mean()
            
            # Create preview card with light background
            st.markdown(f"""
            <div style="background-color: #E8EAF6; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="margin: 0; color: #1A237E;">Student Lookup — Preview</h3>
                <p style="margin: 5px 0; color: #5C6BC0;">
                    <strong>Student ID:</strong> {lookup_student_id if lookup_student_id else 'A123456'} &nbsp;&nbsp;•&nbsp;&nbsp; 
                    <strong>Cohort:</strong> {cohort_label} &nbsp;&nbsp;•&nbsp;&nbsp; 
                    <strong>Attempts:</strong> {num_attempts} &nbsp;&nbsp;•&nbsp;&nbsp; 
                    <strong>Latest:</strong> {int(latest_score)}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Attempts trend (Overall score)
                st.markdown("**Attempts trend (Overall score)**")
                
                # Create trend chart - properly aggregate scores per attempt
                attempts_list = []
                for attempt_num in student_data['attempt'].unique():
                    attempt_rows = student_data[student_data['attempt'] == attempt_num]
                    avg_score = attempt_rows[ELEMENTS].mean().mean()
                    attempts_list.append({'Attempt': attempt_num, 'Score': avg_score})
                
                attempts_data = pd.DataFrame(attempts_list).sort_values('Attempt')
                attempts_data['Delta'] = attempts_data['Score'].diff()
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=attempts_data['Attempt'],
                    y=attempts_data['Score'],
                    mode='lines+markers',
                    line=dict(color='#2196F3', width=3),
                    marker=dict(size=8, color='#2196F3'),
                    hovertemplate='Attempt %{x}<br>Score: %{y:.1f}<extra></extra>'
                ))
                
                fig_trend.update_layout(
                    height=200,
                    margin=dict(l=40, r=20, t=20, b=40),
                    xaxis=dict(
                        title='',
                        showgrid=True,
                        gridcolor='#E5E7E9',
                        dtick=1
                    ),
                    yaxis=dict(
                        title='',
                        showgrid=True,
                        gridcolor='#E5E7E9',
                        range=[0, 4]
                    ),
                    plot_bgcolor='white'
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Attempts summary table
                st.markdown("**Attempts summary**")
                
                # Create realistic timestamps
                import datetime
                base_date = datetime.datetime(2024, 9, 20, 9, 10)
                timestamps = []
                for i in range(len(attempts_data)):
                    timestamp = base_date + datetime.timedelta(days=i*2, hours=i*4, minutes=i*48)
                    timestamps.append(timestamp.strftime("%m/%d %H:%M"))
                
                # Format delta properly - handle NaN for first attempt
                delta_formatted = []
                for i, delta_val in enumerate(attempts_data['Delta']):
                    if pd.isna(delta_val) or i == 0:
                        delta_formatted.append('—')
                    elif delta_val > 0:
                        delta_formatted.append(f'+{int(delta_val)}')
                    elif delta_val == 0:
                        delta_formatted.append('+0')
                    else:
                        delta_formatted.append(f'{int(delta_val)}')
                
                summary_df = pd.DataFrame({
                    'Attempt': attempts_data['Attempt'].astype(int),
                    'Score': attempts_data['Score'].astype(int),
                    'Δ vs prev': delta_formatted,
                    'Timestamp': timestamps
                })
                
                st.dataframe(summary_df, hide_index=True, use_container_width=True, height=210)
            
            with col2:
                # Per-domain scores (latest attempt)
                st.markdown("**Per-domain scores (latest attempt)**")
                
                latest_data = student_data[student_data['attempt'] == latest_attempt]
                
                # Map to display categories
                domain_mapping = {
                    'Communication': ['PI_01_Element_A', 'PI_01_Element_B'],
                    'Clinical Reasoning': ['PI_01_Element_C', 'PI_01_Element_D', 'PI_02_Element_A'],
                    'Safety': ['PI_02_Element_B', 'PI_02_Element_C', 'PI_02_Element_D']
                }
                
                domain_scores = []
                for domain, elements in domain_mapping.items():
                    available_elements = [e for e in elements if e in ELEMENTS]
                    if available_elements:
                        score = latest_data[available_elements].mean().mean()
                        domain_scores.append({'Domain': domain, 'Score': round(score, 1)})
                
                # Create horizontal bar chart
                if domain_scores:
                    domain_df = pd.DataFrame(domain_scores)
                    
                    fig_domains = go.Figure()
                    
                    # Add bars with different colors
                    colors = ['#42A5F5', '#66BB6A', '#FFA726']
                    for i, row in domain_df.iterrows():
                        fig_domains.add_trace(go.Bar(
                            y=[row['Domain']],
                            x=[row['Score']],
                            orientation='h',
                            marker=dict(color=colors[i % len(colors)]),
                            text=str(row['Score']),
                            textposition='outside',
                            hovertemplate=f"<b>{row['Domain']}</b><br>Score: {row['Score']}<extra></extra>",
                            showlegend=False
                        ))
                    
                    fig_domains.update_layout(
                        height=150,
                        margin=dict(l=10, r=60, t=10, b=10),
                        xaxis=dict(
                            title='Score (0-4 rubric scale)',
                            range=[0, 4],
                            showgrid=True,
                            gridcolor='#E5E7E9'
                        ),
                        yaxis=dict(showgrid=False),
                        plot_bgcolor='white',
                        bargap=0.3
                    )
                    st.plotly_chart(fig_domains, use_container_width=True)
                
                # Qualitative excerpt
                st.markdown("**Qualitative excerpt (AI)**")
                
                qualitative_text = """• Used patient-friendly language; clear explanation
• Follow-up questions were timely; add teach-back
• Consider ranking differential by likelihood next time"""
                
                st.markdown(qualitative_text)
                st.caption("*AI-generated from simulation transcripts & rubric scoring*")
        else:
            st.error(f"No data found for {lookup_student_id}")
    else:
        st.info("Select a student from the sidebar to view their detailed performance")

st.caption('**Interactive demo**: Adjust controls in the sidebar to regenerate data and see updated visuals.')
