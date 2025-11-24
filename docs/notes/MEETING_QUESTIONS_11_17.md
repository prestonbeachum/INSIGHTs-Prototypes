# Meeting Questions - Dashboard Feedback Implementation
**Date:** November 17, 2025  
**RE:** Dr. Ford's Feedback (11/5) - Dashboard Enhancements

---

## 1. PROaCTIVE Dashboard - New Metrics

### Encounter Feedback Metrics (Binary)
**Questions:**
- What specific components of the subjective exam encounter should be tracked? For example:
  - Chief Complaint documented? (Y/N)
  - History of Present Illness documented? (Y/N)
  - Past Medical History documented? (Y/N)
  - Medications documented? (Y/N)
  - Allergies documented? (Y/N)
  - Social History documented? (Y/N)
  - Family History documented? (Y/N)
  - Review of Systems documented? (Y/N)
- Are there other binary outcomes beyond documentation (e.g., "adequately detailed", "patient-centered approach used")?
- Should these be per-encounter or aggregated across attempts?

### Speech Metrics
**Questions:**
- Which speech metrics are priorities? Examples:
  - Speaking duration/time
  - Speech rate (words per minute)
  - Filler word count (um, uh, like)
  - Pause frequency/duration
  - Volume/projection
  - Clarity/articulation score
  - Professional terminology usage
- Will speech data come from automated transcription/analysis, or manual rating?
- Should speech metrics be per-encounter or aggregated?

### Socratic Measures
**Confirmation:**
- The PROaCTIVE dashboard already has 4 Socratic domains:
  1. Question Formulation (inquiry_clarity, question_precision, conceptual_targeting, probing_depth)
  2. Response Quality (answer_accuracy, response_completeness, evidence_integration, clarity_expression)
  3. Critical Thinking (logical_reasoning, argument_evaluation, inference_quality, pattern_recognition)
  4. Assumption Recognition (implicit_assumptions, bias_awareness, premise_examination, context_sensitivity)
- **Are these the correct Socratic measures, or do we need different ones?**

### Network Visualizations
**Clarifications Needed:**
- Color-coding: Confirm 4 colors for 4 domains above, or should we use different groupings?
- "Assessment by frequency (completion vs incomplete)": 
  - Do you want a separate frequency chart showing % of students who completed each metric?
  - Or should network nodes be sized based on completion rate?
- "Networks relating associations using summed total scores for domains":
  - Should we create edges between domains based on correlation of domain totals?
  - Or show student-level associations (which students struggle with multiple domains)?

---

## 2. INSIGHTs Admin Dashboard - Instance Summaries

**Key Question:**
- Should we **integrate SIM-U and PROaCTIVE analytics into the Admin Dashboard** (centralized view), **OR** keep summaries in their individual instances and just link to them from Admin?

**If Integrated:**
- What summary metrics are most important to see at the admin level?
  - Overall completion rates?
  - Average scores by instance?
  - Student performance distributions?
  - Cohort comparisons across instances?

**Current Admin Dashboard has:**
- Instance Management (start/stop/configure)
- User Management
- Analytics (cross-instance performance, usage stats, correlations)

**Proposed Enhancement:**
- Add "Instance Analytics" tab showing:
  - Side-by-side SIM-U and PROaCTIVE performance summaries
  - Aggregate metrics across both instances
  - Quick links to detailed instance dashboards

---

## 3. SIM-U Dashboard (Professional Integrity) - New Metrics

### INACSL Standards
**Questions:**
- Which specific INACSL standards should be tracked? The Healthcare Simulation Standards of Best Practice include:
  1. Outcomes and Objectives
  2. Facilitation
  3. Debriefing
  4. Participant Evaluation
  5. Professional Development
  6. Simulation Design
  7. Prebriefing
  8. Operations
  9. Interprofessional Education
- Should we track all 9, or focus on a subset relevant to faculty training?
- Are these binary (met/not met) or scored on a rubric?

### DASH Tool (Debriefing Assessment for Simulation in Healthcare)
**Questions:**
- Should we track all 6 DASH elements?
  1. Establishes an engaging learning environment
  2. Maintains an engaging learning environment
  3. Structures debriefing in an organized way
  4. Provokes engaging discussions
  5. Identifies and explores performance gaps
  6. Helps trainees achieve or sustain good future performance
- Are these rated on the standard 7-point scale (1=extremely ineffective to 7=extremely effective)?
- Who provides ratings: peer faculty, observers, or self-assessment?

### Socratic Measures & Speech Metrics
**Questions:**
- Same Socratic domains as PROaCTIVE, or different ones for faculty training context?
- Same speech metrics, or faculty-specific (e.g., teaching clarity, questioning technique)?

### Current SIM-U Dashboard
- Currently tracks Professional Integrity criteria (PI_01 through PI_04)
- Should PI criteria remain, or be replaced by the new metrics?
- Or should both sets coexist?

---

## Easy Fixes - Implemented Today

**What I can do immediately (no clarification needed):**

1. ✅ **Add color-coding to PROaCTIVE networks** based on 4 existing domains
2. ✅ **Create completion rate analytics** showing % students completing each metric
3. ✅ **Add domain summary scores** to network visualizations
4. ✅ **Prepare admin dashboard structure** for instance summaries (can populate with real metrics after meeting)

**What needs specs before implementation:**
- Encounter Feedback metrics (need exact list)
- Speech metrics (need priority list and data source)
- INACSL Standards (need which standards and rating system)
- DASH tool integration (need rating scale and rater role)
- Admin dashboard integration approach (centralized vs. linked)

---

## Recommended Meeting Agenda

1. **Review PROaCTIVE domains** - confirm Socratic measures are correct
2. **Prioritize new metrics** - which are must-haves vs. nice-to-haves?
3. **Data sources** - where will Encounter Feedback, Speech, INACSL, DASH data come from?
4. **Admin dashboard approach** - integrated summaries or links?
5. **Timeline** - which features for next milestone?

---

## Notes
- Color-coding and completion analytics are quick wins I can implement today
- New metric types need data structure design (may need mock data generators)
- Admin integration is architectural decision best made together
