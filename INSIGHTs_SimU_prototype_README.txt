INSIGHTs Sim-U Prototype

What this is
-----------
This mini prototype generates mock Sim-U data (first 3 criteria) and produces a
set of PNG visualizations demonstrating what student and faculty dashboards
might show. It's a proof-of-concept only — not a web app.

Files produced (after running `simu_prototype.py`)

Student (student-facing) plots:

Faculty (faculty-facing) plots:
 - network_simu_x_socratic.png                 <- correlation network between Sim-U elements and Socratic metrics

Additional CSVs:
 - socratic_metrics_long.csv                   <- long table of generated Socratic metrics per student
 - socratic_metrics_wide.csv                   <- wide table (student_id + socratic metric columns) for correlation

Data Specification (updated)

CSV Structure (Sim-U mock):

student_id	attempt	[12 element columns]

The 12 element columns are the first three Professional Integrity criteria from the Sim-U rubric,
each with four element-level measures. Column names:

PI_01_Foster_Integrity:
- upholds_code_of_ethics
- professional_standards
- ethical_principles
- preparedness_conduct

PI_02_Safe_Learning_Environment:
- psychological_safety
- boundaries
- respectful_communication
- disruptive_behavior_response

PI_03_Foster_Inclusive_Environment:
- cultural_sensitivity
- social_determinants
- diverse_perspectives
- values_diverse_expertise

12–15 students and 5 attempts per student are used by default; scores are clamped to 40–100 with random noise and a seeded upward trend.

Socratic Metrics (optional):
 - `socratic_metrics_long.csv` contains per-student long-form socratic metric rows
 - `socratic_metrics_wide.csv` contains per-student wide-form socratic metric columns (for correlation analysis)
- --student-id ID      : which student to create the single-student plot for (default: S01)
- --miss-threshold F   : score threshold below which a score is considered a miss (default: 70.0)
- --min-misses N       : minimum misses required to show an edge in student-criterion network (default: 2)
- --seed N             : random seed for reproducible mock data (default: 42)
- --quiet              : hide a seaborn FutureWarning about palette usage

Examples
--------
Write outputs to ./out and simulate 20 students:

   python3 simu_prototype.py --out-dir out --n-students 20

Create plots for student S03 and use a higher miss threshold:

   python3 simu_prototype.py --student-id S03 --miss-threshold 75

Notes on interpretation
-----------------------
- The mock data is randomly generated but seeded for reproducibility.
- Scores are clamped to the 40–100 range to match the project specification.
- A "miss" is defined in the script as a score < 70 (this threshold can be changed with --miss-threshold).
- Network visuals show co-misses and which students miss which criteria repeatedly.
- Visuals use a default figure size of approximately 6×4 inches and are saved at 160 dpi.

If you'd like any changes (different miss threshold, different numbers of students,
or export to interactive HTML), tell me which part to change and I will update
the script.
