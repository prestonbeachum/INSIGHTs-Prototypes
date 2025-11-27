"""Test script to verify AI feedback context generation."""

import json
from simu_prototype import (
    generate_mock_data,
    generate_socratic_metrics,
    generate_ai_feedback_context,
    GROUPS
)

# Generate sample data
students = ['S01']
attempts = [1, 2, 3, 4, 5]

print("Generating mock data...")
df = generate_mock_data(students, attempts)
soc_long, soc_wide = generate_socratic_metrics(students)

print("\nSample domain data:")
print(df[df['student_id'] == 'S01'][df['attempt'] == 3].head())

print("\nSample Socratic data:")
print(soc_wide[soc_wide['student_id'] == 'S01'][soc_wide['attempt'] == 3])

# Extract data for a specific student/attempt
student_id = 'S01'
attempt = 3

# Get domain scores (average per domain)
student_attempt_data = df[(df['student_id'] == student_id) & (df['attempt'] == attempt)]
domain_scores = {}
for domain, elements in GROUPS.items():
    domain_scores[domain] = student_attempt_data[elements].mean().mean()

print("\nDomain scores:")
for domain, score in domain_scores.items():
    print(f"  {domain}: {score:.2f}")

# Get socratic scores from wide format
soc_student_attempt = soc_wide[(soc_wide['student_id'] == student_id) & (soc_wide['attempt'] == attempt)].iloc[0]
socratic_scores = {
    "Question Depth": soc_student_attempt['socratic_Question_Depth'],
    "Response Completeness": soc_student_attempt['socratic_Response_Completeness'],
    "Assumption Recognition": soc_student_attempt['socratic_Assumption_Recognition'],
    "Plan Flexibility": soc_student_attempt['socratic_Plan_Flexibility'],
    "In-Encounter Adjustment": soc_student_attempt['socratic_In-Encounter_Adjustment'],
}

print("\nSocratic scores:")
for metric, score in socratic_scores.items():
    print(f"  {metric}: {score:.1f}")

# Get speech scores
speech_scores = {
    "volume": soc_student_attempt['speech_volume'],
    "pace": soc_student_attempt['speech_pace'],
    "pitch": soc_student_attempt['speech_pitch'],
    "pauses": soc_student_attempt['speech_pauses'],
}

print("\nSpeech scores:")
for metric, score in speech_scores.items():
    print(f"  {metric}: {score:.1f}")

# Get encounter completeness
encounter_completeness = {
    elem: int(soc_student_attempt[f'encounter_{elem}'])  # Convert to int
    for elem in ['chief_complaint', 'hpi', 'pmh', 'social_history', 'ros', 'family_history', 'surgical_history', 'allergies']
}

print("\nEncounter completeness:")
completed = sum(encounter_completeness.values())
print(f"  {completed}/8 elements completed")

# Generate AI feedback context
print("\n" + "="*80)
print("GENERATING AI FEEDBACK CONTEXT")
print("="*80)

context = generate_ai_feedback_context(
    student_id=student_id,
    attempt=attempt,
    domain_scores=domain_scores,
    socratic_scores=socratic_scores,
    speech_scores=speech_scores,
    encounter_completeness=encounter_completeness
)

# Pretty print the context
print("\n" + json.dumps(context, indent=2))

# Save to JSON file
output_file = "ai_feedback_context_sample.json"
with open(output_file, 'w') as f:
    json.dump(context, f, indent=2)
print(f"\n✅ Context saved to: {output_file}")

print("\n" + "="*80)
print("SUMMARY FOR AI FEEDBACK GENERATION")
print("="*80)

print(f"\nStudent: {context['student_id']}, Attempt: {context['attempt']}")

print("\n🌟 TOP STRENGTHS:")
for strength in context['top_strengths']:
    print(f"  • {strength['domain']}: {strength['score']}/4.0 - {strength['note']}")

print("\n📈 GROWTH AREAS:")
for area in context['growth_areas']:
    print(f"  • {area['domain']}: {area['score']}/4.0 - {area['note']}")

print("\n🔍 OBSERVED PATTERNS:")
for pattern in context['patterns']:
    print(f"  • [{pattern['type'].upper()}] {pattern['observation']}")

print("\n👀 SPECIFIC OBSERVATIONS:")
for behavior in context['observed_behaviors']:
    print(f"  • [{behavior['timestamp']}] {behavior['category']}: {behavior['observation']}")

print("\n✅ Test completed successfully!")
