"""simu_prototype.py

Mock data generator that creates CSV files for the INSIGHTs prototype,
matching the INSIGHTs PROaCTIVE prototype description.

Run:
  python3 simu_prototype.py

Produces:
  - simu_first3_criteria_mock.csv
  - student_cohort_avg_by_criterion.png
  - student_cohort_overall_trend.png
  - S01_avg_by_criterion.png
  - faculty_boxplot_by_criterion.png
  - faculty_attempt_vs_overall_scatter.png
  - network_co_missed_criteria.png
  - network_student_criterion_bipartite.png

Dependencies: pandas, numpy, matplotlib, networkx, seaborn
"""

import os
from pathlib import Path
import random
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib import cm

# Make reproducible
RANDOM_SEED = 42

# Use matplotlib default style (no external theme)
plt.style.use('default')

# Default figure size and DPI
FIGSIZE = (6, 4)
DPI = 160

# Default output directory (script directory)
DEFAULT_OUT_DIR = Path(__file__).resolve().parent

# New schema: PROaCTIVE Socratic Dialogue criteria, each with 4 elements
# Covers: Question Formulation, Response Quality, Critical Thinking, and Assumption Recognition
# These will be the columns in the CSV (16 numeric columns)
GROUPS = {
    "PRO_01_Question_Formulation": [
        "inquiry_clarity",
        "question_precision",
        "conceptual_targeting",
        "probing_depth",
    ],
    "PRO_02_Response_Quality": [
        "answer_accuracy",
        "response_completeness",
        "evidence_integration",
        "clarity_expression",
    ],
    "PRO_03_Critical_Thinking": [
        "logical_reasoning",
        "argument_evaluation",
        "inference_quality",
        "pattern_recognition",
    ],
    "PRO_04_Assumption_Recognition": [
        "implicit_assumptions",
        "bias_awareness",
        "premise_examination",
        "context_sensitivity",
    ],
}

# Flattened list of element column names (16 columns)
ELEMENTS = [el for group in GROUPS.values() for el in group]

# -------------
# 1) Generate mock data
# -------------

def generate_mock_data(students, attempts, seed=RANDOM_SEED, groups=GROUPS):
    """Generate mock dataframe for given students and attempts.

    Args:
        students: list of student IDs (e.g., ['S01', 'S02'])
        attempts: list of attempt numbers (e.g., [1,2,3,4,5])
        seed: random seed for reproducibility
    Returns:
        pandas.DataFrame
    """
    random.seed(seed)
    np.random.seed(seed)

    rows = []
    # Per-student baseline ability to create variety (on 0-4 rubric scale)
    # Most students start around 1.5-2.5 (Developing to Proficient range)
    baselines = {s: random.uniform(1.2, 2.8) for s in students}

    # Per-group sensitivity modifiers to vary how much elements improve
    group_sensitivities = {g: random.uniform(0.8, 1.2) for g in groups.keys()}

    # Generate data for all scenario/mode combinations
    scenarios = ["PROaCTIVE : Cardio A", "PROaCTIVE : Cardio B", "PROaCTIVE : Respiratory"]
    modes = ["Socratic", "Verbal", "Mixed"]
    
    for s in students:
        base = baselines[s]
        # per-student per-group bias
        student_group_bias = {g: random.uniform(-0.3, 0.3) for g in groups.keys()}
        
        # Generate data for each scenario/mode combination
        for scenario in scenarios:
            for mode in modes:
                for a in attempts:
                    # Students generally improve slightly with attempts, but with noise
                    # Improvement of ~0.1-0.3 per attempt on 0-4 scale
                    improvement = (a - 1) * random.uniform(0.1, 0.3)
                    
                    # Add small variation based on scenario/mode
                    scenario_modifier = random.gauss(0, 0.1)
                    mode_modifier = random.gauss(0, 0.1)

                    row = {
                        "student_id": s, 
                        "attempt": a,
                        "scenario": scenario,
                        "mode": mode
                    }
                    # Generate each element score
                    for g, elements in groups.items():
                        g_sens = group_sensitivities[g]
                        g_bias = student_group_bias[g]
                        for el in elements:
                            # element-specific noise and slight variation
                            raw = base + improvement * g_sens + g_bias + scenario_modifier + mode_modifier + random.gauss(0, 0.5)
                            # Clamp to 0-4 rubric scale and round to 1 decimal
                            val = max(0.0, min(4.0, round(raw, 1)))
                            row[el] = val

                    rows.append(row)

    df = pd.DataFrame(rows)
    # Shuffle rows for realism
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


# -------------
# 2) Plots for student view
# -------------

def plot_student_cohort_avg_by_criterion(df, out_path):
    # Compute cohort average per GROUP (average across the group's elements)
    group_means = {gname: df[elements].mean(axis=1).mean() for gname, elements in GROUPS.items()}
    labels = [g.replace('_', ' ') for g in group_means.keys()]
    values = list(group_means.values())
    plt.figure(figsize=FIGSIZE)
    cmap = cm.get_cmap('Blues')
    colors = [cmap(i / max(1, len(labels) - 1)) for i in range(len(labels))]
    plt.bar(labels, values, color=colors)
    plt.ylim(0, 4)
    plt.ylabel('Average score (0-4 rubric scale)')
    plt.title('Class average by criterion group (all attempts)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


def plot_student_cohort_overall_trend(df, out_path):
    df = df.copy()
    df['overall'] = df[ELEMENTS].mean(axis=1)
    by_attempt = df.groupby('attempt')['overall'].mean()
    plt.figure(figsize=FIGSIZE)
    plt.plot(by_attempt.index, by_attempt.values, marker='o')
    plt.ylim(0, 4)
    plt.xlabel('Attempt')
    plt.ylabel('Average overall score (0-4 rubric scale)')
    plt.title('Cohort overall trend by attempt')
    plt.xticks(sorted(df['attempt'].unique()))
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


def plot_single_student_avg(df, out_path, student_id='S01'):
    s = df[df['student_id'] == student_id]
    if s.empty:
        print(f"Warning: no data for {student_id}")
        return
    # Compute per-group mean for this student across all attempts
    group_means = {gname: s[elements].mean(axis=0).mean() for gname, elements in GROUPS.items()}
    labels = [g.replace('_', ' ') for g in group_means.keys()]
    values = list(group_means.values())
    plt.figure(figsize=FIGSIZE)
    cmap = cm.get_cmap('Greens')
    colors = [cmap(i / max(1, len(labels) - 1)) for i in range(len(labels))]
    plt.bar(labels, values, color=colors)
    plt.ylim(0, 4)
    plt.title(f'{student_id} average by criterion group (all attempts)')
    plt.ylabel('Average score (0-4 rubric scale)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


# -------------
# 3) Plots for faculty view
# -------------

def plot_faculty_boxplot_by_criterion(df, out_path):
    # Boxplot per group: compute group-level averages across each row, then show distribution
    plt.figure(figsize=(FIGSIZE[0] * 1.33, FIGSIZE[1] * 1.5))
    # compute per-row group means
    group_df = pd.DataFrame()
    for gname, elements in GROUPS.items():
        group_df[gname] = df[elements].mean(axis=1)

    groups = [group_df[col].values for col in group_df.columns]
    plt.boxplot(groups, labels=list(group_df.columns))
    plt.ylim(0, 4)
    plt.ylabel('Score (0-4 rubric scale)')
    plt.title('Score distribution by criterion group (all students & attempts)')
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


def plot_faculty_attempt_vs_overall_scatter(df, out_path):
    df = df.copy()
    df['overall'] = df[ELEMENTS].mean(axis=1)
    plt.figure(figsize=(FIGSIZE[0] * 1.33, FIGSIZE[1] * 1.5))
    plt.scatter(df['attempt'], df['overall'], alpha=0.7)
    # add a simple trend line
    z = np.polyfit(df['attempt'], df['overall'], 1)
    p = np.poly1d(z)
    xs = np.linspace(df['attempt'].min(), df['attempt'].max(), 100)
    plt.plot(xs, p(xs), color='red', linestyle='--')
    plt.ylim(0, 4)
    plt.xlabel('Attempt')
    plt.ylabel('Overall score (0-4 rubric scale)')
    plt.title('Attempt vs overall score (trend line)')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


# -------------
# 4) Networks for faculty
# -------------

def plot_network_co_missed_criteria(df, out_path, miss_threshold=70):
    # Define a miss as score < miss_threshold
    misses = df.copy()
    for c in ELEMENTS:
        misses[c] = misses[c] < miss_threshold

    # count co-misses
    co_miss_counts = {}
    for i in range(len(ELEMENTS)):
        for j in range(i + 1, len(ELEMENTS)):
            c1 = ELEMENTS[i]
            c2 = ELEMENTS[j]
            both = (misses[c1] & misses[c2]).sum()
            co_miss_counts[(c1, c2)] = both

    # Build graph
    G = nx.Graph()
    # Add nodes
    labels = {c: c.replace('_', '\n') for c in ELEMENTS}
    for c in ELEMENTS:
        G.add_node(c)
    # Add edges weighted by co-miss counts (only if > 0)
    for (c1, c2), count in co_miss_counts.items():
        if count > 0:
            G.add_edge(c1, c2, weight=count)

    plt.figure(figsize=(FIGSIZE[0] * 1.0, FIGSIZE[1] * 1.5))
    pos = nx.spring_layout(G, seed=RANDOM_SEED)
    # node sizes scaled by total misses per criterion
    node_sizes = [max(200, 200 * df[df[c] < miss_threshold].shape[0] / 5) for c in ELEMENTS]
    # edge widths from weights
    edges = G.edges(data=True)
    edge_widths = [max(1.0, d['weight'] * 0.7) for (_, _, d) in edges]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='lightcoral')
    nx.draw_networkx_edges(G, pos, width=edge_widths)
    nx.draw_networkx_labels(G, pos, labels)
    plt.title(f'Co-missed criteria (miss < {miss_threshold})')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


def plot_network_student_criterion_bipartite(df, out_path, miss_threshold=70, min_misses_for_edge=2):
    # For each student, count misses per criterion
    misses = df.copy()
    for c in ELEMENTS:
        misses[c] = misses[c] < miss_threshold

    student_crit_counts = {}
    for s in df['student_id'].unique():
        sub = misses[misses['student_id'] == s]
        student_crit_counts[s] = {c: sub[c].sum() for c in ELEMENTS}

    B = nx.Graph()
    # Add student nodes and criterion nodes
    for s, counts in student_crit_counts.items():
        B.add_node(s, bipartite=0)
    for c in ELEMENTS:
        B.add_node(c, bipartite=1)

    # Add edges when a student misses a criterion at least min_misses_for_edge times
    for s, counts in student_crit_counts.items():
        for c, cnt in counts.items():
            if cnt >= min_misses_for_edge:
                B.add_edge(s, c, weight=cnt)

    # Draw bipartite layout
    plt.figure(figsize=(FIGSIZE[0] * 1.6, FIGSIZE[1] * 1.5))
    # Separate positions
    top = {n: (i * 1.0, 1) for i, n in enumerate([n for n in B.nodes() if n in student_crit_counts.keys()])}
    bottom = {n: (i * 2.0, 0) for i, n in enumerate(ELEMENTS)}
    pos = {**top, **bottom}

    # Draw nodes
    student_nodes = [n for n in B.nodes() if n in student_crit_counts.keys()]
    crit_nodes = ELEMENTS
    nx.draw_networkx_nodes(B, pos, nodelist=student_nodes, node_color='skyblue', node_size=300, label='students')
    nx.draw_networkx_nodes(B, pos, nodelist=crit_nodes, node_color='lightgreen', node_size=800, label='criteria')

    # Edge widths
    edges = B.edges(data=True)
    edge_widths = [1 + d['weight'] for (_, _, d) in edges]
    nx.draw_networkx_edges(B, pos, width=edge_widths)

    labels = {n: n for n in B.nodes()}
    nx.draw_networkx_labels(B, pos, labels, font_size=9)
    plt.title(f'Student - Criterion risk map (misses >= {min_misses_for_edge})')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


def generate_socratic_metrics(students, seed=RANDOM_SEED, num_attempts=5):
    """Generate a small socratic metrics table per student for cross-analysis.

    Returns a DataFrame with columns: student_id, attempt, competency_area, metric, measurement, score
    For simplicity we aggregate per-student-attempt into a wide table too (student_id + attempt + metrics)
    """
    random.seed(seed)
    np.random.seed(seed)

    # Define a few mock socratic metrics
    socratic_specs = [
        ("Question Formulation", "Question Depth", "levels"),
        ("Response Quality", "Answer Completeness", "percent"),
        ("Critical Thinking", "Logical Reasoning", "rating"),
        ("Assumption Recognition", "Assumption Awareness", "rating"),
    ]

    rows = []
    wide_rows = []
    for s in students:
        # Generate base scores for this student (0-4 rubric scale)
        student_bases = {}
        for area, metric, measurement in socratic_specs:
            student_bases[metric] = random.uniform(1.2, 2.8)  # Developing to Proficient range
        
        # Generate scores across attempts with progression
        for attempt in range(1, num_attempts + 1):
            wide = {"student_id": s, "attempt": attempt}
            for area, metric, measurement in socratic_specs:
                # Add progression: slight improvement over attempts with some noise
                base = student_bases[metric]
                progression = (attempt - 1) * random.uniform(0.1, 0.3)  # Gradual improvement on 0-4 scale
                noise = random.gauss(0, 0.4)  # Random variation
                score = max(0.0, min(4.0, round(base + progression + noise, 1)))
                
                rows.append({
                    "student_id": s, 
                    "attempt": attempt,
                    "competency_area": area, 
                    "metric": metric, 
                    "measurement": measurement, 
                    "score": score
                })
                wide[f"socratic_{metric.replace(' ', '_')}"] = score
            wide_rows.append(wide)

    df_long = pd.DataFrame(rows)
    df_wide = pd.DataFrame(wide_rows)
    return df_long, df_wide


def plot_simu_x_socratic_network(simudf, socratic_wide_df, out_path, miss_threshold=70):
    """Create a bipartite-like network showing correlations between PROaCTIVE elements and Socratic metrics.

    We'll compute Pearson correlations between each PROaCTIVE element (averaged per student) and each socratic metric.
    Edges show absolute correlation > 0.3 (or configurable threshold).
    """
    # Aggregate simudf per student
    sim_per_student = simudf.groupby('student_id')[ELEMENTS].mean()
    soc_wide = socratic_wide_df.set_index('student_id')

    # compute correlations
    corr = pd.DataFrame(index=ELEMENTS, columns=soc_wide.columns, dtype=float)
    for e in ELEMENTS:
        for s in soc_wide.columns:
            try:
                corr.loc[e, s] = sim_per_student[e].corr(soc_wide[s])
            except Exception:
                corr.loc[e, s] = 0.0

    # Build graph: nodes are elements and socratic metrics
    G = nx.Graph()
    for e in ELEMENTS:
        G.add_node(e, bipartite=0)
    for s in soc_wide.columns:
        G.add_node(s, bipartite=1)

    # Add edges for |corr| >= 0.3
    for e in ELEMENTS:
        for s in soc_wide.columns:
            val = corr.loc[e, s]
            if pd.notna(val) and abs(val) >= 0.3:
                G.add_edge(e, s, weight=abs(val), corr=val)

    plt.figure(figsize=(FIGSIZE[0] * 1.6, FIGSIZE[1] * 1.5))
    # Simple layout: elements on left, socratic on right
    left = {n: (0, i) for i, n in enumerate(ELEMENTS)}
    right = {n: (2, i) for i, n in enumerate(soc_wide.columns)}
    pos = {**left, **right}

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=ELEMENTS, node_color='lightblue', node_size=300)
    nx.draw_networkx_nodes(G, pos, nodelist=list(soc_wide.columns), node_color='lightgreen', node_size=700)

    edges = G.edges(data=True)
    edge_widths = [1 + d['weight'] * 4 for (_, _, d) in edges]
    nx.draw_networkx_edges(G, pos, width=edge_widths)

    labels = {n: n.replace('_', '\n') for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title('PROaCTIVE elements × Socratic metrics (|corr| >= 0.3)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()


# -------------
# Main
# -------------

def main():
    parser = argparse.ArgumentParser(description='Generate INSIGHTs PROaCTIVE prototype CSV and PNGs')
    parser.add_argument('--out-dir', type=Path, default=DEFAULT_OUT_DIR, help='Directory to write CSV and PNGs')
    parser.add_argument('--n-students', type=int, default=12, help='Number of students to simulate')
    parser.add_argument('--n-attempts', type=int, default=5, help='Number of attempts per student')
    parser.add_argument('--student-id', type=str, default='S01', help='Example student id for single-student plot')
    parser.add_argument('--miss-threshold', type=float, default=70.0, help='Threshold below which a score is considered a miss')
    parser.add_argument('--min-misses', type=int, default=2, help='Minimum misses for showing an edge in student-criterion network')
    parser.add_argument('--seed', type=int, default=RANDOM_SEED, help='Random seed')
    parser.add_argument('--quiet', action='store_true', help='Suppress seaborn future warnings')
    args = parser.parse_args()

    # Optional: suppress seaborn FutureWarning about palette usage to keep output clean
    if args.quiet:
        warnings.filterwarnings("ignore", message="Passing `palette` without assigning `hue` is deprecated")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build student and attempt lists
    students = [f"S{str(i).zfill(2)}" for i in range(1, args.n_students + 1)]
    attempts = list(range(1, args.n_attempts + 1))

    print('Generating mock data...')
    df = generate_mock_data(students, attempts, seed=args.seed)
    csv_path = out_dir / 'simu_first3_criteria_mock.csv'
    df.to_csv(csv_path, index=False)
    print(f'Wrote CSV -> {csv_path}')

    print('Creating student view plots...')
    plot_student_cohort_avg_by_criterion(df, out_dir / 'student_cohort_avg_by_criterion.png')
    plot_student_cohort_overall_trend(df, out_dir / 'student_cohort_overall_trend.png')
    plot_single_student_avg(df, out_dir / f'{args.student_id}_avg_by_criterion.png', student_id=args.student_id)

    print('Creating faculty view plots...')
    plot_faculty_boxplot_by_criterion(df, out_dir / 'faculty_boxplot_by_criterion.png')
    plot_faculty_attempt_vs_overall_scatter(df, out_dir / 'faculty_attempt_vs_overall_scatter.png')
    plot_network_co_missed_criteria(df, out_dir / 'network_co_missed_criteria.png', miss_threshold=args.miss_threshold)
    plot_network_student_criterion_bipartite(df, out_dir / 'network_student_criterion_bipartite.png', miss_threshold=args.miss_threshold, min_misses_for_edge=args.min_misses)
    # Generate socratic metrics (long + wide). Save for potential cross-analysis
    soc_long, soc_wide = generate_socratic_metrics(students, seed=args.seed)
    soc_long_path = out_dir / 'socratic_metrics_long.csv'
    soc_wide_path = out_dir / 'socratic_metrics_wide.csv'
    soc_long.to_csv(soc_long_path, index=False)
    soc_wide.to_csv(soc_wide_path, index=False)
    print(f'Wrote Socratic CSVs -> {soc_long_path}, {soc_wide_path}')

    # Create cross-domain network between PROaCTIVE elements and Socratic metrics
    plot_simu_x_socratic_network(df, soc_wide, out_dir / 'network_simu_x_socratic.png', miss_threshold=args.miss_threshold)

    print('All plots saved in', out_dir)


if __name__ == '__main__':
    main()
