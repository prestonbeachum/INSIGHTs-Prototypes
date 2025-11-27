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

# New schema: PROaCTIVE Socratic Dialogue criteria - 5 core domains, each with 4 elements
# Based on PDF specifications: Question Formulation, Response Quality, Critical Thinking,
# Humility & Partnership, and Reflective Practice
# These will be the columns in the CSV (20 numeric columns)
GROUPS = {
    "PRO_01_Question_Formulation": [
        "question_depth",
        "question_types",
        "question_timing",
        "question_clarity",
    ],
    "PRO_02_Response_Quality": [
        "reflective_pausing",
        "response_completeness",
        "understanding_verification",
        "empathic_acknowledgment",
    ],
    "PRO_03_Critical_Thinking": [
        "assumption_recognition",
        "reasoning_transparency",
        "differential_thinking",
        "complexity_navigation",
    ],
    "PRO_04_Humility_Partnership": [
        "plan_flexibility",
        "expertise_acknowledgment",
        "uncertainty_communication",
        "partnership_language",
    ],
    "PRO_05_Reflective_Practice": [
        "in_encounter_adjustment",
        "bias_recognition",
        "style_awareness",
        "post_encounter_reflection",
    ],
}

# Flattened list of element column names (20 columns)
ELEMENTS = [el for group in GROUPS.values() for el in group]

# Encounter completeness checklist (8 binary items)
ENCOUNTER_ELEMENTS = [
    "chief_complaint",
    "hpi",
    "pmh",
    "social_history",
    "ros",
    "family_history",
    "surgical_history",
    "allergies",
]

# Speech quality metrics (0-10 scale, optional/secondary)
SPEECH_METRICS = [
    "volume",
    "pace",
    "pitch",
    "pauses",
]

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

    # Define socratic metrics based on 5 core domains (0-5.0 scale)
    socratic_specs = [
        ("Question Formulation", "Question Depth", "levels"),
        ("Response Quality", "Response Completeness", "percent"),
        ("Critical Thinking", "Assumption Recognition", "rating"),
        ("Humility Partnership", "Plan Flexibility", "percent"),
        ("Reflective Practice", "In-Encounter Adjustment", "rating"),
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
            
            # Generate encounter checklist (binary completion)
            for enc_elem in ENCOUNTER_ELEMENTS:
                # Probability of completion increases with attempts
                completion_prob = 0.5 + (attempt - 1) * 0.08  # 50% → 82% by attempt 5
                wide[f"encounter_{enc_elem}"] = 1 if random.random() < completion_prob else 0
            
            # Generate speech metrics (0-10 scale, typically 7-9 range)
            for speech_metric in SPEECH_METRICS:
                base_score = random.uniform(7.0, 8.5)
                improvement = (attempt - 1) * random.uniform(0.1, 0.3)
                noise = random.gauss(0, 0.5)
                score = max(0.0, min(10.0, round(base_score + improvement + noise, 1)))
                wide[f"speech_{speech_metric}"] = score
            
            for area, metric, measurement in socratic_specs:
                # Add progression: slight improvement over attempts with some noise
                base = student_bases[metric]
                progression = (attempt - 1) * random.uniform(0.1, 0.3)  # Gradual improvement on 0-5 scale
                noise = random.gauss(0, 0.4)  # Random variation
                score = max(0.0, min(5.0, round(base + progression + noise, 1)))
                
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


def generate_ai_feedback_context(student_id, attempt, domain_scores, socratic_scores, speech_scores, encounter_completeness, seed=RANDOM_SEED):
    """Generate rich contextual data for AI-powered feedback generation.
    
    This function creates interpretable data structures that can be used to generate
    qualitative descriptive feedback based on quantitative performance data.
    
    Args:
        student_id: Student identifier
        attempt: Attempt number
        domain_scores: Dict mapping domain names to average scores (0-4 scale)
        socratic_scores: Dict mapping Socratic component names to scores (0-5 scale)
        speech_scores: Dict mapping speech metrics to scores (0-10 scale)
        encounter_completeness: Dict mapping encounter elements to completion status (0 or 1)
        seed: Random seed for reproducibility
        
    Returns:
        Dict containing contextual data for AI feedback generation
    """
    # Create deterministic but valid seed from student_id and attempt
    combined_seed = (seed + abs(hash(student_id)) + attempt) % (2**32 - 1)
    random.seed(combined_seed)
    np.random.seed(combined_seed)
    
    context = {
        "student_id": student_id,
        "attempt": attempt,
        "timestamp": f"2025-11-{20 + attempt:02d}",  # Mock timestamp
        
        # Raw chart data for visualization
        "chart_data": {
            "domain_scores": domain_scores,
            "socratic_scores": socratic_scores,
            "speech_scores": speech_scores
        },
        
        # Performance summary
        "domain_performance": {},
        "socratic_performance": {},
        "speech_performance": {},
        "encounter_completeness": encounter_completeness,
        
        # Descriptive statistics
        "descriptive_statistics": {
            "domain_scores": {},
            "socratic_scores": {},
            "speech_scores": {}
        },
        
        # Strengths and areas for growth
        "top_strengths": [],
        "growth_areas": [],
        
        # Patterns and trends
        "patterns": [],
        
        # Specific examples (mock qualitative observations)
        "observed_behaviors": [],
    }
    
    # Calculate descriptive statistics for domain scores
    domain_values = list(domain_scores.values())
    if domain_values:
        context["descriptive_statistics"]["domain_scores"] = {
            "mean": round(np.mean(domain_values), 2),
            "median": round(np.median(domain_values), 2),
            "std": round(np.std(domain_values), 2),
            "variance": round(np.var(domain_values), 2),
            "min": round(min(domain_values), 2),
            "max": round(max(domain_values), 2),
            "range": round(max(domain_values) - min(domain_values), 2)
        }
    
    # Calculate descriptive statistics for socratic scores
    socratic_values = list(socratic_scores.values())
    if socratic_values:
        context["descriptive_statistics"]["socratic_scores"] = {
            "mean": round(np.mean(socratic_values), 2),
            "median": round(np.median(socratic_values), 2),
            "std": round(np.std(socratic_values), 2),
            "variance": round(np.var(socratic_values), 2),
            "min": round(min(socratic_values), 2),
            "max": round(max(socratic_values), 2),
            "range": round(max(socratic_values) - min(socratic_values), 2)
        }
    
    # Calculate descriptive statistics for speech scores
    speech_values = list(speech_scores.values())
    if speech_values:
        context["descriptive_statistics"]["speech_scores"] = {
            "mean": round(np.mean(speech_values), 2),
            "median": round(np.median(speech_values), 2),
            "std": round(np.std(speech_values), 2),
            "variance": round(np.var(speech_values), 2),
            "min": round(min(speech_values), 2),
            "max": round(max(speech_values), 2),
            "range": round(max(speech_values) - min(speech_values), 2)
        }
    
    # Analyze domain scores
    for domain, score in domain_scores.items():
        domain_clean = domain.replace("PRO_0", "").replace("_", " ").replace("1 ", "").replace("2 ", "").replace("3 ", "").replace("4 ", "").replace("5 ", "")
        
        # Determine proficiency level
        if score >= 3.5:
            level = "Advanced"
            descriptor = "consistently demonstrates sophisticated application"
        elif score >= 2.5:
            level = "Proficient"
            descriptor = "shows solid competence with regular effective application"
        elif score >= 1.5:
            level = "Emerging"
            descriptor = "demonstrates growing capability with some inconsistency"
        else:
            level = "Developing"
            descriptor = "beginning to incorporate skills, primarily foundational"
            
        context["domain_performance"][domain_clean] = {
            "score": round(score, 1),
            "level": level,
            "descriptor": descriptor
        }
        
        # Identify strengths (scores >= 3.0)
        if score >= 3.0:
            context["top_strengths"].append({
                "domain": domain_clean,
                "score": round(score, 1),
                "note": f"Strong {level.lower()} performance in {domain_clean.lower()}"
            })
        
        # Identify growth areas (scores < 2.5)
        elif score < 2.5:
            context["growth_areas"].append({
                "domain": domain_clean,
                "score": round(score, 1),
                "note": f"Opportunity to develop {domain_clean.lower()} skills"
            })
    
    # Analyze Socratic components (WONDER, REFLECT, REFINE, RESTATE, REPEAT framework)
    socratic_components = {
        "WONDER": ["Question Depth"],
        "REFLECT": ["Response Completeness"],
        "REFINE": ["Assumption Recognition"],
        "RESTATE": ["Plan Flexibility"],
        "REPEAT": ["In-Encounter Adjustment"]
    }
    
    for component, metrics in socratic_components.items():
        scores = [socratic_scores.get(m, 0) for m in metrics if m in socratic_scores]
        if scores:
            avg_score = np.mean(scores)
            context["socratic_performance"][component] = {
                "score": round(avg_score, 1),
                "interpretation": "strong" if avg_score >= 3.5 else "developing" if avg_score < 2.5 else "adequate"
            }
    
    # Analyze speech quality
    for metric, score in speech_scores.items():
        if score >= 8.5:
            quality = "excellent"
        elif score >= 7.0:
            quality = "good"
        elif score >= 5.5:
            quality = "adequate"
        else:
            quality = "needs attention"
            
        context["speech_performance"][metric] = {
            "score": round(score, 1),
            "quality": quality
        }
    
    # Generate pattern observations
    avg_domain = np.mean(list(domain_scores.values()))
    avg_socratic = np.mean([s.get("score", 0) for s in context["socratic_performance"].values()])
    
    if avg_domain > avg_socratic * 0.8:  # Assuming 0-4 vs 0-5 scale
        context["patterns"].append({
            "type": "alignment",
            "observation": "Domain performance aligns well with Socratic dialogue skills"
        })
    else:
        context["patterns"].append({
            "type": "gap",
            "observation": "Opportunity to better integrate Socratic techniques into clinical domains"
        })
    
    # Mock observed behaviors based on scores
    behaviors = []
    
    # Question formulation behaviors
    if "Question Formulation" in [d for d in context["top_strengths"]]:
        behaviors.append({
            "category": "Question Formulation",
            "observation": "Asked open-ended questions that invited patient elaboration",
            "timestamp": "00:02:15"
        })
    elif any("Question Formulation" in g["domain"] for g in context["growth_areas"]):
        behaviors.append({
            "category": "Question Formulation",
            "observation": "Primarily used closed-ended questions limiting patient narrative",
            "timestamp": "00:02:15"
        })
    
    # Response quality behaviors
    response_score = domain_scores.get("PRO_02_Response_Quality", 0)
    if response_score >= 3.0:
        behaviors.append({
            "category": "Response Quality",
            "observation": "Demonstrated reflective pausing before responding to patient statements",
            "timestamp": "00:05:42"
        })
    else:
        behaviors.append({
            "category": "Response Quality",
            "observation": "Responses occasionally interrupted patient's train of thought",
            "timestamp": "00:05:42"
        })
    
    # Critical thinking behaviors
    critical_score = domain_scores.get("PRO_03_Critical_Thinking", 0)
    if critical_score >= 3.0:
        behaviors.append({
            "category": "Critical Thinking",
            "observation": "Verbalized clinical reasoning process in patient-friendly language",
            "timestamp": "00:08:20"
        })
    
    # Partnership behaviors
    partnership_score = domain_scores.get("PRO_04_Humility_Partnership", 0)
    if partnership_score >= 3.0:
        behaviors.append({
            "category": "Partnership",
            "observation": "Used partnership language when discussing care plan options",
            "timestamp": "00:11:05"
        })
    elif partnership_score < 2.5:
        behaviors.append({
            "category": "Partnership",
            "observation": "Primarily directive approach with limited patient input on care decisions",
            "timestamp": "00:11:05"
        })
    
    context["observed_behaviors"] = behaviors
    
    # Sort strengths and growth areas by score
    context["top_strengths"].sort(key=lambda x: x["score"], reverse=True)
    context["growth_areas"].sort(key=lambda x: x["score"])
    
    # Generate comprehensive feedback sections
    context["what_student_did_well"] = generate_what_went_well(domain_scores, socratic_scores, speech_scores, context)
    context["areas_for_improvement"] = generate_areas_for_improvement(domain_scores, socratic_scores, speech_scores, context)
    
    return context


def generate_what_went_well(domain_scores, socratic_scores, speech_scores, context):
    """Generate detailed 'What the student did well' feedback."""
    feedback = []
    
    # Speech quality and delivery
    avg_speech = np.mean(list(speech_scores.values()))
    if avg_speech >= 7.0:
        speech_details = []
        if speech_scores.get("volume", 0) >= 7.0:
            speech_details.append("maintained an appropriate volume throughout, ensuring clear audibility")
        if speech_scores.get("pace", 0) >= 7.0:
            speech_details.append("maintained a well-paced professional rate that allowed the patient to process information")
        if speech_scores.get("pitch", 0) >= 7.0:
            speech_details.append("varied pitch and intonation effectively to convey empathy and engagement")
        if speech_scores.get("pauses", 0) >= 7.0:
            speech_details.append("used meaningful pauses that allowed patient reflection")
        
        if speech_details:
            feedback.append({
                "category": "Speech Quality and Delivery",
                "details": "The student " + ", ".join(speech_details) + ". This approach enhanced patient comfort and comprehension throughout the encounter."
            })
    
    # Socratic dialogue
    wonder_score = socratic_scores.get("Question Depth", 0)
    reflect_score = socratic_scores.get("Response Completeness", 0)
    refine_score = socratic_scores.get("Assumption Recognition", 0)
    
    if wonder_score >= 3.0 or reflect_score >= 3.0:
        socratic_details = []
        if wonder_score >= 3.0:
            socratic_details.append("demonstrated strong curiosity by frequently asking open-ended questions")
        if reflect_score >= 3.0:
            socratic_details.append("showed reflective listening with empathetic acknowledgments and summarizing")
        if refine_score >= 3.0:
            socratic_details.append("skillfully refined patient responses to clarify meaning")
        
        if socratic_details:
            feedback.append({
                "category": "Socratic Dialogue",
                "details": "The student " + ", ".join(socratic_details) + ". This approach helped deepen patient engagement and understanding."
            })
    
    # Clinical reasoning and shared decision making
    critical_score = domain_scores.get("PRO_03_Critical_Thinking", 0)
    partnership_score = domain_scores.get("PRO_04_Humility_Partnership", 0)
    
    if critical_score >= 2.5 or partnership_score >= 2.5:
        clinical_details = []
        if critical_score >= 2.5:
            clinical_details.append("demonstrated thoughtful clinical reasoning with transparent explanation of decision-making")
        if partnership_score >= 2.5:
            clinical_details.append("showed humility and partnership by inviting patient input on care decisions")
            clinical_details.append("validated patient concerns respectfully and communicated uncertainty constructively")
        
        if clinical_details:
            feedback.append({
                "category": "Clinical Reasoning and Shared Decision Making",
                "details": "The student " + ", ".join(clinical_details) + "."
            })
    
    # Patient-centered communication
    question_score = domain_scores.get("PRO_01_Question_Formulation", 0)
    response_score = domain_scores.get("PRO_02_Response_Quality", 0)
    
    if question_score >= 2.5 or response_score >= 2.5:
        communication_details = []
        if question_score >= 2.5:
            communication_details.append("consistently avoided jargon and used accessible language")
        if response_score >= 2.5:
            communication_details.append("provided empathic acknowledgment that helped build rapport and trust")
        communication_details.append("encouraged patient agency in decision-making")
        
        feedback.append({
            "category": "Patient-Centered Communication",
            "details": "The student " + ", ".join(communication_details) + "."
        })
    
    return feedback


def generate_areas_for_improvement(domain_scores, socratic_scores, speech_scores, context):
    """Generate detailed 'Areas for improvement' feedback."""
    feedback = []
    
    # Speech quality improvements
    avg_speech = np.mean(list(speech_scores.values()))
    if avg_speech < 8.5:
        speech_improvements = []
        if speech_scores.get("pace", 0) < 8.5:
            speech_improvements.append("slightly slower delivery and longer reflective pauses could permit deeper patient processing, especially after emotionally charged questions")
        if speech_scores.get("pitch", 0) < 8.5:
            speech_improvements.append("enhancing pitch variation to emphasize key points more dramatically could increase engagement")
        
        if speech_improvements:
            feedback.append({
                "category": "Speech Quality and Delivery",
                "details": "While overall delivery was appropriate, " + " Additionally, ".join(speech_improvements) + "."
            })
    
    # Reflective practice
    reflective_score = domain_scores.get("PRO_05_Reflective_Practice", 0)
    if reflective_score < 3.0:
        feedback.append({
            "category": "Reflective Practice and Self-Awareness",
            "details": "The student showed some adaptive responses but could improve by actively recognizing and verbalizing personal biases or assumptions during the encounter. More overt in-encounter adjustments based on patient cues could enhance responsiveness."
        })
    
    # Clinical reasoning transparency
    critical_score = domain_scores.get("PRO_03_Critical_Thinking", 0)
    if critical_score < 3.5:
        feedback.append({
            "category": "Clinical Reasoning Transparency",
            "details": "While the student shared clinical thinking, further explaining the rationale behind each suggested test or treatment option in more detail could improve patient understanding and engagement. Clarifying why specific approaches are prioritized would be beneficial."
        })
    
    # Question formulation
    question_score = domain_scores.get("PRO_01_Question_Formulation", 0)
    if question_score < 3.0:
        feedback.append({
            "category": "Question Formulation",
            "details": "Greater use of open-ended questions and deeper exploration of patient perspectives could enhance information gathering. Consider asking more 'why' and 'how' questions to understand patient reasoning and concerns."
        })
    
    # Response quality
    response_score = domain_scores.get("PRO_02_Response_Quality", 0)
    if response_score < 3.0:
        feedback.append({
            "category": "Active Listening and Response Quality",
            "details": "More consistent use of reflective pausing before responding would demonstrate active listening. Ensuring all patient concerns are acknowledged before moving to the next topic would improve completeness."
        })
    
    return feedback


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
