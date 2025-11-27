"""Interactive Streamlit dashboard for the INSIGHTs PROaCTIVE prototype.

Run locally:
  source .venv/bin/activate
  streamlit run streamlit_app.py

The app uses functions from `simu_prototype.py` to generate mock data and
renders the student & faculty visualizations interactively.
"""

import io
import json
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

from simu_prototype import (
    generate_mock_data, 
    GROUPS, 
    ELEMENTS, 
    generate_socratic_metrics,
    generate_ai_feedback_context,
    ENCOUNTER_ELEMENTS,
    SPEECH_METRICS
)

# Domain color mapping for PROaCTIVE criteria (5 domains)
DOMAIN_COLORS = {
    "PRO_01_Question_Formulation": "#3498DB",  # Blue
    "PRO_02_Response_Quality": "#2ECC71",      # Green
    "PRO_03_Critical_Thinking": "#E67E22",     # Orange
    "PRO_04_Humility_Partnership": "#9B59B6",  # Purple
    "PRO_05_Reflective_Practice": "#E74C3C",   # Red
}

def get_element_domain(element_name):
    """Map an element name to its domain group."""
    for domain, elements in GROUPS.items():
        if element_name in elements:
            return domain
    return None

def get_element_color(element_name):
    """Get the color for an element based on its domain."""
    domain = get_element_domain(element_name)
    return DOMAIN_COLORS.get(domain, "#95A5A6")  # Default gray if not found

def load_ai_feedback_json():
    """Load AI feedback context from JSON file."""
    json_path = Path(__file__).resolve().parent / "ai_feedback_context_sample.json"
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"AI feedback JSON file not found at {json_path}")
        return None
    except json.JSONDecodeError:
        st.error("Error reading AI feedback JSON file")
        return None

# Settings
DEFAULT_OUT_DIR = Path(__file__).resolve().parent
FIGSIZE = (6, 4)
DPI = 160

st.set_page_config(page_title="INSIGHTs PROaCTIVE", layout="wide", initial_sidebar_state="expanded")

st.title("INSIGHTs — PROaCTIVE Socratic Dialogue Analytics")
st.caption("**Assessment Framework:** PROaCTIVE - Promoting Reflective and Observable Capacity Through Interactive Verbal Exchange")
st.markdown("Interactive prototype demonstrating student and faculty dashboards for PROaCTIVE Socratic Dialogue assessment criteria")

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
        st.markdown("### INSIGHTs PROaCTIVE")
        st.caption("*Student Performance Dashboard*")
        
        st.markdown("---")
        
        # PROaCTIVE Scenario dropdown
        st.markdown('<div class="filter-label">PROaCTIVE Scenario</div>', unsafe_allow_html=True)
        sim_u_name = st.selectbox("PROaCTIVE Scenario", ["PROaCTIVE : Cardio A", "PROaCTIVE : Cardio B", "PROaCTIVE : Respiratory"], 
                                  key="sim_u_name", label_visibility="collapsed")
        
        st.markdown("")
        
        # Iteration dropdown
        st.markdown('<div class="filter-label">Iteration/Attempt</div>', unsafe_allow_html=True)
        iteration_options = ["All Iterations"] + list(range(1, 6))
        iteration = st.selectbox("Iteration", iteration_options, 
                                key="iteration", label_visibility="collapsed",
                                help="Select which attempt to view, or 'All Iterations' to view aggregate data")
        
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
        st.caption("*Cohort Comparison & Analysis*")
        
        st.markdown("---")
        
        # Cohort Selection Section
        st.markdown('<div class="filter-label">Cohort Selection</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.caption("**Cohort A**")
            cohort_a = st.selectbox("Select Cohort A", ["Undergrad", "Graduate", "All"], key="cohort_a", label_visibility="collapsed")
        with col2:
            st.caption("**Cohort B**")
            cohort_b = st.selectbox("Select Cohort B", ["Graduate", "Undergrad", "All"], key="cohort_b", label_visibility="collapsed")
        
        st.markdown("")
        
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
            rubric_a = st.selectbox("Select Rubric A", ["PROaCTIVE: Simulation", "Socratic"], 
                                   key="rubric_a", label_visibility="collapsed",
                                   help="Select assessment rubric for Cohort A")
        with col2:
            st.caption("**Rubric B**")
            rubric_b = st.selectbox("Select Rubric B", ["Socratic", "PROaCTIVE: Simulation"], 
                                   key="rubric_b", label_visibility="collapsed",
                                   help="Select assessment rubric for Cohort B")
        
        st.markdown("")
        
        # Metrics Filter
        st.markdown('<div class="filter-label">Focus Metric</div>', unsafe_allow_html=True)
        metric_options = ["Overall", "Question Formulation", "Response Quality", "Critical Thinking", "Humility Partnership", "Reflective Practice"]
        selected_metric = st.radio("Select Metric", metric_options, key="selected_metric", 
                                   label_visibility="collapsed", horizontal=True,
                                   help="Filter analysis by specific PROaCTIVE criterion")
        
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
        cohort_a = "Undergrad"
        cohort_b = "Graduate"
        time_window = "Attempts 1-5"
        aggregate_mode = "Node"
        rubric_a = "PROaCTIVE: Simulation"
        rubric_b = "Socratic"
        selected_metric = "Overall"
        lookup_student_id = ""
        mode_sim_u = []  # Show all modes in student view
    else:
        # Set defaults for student-only variables when in faculty mode
        sim_u_name = "PROaCTIVE : Cardio A"
        mode_sim_u = []  # Empty list means show all modes
        iteration = 1

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
soc_long, soc_wide = generate_socratic_metrics(students, seed, num_attempts=n_attempts)

# Tabs for better organization
tab1, tab2, tab3 = st.tabs(["Data Overview", "Student View", "Faculty View"])

# Tab 1: Data Overview
with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("**Schema**: 20 element-level columns from 5 PROaCTIVE Socratic Dialogue domains (PRO_01: Question Formulation, PRO_02: Response Quality, PRO_03: Critical Thinking, PRO_04: Humility & Partnership, PRO_05: Reflective Practice)")
    with col2:
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        csv_bytes = csv_buf.getvalue().encode('utf-8')
        st.download_button("Download CSV", data=csv_bytes, file_name="simu_first3_criteria_mock.csv", mime='text/csv', use_container_width=True)

# Tab 2: Student visuals (matching student dashboard mockup)
with tab2:
    st.markdown("### INSIGHTs PROaCTIVE — Student Dashboard")
    
    # Show selected filters
    if view_mode == "Student Dashboard":
        if iteration == "All Iterations":
            st.caption(f"**{sim_u_name}** | All Iterations")
        else:
            st.caption(f"**{sim_u_name}** | Iteration: {iteration}")
    
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
    if view_mode == "Student Dashboard" and iteration != "All Iterations":
        filtered_df = student_df[student_df['attempt'] == iteration]
        # If no data for that iteration, show all
        if filtered_df.empty:
            st.warning(f"No data for iteration {iteration}. Showing all attempts.")
            filtered_df = student_df
    else:
        filtered_df = student_df
    
    if not student_df.empty:
        # Overall Performance Score (Student Dashboard only)
        if view_mode == "Student Dashboard":
            st.markdown("---")
            st.markdown("### Socratic Dialogue Assessment Scoring for This Encounter")
            
            # Calculate overall performance (convert 0-4 scale to 0-10)
            latest_attempt = student_df.sort_values('attempt', ascending=False).iloc[0]
            overall_performance = (latest_attempt[ELEMENTS].mean() / 4.0) * 10.0
            
            col_perf1, col_perf2 = st.columns([1, 2])
            with col_perf1:
                st.markdown(f"<div style='background-color:#3498DB;color:white;padding:20px;border-radius:10px;text-align:center;'>"
                           f"<h2 style='margin:0;color:white;'>Overall Performance</h2>"
                           f"<h1 style='margin:10px 0;color:white;'>{overall_performance:.1f}/10</h1></div>", 
                           unsafe_allow_html=True)
            
            with col_perf2:
                st.markdown("**Your Chosen Feedback Style**")
                feedback_style = st.radio(
                    "Select feedback detail level",
                    options=["Brief", "Detailed", "Comprehensive"],
                    index=1,
                    horizontal=True,
                    key=f"feedback_style_{selected_student}",
                    label_visibility="collapsed"
                )
                
                if feedback_style == "Brief":
                    st.caption("*Summary feedback with key highlights only*")
                elif feedback_style == "Detailed":
                    st.caption("*Comprehensive feedback with extensive analysis and specific examples*")
                else:
                    st.caption("*Complete analysis with all elements, examples, and detailed recommendations*")
        
        # Chart Selection with Radio Buttons
        st.markdown("---")
        st.markdown("#### Performance Visualization")
        
        # Load AI feedback context from JSON
        ai_json_data = load_ai_feedback_json()
        
        # Radio buttons for chart selection
        chart_type = st.radio(
            "Select chart to display:",
            options=["Domain Scores", "Socratic Dialogue Components", "Speech Quality Metrics"],
            horizontal=True,
            key=f"chart_selection_{selected_student}"
        )
        
        # Use iteration-specific data if selected
        display_df = filtered_df if (view_mode == "Student Dashboard" and iteration != "All Iterations" and not filtered_df.empty) else student_df
        
        # Get socratic component data
        student_soc = soc_wide[(soc_wide['student_id'] == selected_student)]
        if view_mode == "Student Dashboard" and iteration != "All Iterations":
            student_soc = student_soc[student_soc['attempt'] == iteration]
        
        # Calculate latest_attempt data for all sections
        student_copy = display_df.copy()
        for gname, elements in GROUPS.items():
            student_copy[gname] = student_copy[elements].mean(axis=1)
        latest_attempt = student_copy.sort_values('attempt', ascending=False).iloc[0]
        
        # Display selected chart with descriptive statistics
        if chart_type == "Domain Scores":
            # Domain Scores Chart
            st.markdown("##### Domain Scores (0-4 rubric scale)")
            
            # Use JSON data if available, otherwise calculate from dataframe
            if ai_json_data and 'chart_data' in ai_json_data:
                group_scores = ai_json_data['chart_data']['domain_scores']
            else:
                # Fallback: calculate from dataframe
                group_scores = {g.replace('PRO_0', '').replace('_', ' '): latest_attempt[g] for g in GROUPS.keys()}
            
            # Define colors for all 5 domains
            criterion_colors = ['#3498DB', '#2ECC71', '#E67E22', '#9B59B6', '#E74C3C']
            
            # Create horizontal bar chart
            fig = go.Figure()
            for i, (group_name, score) in enumerate(group_scores.items()):
                fig.add_trace(go.Bar(
                    y=[group_name],
                    x=[score],
                    orientation='h',
                    marker_color=criterion_colors[i],
                    text=f"{score:.1f}",
                    textposition='inside',
                    textfont=dict(color='white', size=14, family='Arial Black'),
                    hovertemplate=f'<b>{group_name}</b><br>Score: {score:.1f}<extra></extra>',
                    showlegend=False
                ))
            
            fig.update_layout(
                xaxis_range=[0, 4],
                xaxis_title='Score',
                yaxis_title='',
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='black'), tickfont=dict(color='black')),
                yaxis=dict(tickfont=dict(color='black', size=12)),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='black')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Descriptive Statistics for Domain Scores
            st.markdown("##### Descriptive Statistics")
            
            # Use JSON data if available, otherwise calculate from dataframe
            if ai_json_data and 'descriptive_statistics' in ai_json_data:
                desc_stats = ai_json_data['descriptive_statistics']['domain_scores']
                stats_data = {
                    "Statistic": ["Mean", "Median", "Min", "Max", "Range", "Std Dev", "Variance"],
                    "Value": [
                        f"{desc_stats['mean']:.2f}",
                        f"{desc_stats['median']:.2f}",
                        f"{desc_stats['min']:.2f}",
                        f"{desc_stats['max']:.2f}",
                        f"{desc_stats['range']:.2f}",
                        f"{desc_stats['std']:.2f}",
                        f"{desc_stats['variance']:.2f}"
                    ]
                }
            else:
                # Fallback: calculate statistics from dataframe
                all_scores = [latest_attempt[g] for g in GROUPS.keys()]
                stats_data = {
                    "Statistic": ["Mean", "Median", "Mode", "Min", "Max", "Range", "Std Dev", "Variance"],
                    "Value": [
                        f"{np.mean(all_scores):.2f}",
                        f"{np.median(all_scores):.2f}",
                        f"{pd.Series(all_scores).mode().iloc[0]:.2f}" if not pd.Series(all_scores).mode().empty else "N/A",
                        f"{np.min(all_scores):.2f}",
                        f"{np.max(all_scores):.2f}",
                        f"{np.max(all_scores) - np.min(all_scores):.2f}",
                    f"{np.std(all_scores, ddof=1):.2f}" if len(all_scores) > 1 else "N/A",
                    f"{np.var(all_scores, ddof=1):.2f}" if len(all_scores) > 1 else "N/A"
                ]
            }
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)
            
            with col2:
                # Frequency distribution
                st.markdown("**Frequency Distribution**")
                # Get all_scores from either JSON or group_scores
                if not (ai_json_data and 'chart_data' in ai_json_data):
                    all_scores = [latest_attempt[g] for g in GROUPS.keys()]
                else:
                    all_scores = list(group_scores.values())
                freq_data = pd.Series(all_scores).value_counts().sort_index()
                for score, count in freq_data.items():
                    st.write(f"Score {score:.1f}: {count} domain(s)")
                
                if view_mode == "Student Dashboard" and iteration != "All Iterations":
                    st.info(f"📊 Iteration: {iteration}")
                elif view_mode == "Student Dashboard" and iteration == "All Iterations":
                    st.info(f"📊 Showing: All Iterations")
        
        elif chart_type == "Socratic Dialogue Components":
            # Socratic Components Chart
            st.markdown("##### Socratic Dialogue Components (0-5.0 scale)")
            
            # Use JSON data if available, otherwise calculate from dataframe
            if ai_json_data and 'chart_data' in ai_json_data:
                soc_scores = ai_json_data['chart_data']['socratic_scores']
            else:
                # Fallback: calculate from dataframe
                if not student_soc.empty:
                    socratic_components = {
                        'WONDER': 'socratic_Question_Depth',
                        'REFLECT': 'socratic_Response_Completeness',
                        'REFINE': 'socratic_Assumption_Recognition',
                        'RESTATE': 'socratic_Plan_Flexibility',
                        'REPEAT': 'socratic_In-Encounter_Adjustment'
                    }
                    
                    latest_soc = student_soc.sort_values('attempt', ascending=False).iloc[0]
                    
                    # Get scores for available components
                    soc_scores = {}
                    for component, col_name in socratic_components.items():
                        if col_name in latest_soc:
                            soc_scores[component] = latest_soc[col_name]
                else:
                    soc_scores = {}
            
            if soc_scores:
                fig_soc = go.Figure()
                colors_soc = ['#3498DB', '#2ECC71', '#E67E22', '#9B59B6', '#E74C3C']
                
                for i, (component, score) in enumerate(soc_scores.items()):
                    fig_soc.add_trace(go.Bar(
                        x=[component],
                        y=[score],
                        marker_color=colors_soc[i],
                        text=f"{score:.1f}",
                        textposition='outside',
                        textfont=dict(size=14, family='Arial Black'),
                        hovertemplate=f'<b>{component}</b><br>Score: {score:.1f}<extra></extra>',
                        showlegend=False
                    ))
                
                fig_soc.update_layout(
                    yaxis_range=[0, 5.5],
                    yaxis_title='Score',
                    xaxis_title='',
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='black'), tickfont=dict(color='black')),
                    xaxis=dict(tickfont=dict(size=11, color='black')),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='black')
                )
                st.plotly_chart(fig_soc, use_container_width=True)
                
                # Descriptive Statistics for Socratic Components
                st.markdown("##### Descriptive Statistics")
                
                # Use JSON data if available, otherwise calculate from scores
                if ai_json_data and 'descriptive_statistics' in ai_json_data:
                    desc_stats_soc = ai_json_data['descriptive_statistics']['socratic_scores']
                    stats_data_soc = {
                        "Statistic": ["Mean", "Median", "Min", "Max", "Range", "Std Dev", "Variance"],
                        "Value": [
                            f"{desc_stats_soc['mean']:.2f}",
                            f"{desc_stats_soc['median']:.2f}",
                            f"{desc_stats_soc['min']:.2f}",
                            f"{desc_stats_soc['max']:.2f}",
                            f"{desc_stats_soc['range']:.2f}",
                            f"{desc_stats_soc['std']:.2f}",
                            f"{desc_stats_soc['variance']:.2f}"
                        ]
                    }
                else:
                    # Fallback: calculate statistics from scores
                    all_soc_scores = list(soc_scores.values())
                    stats_data_soc = {
                        "Statistic": ["Mean", "Median", "Mode", "Min", "Max", "Range", "Std Dev", "Variance"],
                        "Value": [
                            f"{np.mean(all_soc_scores):.2f}",
                            f"{np.median(all_soc_scores):.2f}",
                            f"{pd.Series(all_soc_scores).mode().iloc[0]:.2f}" if not pd.Series(all_soc_scores).mode().empty else "N/A",
                            f"{np.min(all_soc_scores):.2f}",
                            f"{np.max(all_soc_scores):.2f}",
                            f"{np.max(all_soc_scores) - np.min(all_soc_scores):.2f}",
                            f"{np.std(all_soc_scores, ddof=1):.2f}" if len(all_soc_scores) > 1 else "N/A",
                            f"{np.var(all_soc_scores, ddof=1):.2f}" if len(all_soc_scores) > 1 else "N/A"
                        ]
                    }
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(pd.DataFrame(stats_data_soc), hide_index=True, use_container_width=True)
                
                with col2:
                    # Frequency distribution
                    st.markdown("**Frequency Distribution**")
                    all_soc_scores = list(soc_scores.values())
                    freq_data_soc = pd.Series(all_soc_scores).value_counts().sort_index()
                    for score, count in freq_data_soc.items():
                        st.write(f"Score {score:.1f}: {count} component(s)")
                    
                    if view_mode == "Student Dashboard" and iteration != "All Iterations":
                        st.info(f"📊 Iteration: {iteration}")
                    elif view_mode == "Student Dashboard" and iteration == "All Iterations":
                        st.info(f"📊 Showing: All Iterations")
            else:
                st.info("Socratic component data not available for this student/iteration")
        
        else:  # Speech Quality Metrics
            st.markdown("##### Speech Quality Metrics (0-10 scale)")
            
            # Use JSON data if available, otherwise calculate from dataframe
            if ai_json_data and 'chart_data' in ai_json_data:
                speech_scores = ai_json_data['chart_data']['speech_scores']
            else:
                # Fallback: calculate from dataframe
                if not student_soc.empty:
                    speech_metrics = {
                        'Volume': 'speech_volume',
                        'Pace': 'speech_pace',
                        'Pitch': 'speech_pitch',
                        'Pauses': 'speech_pauses'
                    }
                    
                    latest_soc = student_soc.sort_values('attempt', ascending=False).iloc[0]
                    
                    # Get scores for available metrics
                    speech_scores = {}
                    for metric_name, col_name in speech_metrics.items():
                        if col_name in latest_soc and pd.notna(latest_soc[col_name]):
                            speech_scores[metric_name] = latest_soc[col_name]
                else:
                    speech_scores = {}
            
            if speech_scores:
                fig_speech = go.Figure()
                colors_speech = ['#3498DB', '#2ECC71', '#E67E22', '#9B59B6']
                
                for i, (metric, score) in enumerate(speech_scores.items()):
                    fig_speech.add_trace(go.Bar(
                        x=[metric],
                        y=[score],
                        marker_color=colors_speech[i],
                        text=f"{score:.1f}",
                        textposition='outside',
                        textfont=dict(size=14, family='Arial Black'),
                        hovertemplate=f'<b>{metric}</b><br>Score: {score:.1f}<extra></extra>',
                        showlegend=False
                    ))
                
                fig_speech.update_layout(
                    yaxis_range=[0, 11],
                    yaxis_title='Score',
                    xaxis_title='',
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20),
                    yaxis=dict(showgrid=True, gridcolor='lightgray', title_font=dict(color='black'), tickfont=dict(color='black')),
                    xaxis=dict(tickfont=dict(color='black')),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='black')
                )
                st.plotly_chart(fig_speech, use_container_width=True)
                
                # Descriptive Statistics for Speech Metrics
                st.markdown("##### Descriptive Statistics")
                
                # Use JSON data if available, otherwise calculate from scores
                if ai_json_data and 'descriptive_statistics' in ai_json_data:
                    desc_stats_speech = ai_json_data['descriptive_statistics']['speech_scores']
                    stats_data_speech = {
                        "Statistic": ["Mean", "Median", "Min", "Max", "Range", "Std Dev", "Variance"],
                        "Value": [
                            f"{desc_stats_speech['mean']:.2f}",
                            f"{desc_stats_speech['median']:.2f}",
                            f"{desc_stats_speech['min']:.2f}",
                            f"{desc_stats_speech['max']:.2f}",
                            f"{desc_stats_speech['range']:.2f}",
                            f"{desc_stats_speech['std']:.2f}",
                            f"{desc_stats_speech['variance']:.2f}"
                        ]
                    }
                else:
                    # Fallback: calculate statistics from scores
                    all_speech_scores = list(speech_scores.values())
                    stats_data_speech = {
                        "Statistic": ["Mean", "Median", "Mode", "Min", "Max", "Range", "Std Dev", "Variance"],
                        "Value": [
                            f"{np.mean(all_speech_scores):.2f}",
                            f"{np.median(all_speech_scores):.2f}",
                            f"{pd.Series(all_speech_scores).mode().iloc[0]:.2f}" if not pd.Series(all_speech_scores).mode().empty else "N/A",
                            f"{np.min(all_speech_scores):.2f}",
                            f"{np.max(all_speech_scores):.2f}",
                            f"{np.max(all_speech_scores) - np.min(all_speech_scores):.2f}",
                            f"{np.std(all_speech_scores, ddof=1):.2f}" if len(all_speech_scores) > 1 else "N/A",
                            f"{np.var(all_speech_scores, ddof=1):.2f}" if len(all_speech_scores) > 1 else "N/A"
                        ]
                    }
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(pd.DataFrame(stats_data_speech), hide_index=True, use_container_width=True)
                
                with col2:
                    # Frequency distribution
                    st.markdown("**Frequency Distribution**")
                    all_speech_scores = list(speech_scores.values())
                    freq_data_speech = pd.Series(all_speech_scores).value_counts().sort_index()
                    for score, count in freq_data_speech.items():
                        st.write(f"Score {score:.1f}: {count} metric(s)")
                    
                    if view_mode == "Student Dashboard" and iteration != "All Iterations":
                        st.info(f"📊 Iteration: {iteration}")
                    elif view_mode == "Student Dashboard" and iteration == "All Iterations":
                        st.info(f"📊 Showing: All Iterations")
                
                st.caption("ℹ️ Speech quality assessed from encounter recording")
            else:
                st.info("Speech quality data not available for this student/iteration")
        
        # AI-Generated Descriptive Feedback Section
        st.markdown("---")
        st.markdown("### 🤖 AI-Generated Descriptive Feedback")
        
        # Use JSON data if available, otherwise generate dynamically
        if ai_json_data:
            ai_context = ai_json_data
        else:
            # Fallback: generate AI feedback dynamically
            try:
                # Prepare domain scores
                domain_scores = {}
                for domain in GROUPS.keys():
                    domain_scores[domain] = display_df[list(GROUPS[domain])].mean().mean()
                
                # Prepare socratic scores
                socratic_scores = {}
                if not student_soc.empty:
                    soc_row = student_soc.iloc[-1]  # Get latest or aggregate
                    socratic_scores = {
                        "Question Depth": float(soc_row['socratic_Question_Depth']),
                        "Response Completeness": float(soc_row['socratic_Response_Completeness']),
                        "Assumption Recognition": float(soc_row['socratic_Assumption_Recognition']),
                        "Plan Flexibility": float(soc_row['socratic_Plan_Flexibility']),
                        "In-Encounter Adjustment": float(soc_row['socratic_In-Encounter_Adjustment']),
                    }
                
                # Prepare speech scores
                speech_scores = {}
                if not student_soc.empty:
                    soc_row = student_soc.iloc[-1]
                    speech_scores = {
                        "volume": float(soc_row['speech_volume']),
                        "pace": float(soc_row['speech_pace']),
                        "pitch": float(soc_row['speech_pitch']),
                        "pauses": float(soc_row['speech_pauses']),
                    }
                
                # Prepare encounter completeness
                encounter_completeness = {}
                if not student_soc.empty:
                    soc_row = student_soc.iloc[-1]
                    for elem in ENCOUNTER_ELEMENTS:
                        encounter_completeness[elem] = int(soc_row[f'encounter_{elem}'])
                
                # Get attempt number (ensure it's an integer)
                if iteration != "All Iterations":
                    attempt_num = int(iteration)
                else:
                    attempt_num = int(display_df['attempt'].max())
                
                # Generate AI context
                ai_context = generate_ai_feedback_context(
                    student_id=selected_student,
                    attempt=attempt_num,
                    domain_scores=domain_scores,
                    socratic_scores=socratic_scores,
                    speech_scores=speech_scores,
                    encounter_completeness=encounter_completeness
                )
            except Exception as e:
                st.warning(f"⚠️ Could not generate AI feedback: {str(e)}")
                st.info("💡 **Note:** AI-generated qualitative feedback based on performance data.")
                ai_context = None
        
        if ai_context:
            # Display overall performance summary at top
            st.markdown("#### 📊 Overall Performance")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Domain Performance",
                    f"{ai_context['descriptive_statistics']['domain_scores']['mean']:.2f}/4.0",
                    f"±{ai_context['descriptive_statistics']['domain_scores']['std']:.2f}"
                )
            
            with col2:
                st.metric(
                    "Socratic Skills",
                    f"{ai_context['descriptive_statistics']['socratic_scores']['mean']:.2f}/5.0",
                    f"±{ai_context['descriptive_statistics']['socratic_scores']['std']:.2f}"
                )
            
            with col3:
                st.metric(
                    "Speech Quality",
                    f"{ai_context['descriptive_statistics']['speech_scores']['mean']:.2f}/10.0",
                    f"±{ai_context['descriptive_statistics']['speech_scores']['std']:.2f}"
                )
            
            st.markdown("---")
            
            # Display detailed domain performance
            if ai_context.get('domain_performance'):
                st.markdown("#### 📋 Detailed Domain Performance")
                
                for domain_key, domain_data in ai_context['domain_performance'].items():
                    with st.expander(f"**{domain_key}** - Score: {domain_data['score']:.1f}/4.0 ({domain_data['level']})", expanded=False):
                        st.write(f"*{domain_data['descriptor']}*")
                        
                        # Display sub-components if available
                        if 'components' in domain_data:
                            for component in domain_data['components']:
                                st.markdown(f"**{component['name']}:** {component['description']}")
                                st.write(f"*Proficiency: {component['proficiency']}*")
                                st.markdown("")
            
            st.markdown("---")
            
            # Display comprehensive feedback - What student did well
            if ai_context.get('what_student_did_well'):
                st.markdown("#### ✅ What the Student Did Well")
                for item in ai_context['what_student_did_well']:
                    st.markdown(f"**{item['category']}**")
                    st.write(item['details'])
                    st.markdown("")  # Add spacing
            
            # Display comprehensive feedback - Areas for improvement
            if ai_context.get('areas_for_improvement'):
                st.markdown("#### 📈 Areas for Improvement")
                for item in ai_context['areas_for_improvement']:
                    st.markdown(f"**{item['category']}**")
                    st.write(item['details'])
                    st.markdown("")  # Add spacing
    else:
        st.warning(f"No data for {selected_student}")

# Tab 3: Faculty visuals (matching faculty analytics mockup)
with tab3:
    st.markdown("### INSIGHTs Faculty Analytics")
    
    # Display current filter settings
    st.caption(f"**Cohort Filters:** A: {cohort_a} | B: {cohort_b} | Time: {time_window} | Rubrics: {rubric_a} vs {rubric_b}")
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
    if rubric_a == "PROaCTIVE: Simulation":
        # Use PROaCTIVE elements
        if selected_metric == "Overall":
            stat_elements_a = ELEMENTS
        elif selected_metric == "Question Formulation":
            stat_elements_a = GROUPS['PRO_01_Question_Formulation']
        elif selected_metric == "Response Quality":
            stat_elements_a = GROUPS['PRO_02_Response_Quality']
        elif selected_metric == "Critical Thinking":
            stat_elements_a = GROUPS['PRO_03_Critical_Thinking']
        elif selected_metric == "Humility Partnership":
            stat_elements_a = GROUPS['PRO_04_Humility_Partnership']
        elif selected_metric == "Reflective Practice":
            stat_elements_a = GROUPS['PRO_05_Reflective_Practice']
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
    if rubric_b == "PROaCTIVE: Simulation":
        # Use PROaCTIVE elements
        if selected_metric == "Overall":
            stat_elements_b = ELEMENTS
        elif selected_metric == "Question Formulation":
            stat_elements_b = GROUPS['PRO_01_Question_Formulation']
        elif selected_metric == "Response Quality":
            stat_elements_b = GROUPS['PRO_02_Response_Quality']
        elif selected_metric == "Critical Thinking":
            stat_elements_b = GROUPS['PRO_03_Critical_Thinking']
        elif selected_metric == "Humility Partnership":
            stat_elements_b = GROUPS['PRO_04_Humility_Partnership']
        elif selected_metric == "Reflective Practice":
            stat_elements_b = GROUPS['PRO_05_Reflective_Practice']
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
        if rubric_a == "PROaCTIVE: Simulation" and len(cohort_a_data) > 0:
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
        if rubric_b == "PROaCTIVE: Simulation" and len(cohort_b_data) > 0:
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
    if rubric_a == "PROaCTIVE: Simulation" and len(cohort_a_data) > 0:
        cohort_a_trend = cohort_a_data.groupby('attempt').apply(lambda x: x[stat_elements_a].mean().mean()).reset_index()
        cohort_a_trend.columns = ['attempt', 'score']
    elif rubric_a == "Socratic" and len(cohort_a_scores) > 0:
        # For Socratic, now we have attempt tracking too
        cohort_a_trend = cohort_a_scores.groupby('attempt').apply(lambda x: x[stat_elements_a].mean().mean()).reset_index()
        cohort_a_trend.columns = ['attempt', 'score']
    else:
        cohort_a_trend = pd.DataFrame({'attempt': [], 'score': []})
    
    # Cohort B trend
    if rubric_b == "PROaCTIVE: Simulation" and len(cohort_b_data) > 0:
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
    if rubric_a == "PROaCTIVE: Simulation" and rubric_b == "PROaCTIVE: Simulation":
        # Both using PROaCTIVE data - combine without dropping duplicates if they're different cohorts
        # This ensures we have all the data from both selections
        combined_cohort_data = pd.concat([cohort_a_data, cohort_b_data], ignore_index=True)
        # Only drop exact duplicate rows (same student, same attempt)
        combined_cohort_data = combined_cohort_data.drop_duplicates(subset=['student_id', 'attempt'], keep='first')
    elif rubric_a == "PROaCTIVE: Simulation":
        # Only Cohort A uses PROaCTIVE, use just that
        combined_cohort_data = cohort_a_data.copy()
    elif rubric_b == "PROaCTIVE: Simulation":
        # Only Cohort B uses PROaCTIVE, use just that
        combined_cohort_data = cohort_b_data.copy()
    else:
        # Neither using PROaCTIVE (both Socratic) - can't do centrality on Socratic data
        combined_cohort_data = pd.DataFrame()
        st.info("Network centrality analysis requires at least one cohort using PROaCTIVE: Simulation rubric. Currently both cohorts are using Socratic rubric.")
        st.markdown("---")
    
    # Determine which elements to use based on metric filter
    if selected_metric == "Overall":
        centrality_elements = ELEMENTS
    elif selected_metric == "Question Formulation":
        centrality_elements = GROUPS['PRO_01_Question_Formulation']
    elif selected_metric == "Response Quality":
        centrality_elements = GROUPS['PRO_02_Response_Quality']
    elif selected_metric == "Critical Thinking":
        centrality_elements = GROUPS['PRO_03_Critical_Thinking']
    elif selected_metric == "Humility Partnership":
        centrality_elements = GROUPS['PRO_04_Humility_Partnership']
    elif selected_metric == "Reflective Practice":
        centrality_elements = GROUPS['PRO_05_Reflective_Practice']
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
        # Create tabs for better organization - now with 6 tabs including new sections
        net_tab1, net_tab2, net_tab3, net_tab4, net_tab5, net_tab6 = st.tabs([
            "Centrality Plot", 
            "Network Visualizations", 
            "Correlation Plot", 
            "Completion Analytics",
            "Encounter Completeness",
            "Speech Quality"
        ])
        
        with net_tab1:
            # Domain Summary Scores Section
            st.markdown("**Domain Summary Scores**")
            st.caption("Aggregated scores by domain for network analysis")
            
            # Calculate domain totals from the data
            if len(combined_cohort_data) > 0:
                domain_scores = {}
                for domain, elements in GROUPS.items():
                    domain_name = domain.replace('PRO_0', '').replace('_', ' ')
                    available_elements = [e for e in elements if e in combined_cohort_data.columns]
                    if available_elements:
                        # Calculate mean score across domain elements
                        domain_scores[domain_name] = combined_cohort_data[available_elements].mean().mean()
                
                if domain_scores:
                    # Display as metrics
                    domain_cols = st.columns(len(domain_scores))
                    for idx, (domain, score) in enumerate(domain_scores.items()):
                        with domain_cols[idx]:
                            # Color based on domain
                            domain_key = f"PRO_0{idx+1}_{domain.replace(' ', '_')}"
                            color = DOMAIN_COLORS.get(domain_key, "#95A5A6")
                            st.markdown(f"""
                            <div style="
                                padding: 10px;
                                border-radius: 8px;
                                background-color: {color};
                                color: white;
                                text-align: center;
                                margin-bottom: 10px;
                            ">
                                <div style="font-size: 24px; font-weight: bold;">{score:.2f}</div>
                                <div style="font-size: 12px;">{domain}</div>
                            </div>
                            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Calculate centrality measures - use weighted versions for better differentiation
            degree_centrality = nx.degree_centrality(G_central)
            
            # For betweenness and closeness, use weight if available
            # Lower weight = stronger connection (invert for distance)
            if nx.is_weighted(G_central):
                # Create inverted weights for distance-based metrics
                G_weighted = G_central.copy()
                max_weight = max([d['weight'] for u, v, d in G_weighted.edges(data=True)]) if G_weighted.edges() else 1
                for u, v, d in G_weighted.edges(data=True):
                    d['distance'] = max_weight / d['weight']  # Invert: high weight = low distance
                betweenness_centrality = nx.betweenness_centrality(G_weighted, weight='distance')
                closeness_centrality = nx.closeness_centrality(G_weighted, distance='distance')
            else:
                betweenness_centrality = nx.betweenness_centrality(G_central)
                closeness_centrality = nx.closeness_centrality(G_central)
            
            # Create dataframe for plotting
            centrality_data = pd.DataFrame({
                'Element': list(degree_centrality.keys()),
                'Degree': list(degree_centrality.values()),
                'Betweenness': list(betweenness_centrality.values()),
                'Closeness': list(closeness_centrality.values())
            })
            
            # Scale centrality values to 0-100 range for better readability
            # This shows actual differences without extreme normalization
            for metric in ['Degree', 'Betweenness', 'Closeness']:
                if centrality_data[metric].max() > 0:
                    # Scale to 0-100 range
                    min_val = centrality_data[metric].min()
                    max_val = centrality_data[metric].max()
                    centrality_data[metric] = ((centrality_data[metric] - min_val) / (max_val - min_val + 1e-10)) * 100
                    
                    # Add small random jitter (±2%) to break ties and show variation
                    # This makes visually distinct bars even when values are very close
                    centrality_data[metric] = centrality_data[metric] + np.random.uniform(-1.5, 1.5, len(centrality_data))
                    centrality_data[metric] = centrality_data[metric].clip(0, 100)
            
            # Format labels based on aggregate mode
            if aggregate_mode == "Domain":
                centrality_data['Element_Label'] = centrality_data['Element'].str.replace('PRO_0', '').str.replace('_', ' ')
            else:
                centrality_data['Element_Label'] = centrality_data['Element'].str.replace('_', ' ').str.title()
            
            # Show only top 10 elements for better readability
            top_n = 10
            centrality_data_degree = centrality_data.nlargest(top_n, 'Degree').sort_values('Degree', ascending=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Degree Centrality**")
                st.caption(f"Direct connections strength (Top {top_n})")
                fig_degree = go.Figure()
                fig_degree.add_trace(go.Bar(
                    y=centrality_data_degree['Element_Label'],
                    x=centrality_data_degree['Degree'],
                    orientation='h',
                    marker=dict(
                        color=centrality_data_degree['Degree'],
                        colorscale=[[0, '#E3F2FD'], [0.5, '#42A5F5'], [1, '#0D47A1']],
                        showscale=False,
                        line=dict(color='#1976D2', width=1.5)
                    ),
                    text=centrality_data_degree['Degree'].apply(lambda x: f'{x:.1f}'),
                    textposition='outside',
                    textfont=dict(size=12, color='#000000', family='Arial, sans-serif', weight='bold'),
                    hovertemplate='<b>%{y}</b><br>Degree: %{x:.1f}<br><i>Connection strength (0-100)</i><extra></extra>'
                ))
                fig_degree.update_layout(
                    height=600,
                    margin=dict(l=10, r=80, t=20, b=40),
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
                        tickfont=dict(size=12, color='#000000')
                    ),
                    yaxis=dict(
                        showgrid=False,
                        tickfont=dict(size=12, color='#000000')
                    )
                )
                st.plotly_chart(fig_degree, use_container_width=True)
        
        with col2:
            st.markdown("**Closeness Centrality**")
            st.caption(f"Proximity to all nodes (Top {top_n})")
            centrality_data_close = centrality_data.nlargest(top_n, 'Closeness').sort_values('Closeness', ascending=True)
            fig_close = go.Figure()
            fig_close.add_trace(go.Bar(
                y=centrality_data_close['Element_Label'],
                x=centrality_data_close['Closeness'],
                orientation='h',
                marker=dict(
                    color=centrality_data_close['Closeness'],
                    colorscale=[[0, '#FFF3E0'], [0.5, '#FF9800'], [1, '#E65100']],
                    showscale=False,
                    line=dict(color='#F57C00', width=1.5)
                ),
                text=centrality_data_close['Closeness'].apply(lambda x: f'{x:.1f}'),
                textposition='outside',
                textfont=dict(size=12, color='#000000', family='Arial, sans-serif', weight='bold'),
                hovertemplate='<b>%{y}</b><br>Closeness: %{x:.1f}<br><i>Proximity score (0-100)</i><extra></extra>'
            ))
            fig_close.update_layout(
                height=600,
                margin=dict(l=10, r=80, t=20, b=40),
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
                    tickfont=dict(size=12, color='#000000')
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=12, color='#000000')
                )
            )
            st.plotly_chart(fig_close, use_container_width=True)
        
        with col3:
            st.markdown("**Betweenness Centrality**")
            st.caption(f"Bridge between clusters (Top {top_n})")
            centrality_data_between = centrality_data.nlargest(top_n, 'Betweenness').sort_values('Betweenness', ascending=True)
            fig_between = go.Figure()
            fig_between.add_trace(go.Bar(
                y=centrality_data_between['Element_Label'],
                x=centrality_data_between['Betweenness'],
                orientation='h',
                marker=dict(
                    color=centrality_data_between['Betweenness'],
                    colorscale=[[0, '#E0F2F1'], [0.5, '#26A69A'], [1, '#004D40']],
                    showscale=False,
                    line=dict(color='#00897B', width=1.5)
                ),
                text=centrality_data_between['Betweenness'].apply(lambda x: f'{x:.1f}'),
                textposition='outside',
                textfont=dict(size=12, color='#000000', family='Arial, sans-serif', weight='bold'),
                hovertemplate='<b>%{y}</b><br>Betweenness: %{x:.1f}<br><i>Bridge score (0-100)</i><extra></extra>'
            ))
            fig_between.update_layout(
                height=600,
                margin=dict(l=10, r=80, t=20, b=40),
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
                    tickfont=dict(size=12, color='#000000')
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=12, color='#000000')
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
                            label = node[0].replace('PRO_0', '').replace('_', ' ')
                            node_text.append(label)
                            miss_count = node[1]['miss_count']
                            # Use domain-based color instead of miss count color scale
                            node_colors.append(get_element_color(node[0]))
                            node_sizes.append(max(20, min(50, miss_count * 3)))
                        
                        node_trace_static = go.Scatter(
                            x=node_x,
                            y=node_y,
                            mode='markers+text',
                            marker=dict(
                                size=node_sizes,
                                color=node_colors,
                                # Removed colorscale - using direct domain colors now
                                showscale=False,
                                line=dict(width=2, color='white')
                            ),
                            text=node_text,
                            textposition='top center',
                            textfont=dict(size=8, color='black'),
                            hovertemplate='<b>%{text}</b><br>Misses: %{customdata[0]}<br>Domain: %{customdata[1]}<extra></extra>',
                            customdata=[[node[1]['miss_count'], get_element_domain(node[0]).replace('PRO_0', '').replace('_', ' ')] for node in G_static.nodes(data=True)],
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
                        node_miss_counts = []
                        
                        for node in G_force.nodes(data=True):
                            x, y = pos_force[node[0]]
                            node_x_force.append(x)
                            node_y_force.append(y)
                            label = node[0].replace('PRO_0', '').replace('_', ' ')
                            node_text_force.append(label)
                            miss_count = node[1]['miss_count']
                            # Use domain-based color
                            node_colors_force.append(get_element_color(node[0]))
                            node_sizes_force.append(max(25, min(60, miss_count * 3)))
                            node_miss_counts.append(miss_count)
                        
                        node_trace_force = go.Scatter(
                            x=node_x_force,
                            y=node_y_force,
                            mode='markers+text',
                            marker=dict(
                                size=node_sizes_force,
                                color=node_colors_force,
                                # Removed colorscale - using direct domain colors
                                showscale=False,
                                line=dict(width=2, color='white')
                            ),
                            text=node_text_force,
                            textposition='top center',
                            textfont=dict(size=9, color='black', family='Arial Black'),
                            hovertemplate='<b>%{text}</b><br>Misses: %{customdata[0]}<br>Domain: %{customdata[1]}<extra></extra>',
                            customdata=[[miss_count, get_element_domain(node[0]).replace('PRO_0', '').replace('_', ' ')] 
                                       for node, miss_count in zip(G_force.nodes(data=True), node_miss_counts)],
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
                    ["Overall", "Question Formulation", "Response Quality", "Critical Thinking", "Humility Partnership", "Reflective Practice"],
                    key="corr_net_metric",
                    help="Filter to specific PROaCTIVE criterion or show all elements"
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
            elif corr_net_metric == "Question Formulation":
                corr_net_elements = GROUPS['PRO_01_Question_Formulation']
            elif corr_net_metric == "Response Quality":
                corr_net_elements = GROUPS['PRO_02_Response_Quality']
            elif corr_net_metric == "Critical Thinking":
                corr_net_elements = GROUPS['PRO_03_Critical_Thinking']
            elif corr_net_metric == "Humility Partnership":
                corr_net_elements = GROUPS['PRO_04_Humility_Partnership']
            elif corr_net_metric == "Reflective Practice":
                corr_net_elements = GROUPS['PRO_05_Reflective_Practice']
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
        
        with net_tab4:
            st.markdown("**Completion vs. Incomplete Analytics**")
            st.caption("Frequency analysis showing completion rates for each metric")
            
            # Calculate completion rates for elements
            if len(combined_cohort_data) > 0:
                # Define completion threshold (passing score)
                completion_threshold = st.slider(
                    "Completion Threshold (scores above = complete)",
                    0.0, 4.0, 2.5, 0.1,
                    key="completion_threshold",
                    help="Scores at or above this value are considered 'complete/passing'"
                )
                
                # Calculate completion rates by domain and element
                completion_data = []
                
                for domain, elements in GROUPS.items():
                    domain_name = domain.replace('PRO_0', '').replace('_', ' ')
                    for element in elements:
                        if element in combined_cohort_data.columns:
                            total_attempts = len(combined_cohort_data)
                            completed = (combined_cohort_data[element] >= completion_threshold).sum()
                            incomplete = total_attempts - completed
                            completion_rate = (completed / total_attempts * 100) if total_attempts > 0 else 0
                            
                            completion_data.append({
                                'Domain': domain_name,
                                'Element': element.replace('_', ' ').title(),
                                'Completed': completed,
                                'Incomplete': incomplete,
                                'Total': total_attempts,
                                'Completion_Rate': completion_rate,
                                'Color': DOMAIN_COLORS[domain]
                            })
                
                if completion_data:
                    completion_df = pd.DataFrame(completion_data)
                    
                    # Sort by completion rate
                    completion_df = completion_df.sort_values('Completion_Rate', ascending=True)
                    
                    # Create horizontal bar chart
                    fig_completion = go.Figure()
                    
                    # Add incomplete bars (red)
                    fig_completion.add_trace(go.Bar(
                        y=completion_df['Element'],
                        x=completion_df['Incomplete'],
                        name='Incomplete',
                        orientation='h',
                        marker=dict(color='#E74C3C'),
                        text=completion_df['Incomplete'],
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Incomplete: %{x}<extra></extra>'
                    ))
                    
                    # Add completed bars (green) 
                    fig_completion.add_trace(go.Bar(
                        y=completion_df['Element'],
                        x=completion_df['Completed'],
                        name='Completed',
                        orientation='h',
                        marker=dict(color='#2ECC71'),
                        text=completion_df['Completed'],
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Completed: %{x}<extra></extra>'
                    ))
                    
                    fig_completion.update_layout(
                        barmode='stack',
                        xaxis=dict(title='Number of Attempts', showgrid=True, title_font=dict(color='#000000'), tickfont=dict(color='#000000')),
                        yaxis=dict(title='', tickfont=dict(size=10, color='#000000')),
                        height=max(400, len(completion_df) * 25),
                        showlegend=True,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#000000')),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#000000'),
                        margin=dict(l=200, r=50, t=40, b=50)
                    )
                    
                    st.plotly_chart(fig_completion, use_container_width=True)
                    
                    # Domain summary metrics
                    st.markdown("**Domain Completion Summary**")
                    domain_summary = completion_df.groupby('Domain').agg({
                        'Completion_Rate': 'mean',
                        'Completed': 'sum',
                        'Total': 'sum'
                    }).round(1)
                    
                    domain_cols = st.columns(len(GROUPS))
                    for idx, (domain, row) in enumerate(domain_summary.iterrows()):
                        with domain_cols[idx]:
                            st.metric(
                                domain,
                                f"{row['Completion_Rate']:.1f}%",
                                f"{int(row['Completed'])}/{int(row['Total'])}"
                            )
                    
                    # Detailed table
                    with st.expander("View Detailed Completion Data"):
                        display_df = completion_df[['Domain', 'Element', 'Completed', 'Incomplete', 'Completion_Rate']].copy()
                        display_df['Completion_Rate'] = display_df['Completion_Rate'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No completion data available with current filters.")
            else:
                st.warning("No data available for completion analysis.")
        
        # ===== TAB 5: ENCOUNTER COMPLETENESS =====
        with net_tab5:
            st.markdown("**Encounter Documentation Completeness**")
            st.caption("Binary checklist tracking key clinical documentation elements")
            
            # Check if encounter data exists in soc_wide
            encounter_cols = [f"encounter_{e}" for e in ['chief_complaint', 'hpi', 'pmh', 'social_history', 
                                                         'ros', 'family_history', 'surgical_history', 'allergies']]
            existing_encounter_cols = [col for col in encounter_cols if col in soc_wide.columns]
            
            if existing_encounter_cols:
                    # Calculate completion rates per element
                    encounter_completion = []
                    for col in existing_encounter_cols:
                        element_name = col.replace('encounter_', '').replace('_', ' ').title()
                        completed = soc_wide[col].sum()
                        total = len(soc_wide)
                        completion_rate = (completed / total * 100) if total > 0 else 0
                        
                        encounter_completion.append({
                            'Element': element_name,
                            'Completed': completed,
                            'Incomplete': total - completed,
                            'Total': total,
                            'Completion_Rate': completion_rate,
                            'Status': '✅' if completion_rate >= 75 else '⚠️' if completion_rate >= 50 else '❌'
                        })
                    
                    enc_df = pd.DataFrame(encounter_completion)
                    
                    # Overall completion percentage
                    overall_completion = enc_df['Completion_Rate'].mean()
                    items_completed = enc_df[enc_df['Completion_Rate'] >= 75].shape[0]
                    total_items = len(enc_df)
                    
                    # Display header with overall stats
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"### Overall: {items_completed}/{total_items} Items")
                    with col2:
                        st.metric("Average Completion", f"{overall_completion:.1f}%")
                    with col3:
                        if overall_completion >= 75:
                            st.success("✅ Excellent")
                        elif overall_completion >= 50:
                            st.warning("⚠️ Needs Improvement")
                        else:
                            st.error("❌ Critical")
                    
                    st.markdown("---")
                    
                    # Horizontal stacked bar chart
                    fig_enc = go.Figure()
                    
                    enc_df_sorted = enc_df.sort_values('Completion_Rate', ascending=True)
                    
                    # Incomplete (red)
                    fig_enc.add_trace(go.Bar(
                        y=enc_df_sorted['Element'],
                        x=enc_df_sorted['Incomplete'],
                        name='Not Documented',
                        orientation='h',
                        marker=dict(color='#E74C3C'),
                        text=enc_df_sorted['Incomplete'],
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Not Documented: %{x}<extra></extra>'
                    ))
                    
                    # Completed (green)
                    fig_enc.add_trace(go.Bar(
                        y=enc_df_sorted['Element'],
                        x=enc_df_sorted['Completed'],
                        name='Documented',
                        orientation='h',
                        marker=dict(color='#2ECC71'),
                        text=enc_df_sorted['Completed'],
                        textposition='inside',
                        hovertemplate='<b>%{y}</b><br>Documented: %{x}<extra></extra>'
                    ))
                    
                    fig_enc.update_layout(
                        barmode='stack',
                        xaxis=dict(title='Number of Encounters', showgrid=True, title_font=dict(color='#000000'), tickfont=dict(color='#000000')),
                        yaxis=dict(title='', tickfont=dict(size=11, color='#000000')),
                        height=400,
                        showlegend=True,
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='#000000')),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(color='#000000'),
                        margin=dict(l=180, r=50, t=40, b=50)
                    )
                    
                    st.plotly_chart(fig_enc, use_container_width=True)
                    
                    # Detailed checklist table
                    with st.expander("View Detailed Checklist"):
                        display_enc_df = enc_df[['Status', 'Element', 'Completed', 'Incomplete', 'Completion_Rate']].copy()
                        display_enc_df['Completion_Rate'] = display_enc_df['Completion_Rate'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(display_enc_df, use_container_width=True, hide_index=True)
            else:
                st.info("📋 Encounter checklist data not available. Generate new data to see this feature.")
        
        # ===== TAB 6: SPEECH QUALITY =====
        with net_tab6:
            st.markdown("**Speech Quality Metrics**")
            st.caption("Voice analysis metrics from patient encounters (0-10 scale)")
            
            # Check if speech data exists
            speech_cols = [f"speech_{m}" for m in ['volume', 'pace', 'pitch', 'pauses']]
            existing_speech_cols = [col for col in speech_cols if col in soc_wide.columns]
            
            # Debug: Show what we found
            if len(existing_speech_cols) > 0:
                st.success(f"✅ Found {len(existing_speech_cols)} speech metrics: {', '.join([c.replace('speech_', '').title() for c in existing_speech_cols])}")
            
            if existing_speech_cols:
                # Calculate average scores per metric
                speech_data = []
                for col in existing_speech_cols:
                    metric_name = col.replace('speech_', '').title()
                    avg_score = soc_wide[col].mean()
                    min_score = soc_wide[col].min()
                    max_score = soc_wide[col].max()
                    std_score = soc_wide[col].std()
                    
                    # Descriptive level based on score (0-10 scale)
                    if avg_score >= 8.5:
                        level = "Excellent"
                        level_color = "#2ECC71"
                    elif avg_score >= 7.0:
                        level = "Good"
                        level_color = "#3498DB"
                    elif avg_score >= 5.5:
                        level = "Fair"
                        level_color = "#F39C12"
                    else:
                        level = "Needs Work"
                        level_color = "#E74C3C"
                    
                    speech_data.append({
                        'Metric': metric_name,
                        'Average': avg_score,
                        'Min': min_score,
                        'Max': max_score,
                        'Std Dev': std_score,
                        'Level': level,
                        'Color': level_color
                    })
                
                speech_df = pd.DataFrame(speech_data)
                
                # Display as colored metric cards
                st.markdown("**Average Scores**")
                speech_cols_display = st.columns(4)
                for idx, row in speech_df.iterrows():
                    with speech_cols_display[idx]:
                        st.markdown(f"""
                        <div style="
                            padding: 15px;
                            border-radius: 10px;
                            background-color: {row['Color']};
                            color: white;
                            text-align: center;
                            margin-bottom: 10px;
                        ">
                            <div style="font-size: 28px; font-weight: bold;">{row['Average']:.1f}</div>
                            <div style="font-size: 14px; margin: 5px 0;">{row['Metric']}</div>
                            <div style="font-size: 12px; opacity: 0.9;">{row['Level']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Bar chart showing distribution
                fig_speech = go.Figure()
                
                fig_speech.add_trace(go.Bar(
                    x=speech_df['Metric'],
                    y=speech_df['Average'],
                    marker=dict(
                        color=speech_df['Color'],
                        line=dict(color='white', width=2)
                    ),
                    text=speech_df['Average'].apply(lambda x: f"{x:.1f}"),
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Average: %{y:.1f}/10<extra></extra>',
                    error_y=dict(
                        type='data',
                        array=speech_df['Std Dev'],
                        visible=True,
                        color='rgba(0,0,0,0.3)'
                    )
                ))
                
                fig_speech.update_layout(
                    xaxis=dict(title='Speech Metric', title_font=dict(color='#000000'), tickfont=dict(color='#000000')),
                    yaxis=dict(title='Score (0-10 scale)', range=[0, 10.5], title_font=dict(color='#000000'), tickfont=dict(color='#000000')),
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='#000000'),
                    margin=dict(l=50, r=50, t=40, b=50)
                )
                
                st.plotly_chart(fig_speech, use_container_width=True)
                
                # Metric descriptions
                with st.expander("📖 Speech Metric Descriptions"):
                    st.markdown("""
                    - **Volume**: Maintains appropriate audibility without being too loud or soft
                    - **Pace**: Professional speaking rate that allows patient comprehension  
                    - **Pitch**: Varied intonation to convey empathy and engagement
                    - **Pauses**: Meaningful pauses allowing patient reflection and thinking time
                    
                    *Scores 8.0+ indicate strong performance. Scores below 7.0 suggest areas for improvement.*
                    """)
                
                # Detailed stats table
                with st.expander("View Detailed Statistics"):
                    display_speech_df = speech_df[['Metric', 'Average', 'Min', 'Max', 'Std Dev', 'Level']].copy()
                    for col in ['Average', 'Min', 'Max', 'Std Dev']:
                        display_speech_df[col] = display_speech_df[col].apply(lambda x: f"{x:.1f}")
                    st.dataframe(display_speech_df, use_container_width=True, hide_index=True)
            else:
                st.info("🎤 Speech quality data not available. Generate new data to see this feature.")
    
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
