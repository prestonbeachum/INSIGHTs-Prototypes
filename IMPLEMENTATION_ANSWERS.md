# Implementation Answers - Based on PDF Specifications
## November 19, 2025

This document answers all the clarifying questions based on the Socratic Dialogue PDFs.

---

## 📊 **PROaCTIVE DASHBOARD**

### **Q1: What does "Encounter Feedback" mean?**

**Answer**: ✅ **YES - It's a binary checklist of 8 clinical documentation elements**

From the PDFs, "Encounter Feedback" tracks whether students documented these key elements:

1. ✅ **Chief Complaint (CC)** - Open-ended solicitation of reason for visit
2. ✅ **History of Present Illness (HPI)** - Chronological symptom exploration  
3. ✅ **Past Medical History (PMH)** - Discussion of diagnoses and medications
4. ✅ **Social History** - Smoking, diet, lifestyle habits
5. ✅ **Review of Systems (ROS)** - Systematic inquiry beyond chief complaint
6. ✅ **Family History** - Inquiry about hereditary conditions
7. ✅ **Past Surgical History** - Surgical background
8. ✅ **Allergies** - Allergy documentation

**Implementation**:
- Binary tracking (yes/no) for each item per encounter
- Display completion percentage (e.g., "6/8 items covered - 75%")
- Highlight missed items in red for student feedback
- Track trends over time (improvement in completeness)

---

### **Q2: What are "Speech Metrics"?**

**Answer**: ✅ **4 metrics on a 0-10 scale (OPTIONAL/SECONDARY)**

The PDFs specify these speech quality metrics:

1. **Volume** - Maintains appropriate audibility (not too loud/soft)
2. **Pace** - Professional speaking rate that allows comprehension
3. **Pitch** - Varied intonation to convey empathy and engagement
4. **Pauses** - Meaningful pauses that allow patient reflection

**Important Note from PDF**: 
> "Speech metrics use default values (no audio provided)"

**Priority**: **LOWER PRIORITY** - These are optional unless you have audio analysis capability.

**Implementation Decision**:
- Add speech metrics as **optional/supplementary section**
- Show default values (8.0) if no audio analysis
- Add flag "Audio Analysis: Not Available" when defaults used
- Only show detailed speech metrics if audio is processed
- Focus first on Socratic domains (higher priority)

---

### **Q3: Are the Socratic measures we already have correct?**

**Answer**: ✅ **YES, but expand them with detailed sub-metrics**

Your current 4 domains are correct and match the PDF, but there are actually **5 core domains** with multiple sub-metrics each:

**EXPAND TO 5 DOMAINS**:

1. ✅ **Question Formulation** (you have this)
   - Add sub-metrics: Depth, Types, Timing, Clarity

2. ✅ **Response Quality** (you have this)
   - Add sub-metrics: Reflective Pausing, Completeness, Verification, Empathy

3. ✅ **Critical Thinking** (you have this)
   - Add sub-metrics: Assumption Recognition, Reasoning Transparency, Differential Thinking, Complexity Navigation

4. ❌ **Shared Decision-Making & Humility** (you DON'T have this - need to add!)
   - Sub-metrics: Plan Flexibility, Expertise Acknowledgment, Uncertainty Communication, Partnership Language

5. ❌ **Reflective Practice & Self-Awareness** (you DON'T have this - need to add!)
   - Sub-metrics: In-Encounter Adjustment, Bias Recognition, Style Awareness, Post-Encounter Reflection

**Additional System**: The PDFs also show 5 **Socratic Components** (simpler scoring):
- WONDER (curiosity)
- REFLECT (listening)
- REFINE (clarification)
- RESTATE (summarization)
- REPEAT (cycling back)

**Recommendation**: 
- Keep your 4 current domains
- **Add 2 new domains** (Humility/Partnership + Reflective Practice)
- Add detailed sub-metrics to all 5 domains
- Optionally add the 5 Socratic Components as a quick visual summary

---

### **Q4: Current Socratic domains - keep these 4?**

**Answer**: ✅ **EXPAND to 5 domains**

| Current (4 domains) | Recommended (5 domains) |
|---------------------|-------------------------|
| ✅ Question Formulation | ✅ Question Formulation Skills |
| ✅ Response Quality | ✅ Response Quality to Inquiry |
| ✅ Critical Thinking | ✅ Critical Thinking & Clinical Reasoning Transparency |
| ✅ Assumption Recognition | ❌ **Merge into Critical Thinking** (as sub-metric) |
| ❌ Missing | ✅ **ADD: Shared Decision-Making & Humility** |
| ❌ Missing | ✅ **ADD: Reflective Practice & Self-Awareness** |

**Action Items**:
1. Merge "Assumption Recognition" into "Critical Thinking" as a sub-metric
2. Add new domain: "Shared Decision-Making & Humility"
3. Add new domain: "Reflective Practice & Self-Awareness"
4. Add sub-metrics to all 5 domains (4 sub-metrics each)

**Color Mapping Update**:
```python
DOMAIN_COLORS = {
    "PRO_01": "#3498DB",   # Blue - Question Formulation
    "PRO_02": "#2ECC71",   # Green - Response Quality
    "PRO_03": "#E67E22",   # Orange - Critical Thinking
    "PRO_04": "#9B59B6",   # Purple - Humility & Partnership (NEW)
    "PRO_05": "#E74C3C",   # Red - Reflective Practice (NEW)
}
```

---

## 🏥 **SIM-U DASHBOARD**

### **Q1: INACSL Standards - which ones?**

**Answer**: ⚠️ **NOT SPECIFIED IN PDFs - Need Dr. Ford input**

The PDFs focus on **Socratic Dialogue** assessment, not INACSL Standards. The INACSL Standards for Best Practice include 9 areas:

1. Outcomes and Objectives
2. Facilitation
3. Debriefing
4. Participant Evaluation
5. Professional Integrity
6. Simulation Design
7. Operations
8. Simulation-Enhanced Interprofessional Education (Sim-IPE)
9. Prebriefing

**Current Implementation**: SIM-U already tracks **Professional Integrity** (PI_01, PI_02, PI_03)

**Questions for Dr. Ford**:
- Which INACSL standards to add beyond Professional Integrity?
- Prioritize which 2-3 standards for initial implementation?
- Are these separate from Socratic measures or integrated?

**Recommendation**: 
- **Keep Professional Integrity** (0-4 scale) as is
- Add **Facilitation** and **Debriefing** as top priorities
- Use same 0-4 rubric scale for consistency

---

### **Q2: DASH tool - is this the debriefing quality checklist with 6 items?**

**Answer**: ⚠️ **NOT SPECIFIED IN PDFs - Need Dr. Ford input**

The PDFs don't mention DASH tool. The **Debriefing Assessment for Simulation in Healthcare (DASH)** typically includes:

- 6 elements rated on a 7-point scale (1=ineffective to 7=extremely effective)
- Elements: Establishes context, maintains engaging environment, structures debriefing, provokes discussion, identifies/explores issues, helps gain insight

**Questions for Dr. Ford**:
- Is this the DASH tool she wants?
- Should it be faculty-only or visible to students?
- Replace existing debriefing metrics or add alongside?

**Recommendation**: 
- Add DASH as a **faculty-only assessment tool**
- 6 elements × 7-point scale
- Separate section in Faculty View
- Show trends over multiple debriefing sessions

---

### **Q3: Do faculty need different Socratic/Speech metrics than students?**

**Answer**: ✅ **YES - Faculty assess students, students see their own scores**

Based on PDF structure:

**Student View** (self-assessment focus):
- View their own Socratic dialogue scores
- See encounter completeness checklist
- Track improvement over time
- Receive automated feedback (what went well, areas to improve)
- View speech metrics (if audio available)

**Faculty View** (assessment & analytics):
- Rate individual students on Socratic domains
- View class-wide analytics and trends
- Compare students or cohorts
- Identify struggling students
- Generate detailed feedback reports
- Access DASH tool for debriefing quality

**Metrics are the SAME, but access/views differ**:
- Same 5 Socratic domains
- Same 8 encounter checklist items
- Same 4 speech metrics
- Different visualization and permissions

---

### **Q4: What happens to the current Professional Integrity stuff?**

**Answer**: ✅ **KEEP IT - Professional Integrity is separate from Socratic**

**Professional Integrity** (SIM-U):
- 0-4 rubric scale
- Elements: PI_01, PI_02, PI_03 (currently implemented)
- INACSL Standard #5
- Measures ethical behavior, accountability, honesty

**Socratic Dialogue** (PROaCTIVE):
- 0-5.0 scale
- 5 core domains with sub-metrics
- Measures questioning, listening, critical thinking

**They serve different purposes**:

| SIM-U (Professional Integrity) | PROaCTIVE (Socratic Dialogue) |
|-------------------------------|-------------------------------|
| Ethical behavior in simulation | Communication during patient encounters |
| 0-4 rubric scale | 0-5.0 scale |
| PI_01, PI_02, PI_03 | 5 core domains (20+ sub-metrics) |
| INACSL Standards-based | Socratic method-based |
| Keep as is | Expand with sub-metrics |

**Recommendation**: 
- **KEEP Professional Integrity** in SIM-U unchanged
- **ADD Socratic domains** to PROaCTIVE dashboard
- Optionally: Add Socratic measures to SIM-U if faculty want to assess communication during simulations
- Keep the assessments conceptually separate

---

## 🎛️ **ADMIN DASHBOARD**

### **Q: Does she want to see SIM-U and PROaCTIVE summaries in the Admin Dashboard?**

**Answer**: ✅ **CONFIRMED - All applications are separate, admin has access to all**

**Architecture**: Distributed independent dashboards with admin navigation

```
Admin Dashboard (8500)
├── Instance Management
│   ├── Start/Stop Dashboard Instances
│   ├── Monitor System Resources
│   └── View Instance Status
├── User Administration
│   ├── User Management
│   ├── Role Assignment
│   └── Access Control
└── Dashboard Access Links
    ├── 🏥 SIM-U Dashboard (8501) → Professional Integrity
    └── 💬 PROaCTIVE Dashboard (8502) → Socratic Dialogue
```

**Implementation**:
- Each dashboard is **fully independent** with its own data and visualizations
- **No cross-dashboard data integration** or summary views in admin
- Admin users navigate between dashboards using links/tabs
- Each dashboard maintains separate authentication/authorization
- Data remains siloed per assessment type

**Advantages**:
- ✅ Simpler implementation and maintenance
- ✅ Each dashboard has full functionality and independence
- ✅ No data duplication or synchronization issues
- ✅ Easier to scale and add new assessment dashboards
- ✅ Clear separation of concerns

**Admin Dashboard Focus**:
- Instance/server management
- User administration
- Quick navigation to assessment dashboards
- System monitoring and health checks

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: PROaCTIVE Expansion** (Priority 1)

**Tasks**:
1. ✅ Domain color-coding (DONE)
2. ✅ Completion analytics (DONE)
3. ⏳ Expand to 5 core domains (add Humility & Reflective Practice)
4. ⏳ Add sub-metrics to each domain (4 per domain = 20 total)
5. ⏳ Implement 8-item encounter checklist with completion tracking
6. ⏳ Add proficiency level calculations (Developing, Emerging, Proficient, Advanced)
7. ⏳ Add Socratic Components (WONDER, REFLECT, REFINE, RESTATE, REPEAT)
8. ⏳ Create detailed sub-metric visualizations
9. ⏳ Add speech metrics section (marked as optional/default values)

**Data Structure Changes**:
```python
# Add new domains to DOMAIN_COLORS
DOMAIN_COLORS = {
    "PRO_01": "#3498DB",  # Blue - Question Formulation
    "PRO_02": "#2ECC71",  # Green - Response Quality
    "PRO_03": "#E67E22",  # Orange - Critical Thinking
    "PRO_04": "#9B59B6",  # Purple - Humility & Partnership
    "PRO_05": "#E74C3C",  # Red - Reflective Practice
}

# Add encounter checklist
ENCOUNTER_ELEMENTS = [
    "chief_complaint",
    "hpi",
    "pmh",
    "social_history",
    "ros",
    "family_history",
    "surgical_history",
    "allergies"
]

# Add speech metrics
SPEECH_METRICS = ["volume", "pace", "pitch", "pauses"]
```

---

### **Phase 2: SIM-U Clarifications** (Priority 2)

**Pending Dr. Ford Input**:
1. Which INACSL Standards to add? (Recommend: Facilitation + Debriefing)
2. Confirm DASH tool implementation (6 elements, 7-point scale, faculty-only)
3. Should SIM-U also track Socratic measures during simulations?
4. Keep Professional Integrity as-is? (Recommend: YES)

**Once Confirmed**:
5. Add selected INACSL Standards with 0-4 rubric scale
6. Implement DASH tool in Faculty View
7. Update mock data generators
8. Add visualizations for new metrics

---

### **Phase 3: Admin Dashboard** (Priority 3)

**Confirmed Approach**: ✅ Distributed independent dashboards

**Tasks**:
1. ✅ Keep current instance management functionality
2. ✅ Keep user administration features
3. ⏳ Add clear navigation links to SIM-U and PROaCTIVE dashboards
4. ⏳ Improve dashboard cards with status indicators
5. ⏳ Add "Launch Dashboard" buttons with port indicators
6. ⏳ Optional: Add system health monitoring for each instance

---

### **Phase 4: Feedback Generation** (Priority 4)

**Tasks**:
1. Generate "What went well" feedback based on high scores
2. Generate "Areas for improvement" based on low scores
3. Provide specific recommendations per domain
4. Offer reflection questions to guide student learning
5. Track feedback over time to show improvement

---

## 📋 **SUMMARY OF ANSWERS**

### ✅ **Answered from PDFs**:
1. **Encounter Feedback**: 8-item binary checklist (Chief Complaint, HPI, PMH, Social History, ROS, Family History, Surgical History, Allergies)
2. **Speech Metrics**: 4 metrics (Volume, Pace, Pitch, Pauses) on 0-10 scale - **OPTIONAL/SECONDARY**
3. **Socratic Domains**: Expand from 4 to **5 domains** with sub-metrics
4. **Keep 4 domains?**: NO - Expand to 5, add Humility & Reflective Practice

### ⚠️ **Need Dr. Ford Input**:
1. **INACSL Standards**: Which ones to add beyond Professional Integrity?
2. **DASH Tool**: Confirm 6-element, 7-point scale implementation
3. **Faculty vs Student metrics**: Confirm same metrics, different views
4. **Professional Integrity**: Keep as-is in SIM-U? (Recommend: YES)
5. ✅ **Admin Dashboard**: CONFIRMED - Distributed independent dashboards with admin access to all

---

## 🎨 **VISUAL MOCKUP SUGGESTIONS**

### **PROaCTIVE Dashboard - New Sections**

**Section 1: Five Core Domains** (Replace current 4-domain cards)
```
┌─────────────────────────────────────────────────────────────────┐
│  Domain Summary Scores                                          │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│ 🔵 Question │ 🟢 Response │ 🟠 Critical │ 🟣 Humility │ 🔴 Reflect│
│ Formulation │   Quality   │  Thinking   │ Partnership │  Practice│
│    4.5/5.0  │    4.5/5.0  │    4.0/5.0  │    4.5/5.0  │   3.5/5.0│
│   Advanced  │   Advanced  │ Proficient  │   Advanced  │Proficient│
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

**Section 2: Encounter Completeness** (NEW)
```
┌─────────────────────────────────────────────────────────────────┐
│  Encounter Documentation Completeness           6/8 items (75%) │
├─────────────────────────────────────────────────────────────────┤
│  ✅ Chief Complaint      ✅ HPI                 ✅ PMH          │
│  ✅ Social History       ✅ ROS                 ❌ Family Hx    │
│  ❌ Surgical History     ✅ Allergies                           │
└─────────────────────────────────────────────────────────────────┘
```

**Section 3: Socratic Components** (NEW - Quick Visual)
```
┌─────────────────────────────────────────────────────────────────┐
│  Socratic Dialogue Components (0-5.0 scale)                     │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   WONDER    │   REFLECT   │   REFINE    │  RESTATE    │  REPEAT │
│   🔵●●●●●   │   🔵●●●●●   │   🔵●●●●○   │   🔵●●●●●   │🔵●●●●○  │
│    4.5      │     4.5     │     4.0     │     4.5     │   4.0   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

**Section 4: Speech Quality** (NEW - Optional)
```
┌─────────────────────────────────────────────────────────────────┐
│  Speech Quality Metrics (0-10 scale)    ⚠️ Using default values │
├─────────────┬─────────────┬─────────────┬─────────────────────┬─┤
│   Volume    │    Pace     │    Pitch    │      Pauses         │ │
│   8.0/10    │   8.0/10    │   8.0/10    │      8.0/10         │ │
│   Good      │    Good     │    Good     │       Good          │ │
└─────────────┴─────────────┴─────────────┴─────────────────────┴─┘
│  ℹ️ Audio analysis not available. Scores reflect typical        │
│     performance. Upload audio for detailed speech analysis.     │
└─────────────────────────────────────────────────────────────────┘
```

---

**Generated**: November 19, 2025  
**Source**: Socratic Dialogue PDFs + Implementation Questions  
**Status**: Ready for Dr. Ford meeting to confirm SIM-U and Admin decisions  
**Next Step**: Implement PROaCTIVE Phase 1 changes based on PDF specifications
