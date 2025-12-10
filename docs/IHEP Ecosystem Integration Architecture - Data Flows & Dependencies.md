# IHEP Ecosystem Integration Architecture - Data Flows & Dependencies
**Date:** December 10, 2025  
**Status:** Cross-Solution Architecture Definition

---

## OVERVIEW

This document defines how the three solutions integrate at the data and operational level, specifying:
1. Data flows between solutions
2. State dependencies and consistency guarantees
3. Real-time feedback loops
4. Emergency handling and fallback mechanisms

---

## SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                        IHEP ECOSYSTEM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐        ┌──────────────────┐                │
│  │  Healthcare API  │        │  Patient Data    │                │
│  │  - Lab results   │───────→│  Lake (BigQuery) │                │
│  │  - Appointments  │        │  - Clinical      │                │
│  │  - Meds refills  │        │  - Behavioral    │                │
│  └──────────────────┘        └────────┬─────────┘                │
│                                       │                           │
│                                       ↓                           │
│                          ┌────────────────────────┐              │
│                          │  [SOLUTION 3]          │              │
│                          │ Twin State Manager     │              │
│                          │ - Update protocols     │              │
│                          │ - Consistency checks   │              │
│                          │ - Signal generation    │              │
│                          └────────┬───────────────┘              │
│                                   │                              │
│           ┌───────────────────────┼───────────────────────┐     │
│           ↓                       ↓                       ↓     │
│  ┌─────────────────────┐ ┌──────────────────┐ ┌──────────────┐ │
│  │ Morphogenetic Sigs  │ │ Patient Twin     │ │  Org Twin    │ │
│  │ - φ_E (error)       │ │ State Store      │ │  State Store │ │
│  │ - φ_L (latency)     │ │                  │ │              │ │
│  │ - φ_S (spare)       │ │ 6-layer model    │ │ Aggregates   │ │
│  └─────────────────────┘ └──────────────────┘ └──────────────┘ │
│           │                      │                       │      │
│           ↓                      ↓                       ↓      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [SOLUTION 1] Recursive Loop Closure                     │  │
│  │  - Compute outcomes: O₁, O₂, O₃, O₄, O₅                 │  │
│  │  - Correlate to signals: signal(t-τ) → outcome(t)       │  │
│  │  - Fit predictive model: R² metric                       │  │
│  │  - Generate hypotheses for optimization                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                                                     │
│           ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Research Team (Theorist, Experimenter, Analyst)         │  │
│  │  - Test parameter variations on outcome prediction       │  │
│  │  - New signal thresholds → higher outcome R²             │  │
│  │  - Adoption gate + human review                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                                                     │
│           ↓                                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Morphogenetic Framework SDN Network                     │  │
│  │  - Agents: Weaver, Builder, Scavenger                    │  │
│  │  - Execute based on optimized E, L, S thresholds         │  │
│  │  - Generate interventions for patients                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                                                     │
│           └──────────────┬──────────────────────────────────┘   │
│                          ↓                                      │
│           ┌──────────────────────────────────────────┐         │
│           │  [SOLUTION 2]                           │         │
│           │  3D Visualization Dashboard             │         │
│           │  - Network topology (3D mesh)           │         │
│           │  - Field visualization (E,L,S colors)   │         │
│           │  - Patient cohort cloud                 │         │
│           │  - Intervention animations              │         │
│           │  - Real-time updates (WebSocket)        │         │
│           └──────────────────────────────────────────┘         │
│           ↑                                                     │
│           │ Stakeholders observe system operation              │
│           │ Leaders understand: "Which interventions work?"    │
│           │                                                     │
└─────────────────────────────────────────────────────────────────┘

Feedback loop closes:
  Patient outcomes improve → Twin state updates → Signals update
  → RLC detects improvement → Research Team learns → Framework optimizes
  → New thresholds → Better interventions → Better patient outcomes
```

---

## DETAILED DATA FLOWS

### Flow 1: Clinical Data → Twin State → Signals

```
Time sequence:

T = T0
  Healthcare API publishes new lab result: VL = 45 copies/mL
  
T = T0 + 100ms
  Twin State Manager receives event via Kafka
  {
    patient_id: "p_12345",
    event_type: "lab_result",
    viral_load: 45,
    timestamp: T0,
    source: "quest_labs_api"
  }

T = T0 + 200ms
  Twin State Manager updates patient twin:
  
  Before:
    clinical_health.viral_load = 200 (last measurement 40 days ago)
    
  After:
    clinical_health.viral_load = 45
    clinical_health.last_lab_update = T0
    
  Recomputes signal E(p, T0):
    clinical_error = 0.3 (45 copies = undetectable range)
    adherence_error = 0.22 (from recent refill data)
    engagement_error = 0.05 (strong app usage)
    system_error = 0.0 (all appointments attended)
    
    E_new = 0.40*0.22 + 0.35*0.3 + 0.15*0.05 + 0.10*0 = 0.18

T = T0 + 250ms
  Old signal: E_old = 0.35 (based on old data: VL=200)
  New signal: E_new = 0.18 (based on new data: VL=45)
  
  Change: ΔE = -0.17 (17% reduction, patient improving!)
  
  Framework agents detect:
    "E signal for patient p_12345 dropped significantly"
    "Intervention may have succeeded - patient likely responding to therapy"

T = T0 + 300ms
  Twin state committed atomically:
  - Clinical health layer ✓
  - Signal values ✓
  - Metadata timestamps ✓
  - Audit log entry ✓
  
  Event published: "twin-updated: p_12345"

T = T0 + 400ms (asynchronous)
  Recursive Loop Closure engine receives signal:
  - Old outcome prediction for this patient based on E_old = 0.35
  - New outcome prediction based on E_new = 0.18
  - Observed actual adherence from this month
  - Validates: "Did improved E signal predict improved adherence?"
  - If yes: correlation confirmed, model quality improves
```

### Flow 2: Outcome → Correlation Analysis → Framework Optimization

```
Time sequence (daily cycle):

DAILY 0000 UTC - Outcome Data Collection
  
  For all 1,247 active patients:
    - Fetch last 7 days of:
      - Twin state snapshots
      - Signal values E(p,t), L(p,t), S(p,t)
      - Patient behaviors (logins, medication adherence)
      - Clinical metrics (viral load, CD4)
    
    - Compute outcomes O₁-O₅
    - Store in outcome warehouse
    
  Result: (1,247 patients) × (7 days) = 8,729 (patient, outcome, signals, time)

DAILY 0100 UTC - Correlation Analysis Starts
  
  RLC Theorist agent:
    For each lag τ ∈ {0, 1, 3, 7, 14, 30}:
      For each (signal_s ∈ {E, L, S}, outcome_o ∈ {O₁-O₅}):
        
        correlation(s, o, τ) = corr(Signal_s(t-τ), Outcome_o(t))
        
        Example: corr(E(t-7d), O₁(t)) = -0.72
                "Errors 7 days ago strongly predict poor adherence today"

DAILY 0200 UTC - Predictive Model Retraining
  
  RLC Analyst:
    Select top 10 signal-outcome pairs (by |correlation|)
    
    Fit multiple regression:
      O₁_pred = 0.85 - 0.42*E(t-7) + 0.28*S(t-3) - 0.15*L(t-14)
    
    Evaluate on holdout set:
      R² = 0.73 (explains 73% of adherence variance)
      RMSE = 0.08
      MAE = 0.06

DAILY 0300 UTC - Hypothesis Generation (New!)
  
  RLC Theorist, using new research objective:
    combined_value = 0.60·signal_quality + 0.40·outcome_prediction
  
  Identifies:
    "Current E threshold (0.70) is good for signal quality"
    "But L threshold (0.35) could be tighter to improve prediction"
    "If L threshold → 0.28, predicted R² would improve by 0.02"
    
  Generates hypothesis:
    "Test thetaL = 0.28 instead of 0.35"
    Predicted improvement in outcome_prediction: 0.02
    Risk to signal_quality: 0.005 (acceptable)

DAILY 0400-2200 UTC - Experimenter runs tests
  
  5 parallel AB tests:
    1. Control: thetaE=0.005, thetaL=0.35, thetaS=0.30 (current)
    2. Candidate: thetaE=0.005, thetaL=0.28, thetaS=0.30 (hypothesis 1)
    3. Candidate: thetaE=0.006, thetaL=0.35, thetaS=0.30 (hypothesis 2)
    ... etc
  
  Each experiment:
    - Runs on synthetic + real interaction data
    - 1 hour duration
    - Measures signal_quality and outcome_prediction_R²
    - Collects 144,000 data points

DAILY 2300 UTC - Decision Gate
  
  Analyst report on best experiment:
    "Hypothesis 2 (thetaL=0.28) succeeded:
     - Signal quality: maintained (was 0.853, now 0.851, -0.2%)
     - Outcome R²: improved (was 0.71, now 0.74, +4.2%)
     - Overall combined_value: +2.1%
     - p-value: 0.008 (highly significant)
     - Recommendation: ADOPT"
  
  Human Review (Operations Lead):
    "Do we approve thetaL: 0.35 → 0.28?"
    Decision: APPROVE
  
  Update Morphogenetic Framework:
    MorphoFramework.constants.thetaL = 0.28
    Timestamp: 2025-12-10T23:15:32Z
    Change_log entry: "L threshold optimized for outcome prediction"

NEXT MORNING - Framework Operates with New Thresholds
  
  Weaver agent with thetaL = 0.28 (tighter latency tolerance):
    More sensitive to delays → earlier action
    Expected: "Patient latency issues caught sooner → better outcomes"
    
  Measured over next week:
    "L threshold change → 2.1% fewer late appointments"
    "2.1% fewer late → O₁ adherence improved by 0.8%"
    Confirmation: Hypothesis validated in production!
```

### Flow 3: 3D Visualization Real-Time Updates

```
Dashboard Client (browser):

  Every 1 second:
    1. Query WebSocket for latest:
       - Morphogenetic field values
       - Patient outcome values
       - Agent action log
    
    2. Backend sends delta (changes only):
       {
         "timestamp": T,
         "field_updates": [
           {node_id: 5, phi_E: 0.25, phi_L: 0.42, phi_S: 0.18},
           {node_id: 12, phi_E: 0.08, phi_L: 0.19, phi_S: 0.65},
           ...
         ],
         "patient_updates": [
           {patient_id: "p_100", pos_x: 0.78, pos_y: 0.91, pos_z: 0.45, health_color: rgb(50, 200, 30)},
           ...
         ],
         "actions": [
           {timestamp: T, agent: "Weaver", action: "reroute", flow_count: 45, from_path: "old", to_path: "new"}
         ]
       }
    
    3. Three.js renderer:
       - Update mesh vertex colors (field visualization)
       - Update point cloud positions (patient cohort)
       - Play animation for action (rerouting as traffic flow)
    
    4. User sees:
       - Red intensity at node 5 (high error)
       - Yellow at node 5 (high latency)
       - Green at node 12 (good capacity)
       - Orange glow animation showing Weaver reroute in action
       - Patient cloud centroid moved up-right (better outcomes)

Executive Dashboard (stakeholder):
  
  Top-level metrics update every 10 seconds:
    - System Health Score: 76.2% (green)
    - Patient Composite Outcome: 0.819 (target 0.85)
    - Active Interventions: 12
    - Framework Optimization Progress: "R² improved 0.71 → 0.74 this week"
    
  Drill-down available:
    - Click "12 active interventions" → see patient-level details
    - Click 3D network → see which regions have issues
    - Click outcome metrics → see outcome prediction model insights
```

---

## CONSISTENCY & DEPENDENCY GUARANTEES

### State Consistency Checkpoints

```
Invariant Validation (Hourly):

SYSTEM STATE TRIPLE (Twin, Signals, Outcomes):
  T_p(t) = Twin state at time t
  S_p(t) = Signals computed from T_p(t)
  O_p(t) = Outcomes measured from patient

Must maintain:
  1. Signals ≡ function(Twin)
     ✓ If Twin changes → Signals recomputed immediately
     
  2. Twin ≡ Outcomes metadata
     ✓ Twin.last_clinical_update reflects latest outcome collection
     
  3. Aggregates ≡ Per-patient values
     ✓ E_org.mean = mean(E_p for all p in org)
     
  4. No divergence in correlation model
     ✓ Predicted_outcome ≈ Actual_outcome (R² > 0.70)

Validation procedure (every hour):
  For each (patient_p, timestamp_t):
    - Recompute E, L, S from raw data
    - Compare to stored values
    - If |delta| > threshold → flag DIVERGENT
    - Alert operations if critical divergence detected
    - Auto-correct within 24 hours
```

### Dependency Ordering

```
Critical Path for Outcome Improvement:

1. NEW CLINICAL DATA arrives
   (lab result, appointment attended, etc.)
   
2. TWIN STATE updates
   (Solution 3 synchronization)
   Duration: <1 second
   
3. SIGNALS recompute
   (E, L, S from updated twin)
   Duration: <1 second
   
4. MORPHOGENETIC AGENTS act
   (Framework responds to signals)
   Duration: seconds to minutes
   
5. PATIENT OUTCOMES measured
   (adherence, viral load, engagement)
   Duration: minutes to hours
   
6. RECURSIVE LOOP CLOSURE detects
   (correlation analysis)
   Duration: daily
   
7. RESEARCH TEAM OPTIMIZES
   (new thresholds tested)
   Duration: hourly experiments
   
8. FRAMEWORK IMPROVES
   (better parameters adopted)
   Duration: depends on validation

Critical Path Slack:
  Step 1→2: 0% slack (must be immediate)
  Step 2→3: 0% slack (deterministic calculation)
  Step 3→4: 10% slack (agents can queue decisions)
  Step 4→5: high slack (patient outcomes inherently delayed)
  Step 5→6: 0% slack (as soon as data available)
  Step 6→7: 0% slack (scheduled daily)
  Step 7→8: 20% slack (human review gate)

Bottleneck: Patient outcome measurement (slowest step)
  Outcome measured every 7 days (minimum)
  Therefore: Optimization cycle is weekly minimum
  Can improve frequency with more frequent assessments
```

---

## FAILURE MODES & RECOVERY

### Scenario 1: Clinical Data Quality Issue

```
Event: New lab result arrives with impossible value
  Patient viral_load = -50 copies/mL (negative!)
  
Handling:
  
  Twin State Manager validation (Step 1 of update protocol):
    ✗ Fail: viral_load must be ≥ 0
    Action: Reject update, log error
    Alert: Notify clinical team
    Result: Twin state unchanged (safe failure)
  
  Clinical Team:
    "Why negative? Query lab system for error"
    Options:
      a) Lab system was wrong → correct and resubmit
      b) Data corruption → investigate integration
      c) False positive result → clinical review
    
  Recovery:
    Once corrected, resubmit with timestamp
    Twin state updates normally
    Signals reflect corrected data
```

### Scenario 2: Signal-Outcome Correlation Collapses

```
Event: Recursive Loop Closure detects R² dropped from 0.73 → 0.52
       Model no longer predicts patient outcomes
  
Root Cause Analysis:
  
  1. Check: Did patient population change?
     - New enrollment cohort added? (different demographics)
     - High-risk patients churned? (selection bias)
     - Outcome measurement changed? (definition shift)
  
  2. Check: Did signals become noisy?
     - Framework parameters drift?
     - Data quality degradation?
     - System state divergence?
  
  3. Check: Did interventions change effectiveness?
     - New peer navigators less skilled?
     - Clinic workflow changed?
     - External factors (policy, season)?
  
  Recovery Actions (in priority order):
    a) If population changed:
       → Rebuild model on sub-cohorts
       → Re-establish baseline for new population
       → Continue optimization from new baseline
    
    b) If data quality degraded:
       → Investigate source (EHR, app, pharmacy)
       → Validate against manual samples
       → Implement quality checks
       → Temporary: Use conservative predictions
    
    c) If interventions less effective:
       → Pause Research Team optimization (preserve known-good)
       → Investigate operational root causes
       → Retrain/support staff as needed
       → Restart optimization once stable
```

### Scenario 3: Three.js Visualization Fails

```
Event: Dashboard shows stale data
       3D field visualization stops updating
       Patient point cloud hasn't moved in 30 minutes
  
Handling:
  
  Client-side (Browser):
    Every update packet:
      Check: Is timestamp_new > timestamp_old?
      If stale (>10 seconds old):
        - Visual indicator: Yellow warning badge
        - Data frozen: Don't animate stale positions
        - Offer: "Refresh" button
  
  Server-side (Backend):
    Monitor WebSocket publication rate:
      Expected: 1 message per second
      Actual: 0.2 messages per second
      Alert: "Visualization feed degraded"
    
    Root cause:
      Option 1: Field computation service down?
        → Check service health
        → Restart if needed
        → Publish cached last-known state while restarting
      
      Option 2: Network latency spike?
        → Monitor network metrics
        → If recovered: continue normal operation
        → If persistent: activate degraded mode
      
      Option 3: Database query slow?
        → Check BigQuery performance
        → Activate read cache if available
        → Temporarily reduce update frequency to 1/5 seconds
  
  Fallback Strategy:
    If WebSocket fails:
      Client switches to HTTP polling (slower but reliable)
      Update frequency: 5 seconds instead of 1 second
      User experience: Slightly choppy but readable
    
    If HTTP polling fails:
      Display last-known state as snapshot
      "Last update: 2 minutes ago"
      Offer manual "Refresh" button
    
    SLA: Dashboard <15 minutes stale, or alert escalated
```

---

## CROSS-SOLUTION METRICS & MONITORING

### Unified Monitoring Dashboard

```
Tier 1: System Health (Real-time)
├─ Recursive Loop Closure
│  ├─ Outcome R² (target ≥0.70): currently 0.74 ✓
│  ├─ Correlation count (target ≥3): currently 8 ✓
│  └─ Monthly improvement (target ≥1.5%): currently +2.1% ✓
│
├─ 3D Geometry Integration
│  ├─ Dashboard FPS (target ≥60): currently 58 ⚠
│  ├─ WebSocket latency (target <100ms): currently 72ms ✓
│  └─ Client accuracy (target 100%): currently 99.8% ✓
│
└─ Twin Synchronization
   ├─ Consistency violations (target zero): currently 0 ✓
   ├─ Max divergence (target <5%): currently 2.1% ✓
   └─ Update latency (target <1s): currently 0.32s ✓

Tier 2: Patient Impact (Daily)
├─ Adherence (target ≥0.90): 0.83 (↑0.02 this week)
├─ Viral suppression (target ≥0.95): 0.76 (↑0.03 this week)
├─ Mental health (target ≥0.80): 0.74 (→ stable)
├─ Engagement (target ≥0.75): 0.77 (↑0.01 this week)
└─ Utilization (target ≥0.85): 0.81 (↑0.02 this week)

Tier 3: Research Progress (Weekly)
├─ Experiments run (target: 5+ per day): 28 this week
├─ Hypothesis success rate (target ≥40%): 46% this week
├─ Parameter optimizations adopted: 2 this week
└─ Cumulative R² improvement: +0.05 (since week 1)
```

### Alerting Rules

```
CRITICAL ALERTS (immediate escalation):
  1. Twin consistency violation detected
     → Trigger automatic recovery
     → If recovery fails: page on-call engineer
  
  2. RLC outcome prediction R² drops >0.10
     → Pause Research Team optimization
     → Investigate root cause
     → Manual review before resuming
  
  3. Framework intervention success rate <70%
     → Analyze failed interventions
     → Check: Are signals correct?
     → Check: Are agents responding properly?
  
  4. Patient health decline in tracked cohort (>10% negative shift)
     → Alert clinical team immediately
     → Do outcomes match predictions?
     → If divergence: investigate external factors

WARNING ALERTS (daily review):
  1. Dashboard update latency >200ms (degraded user experience)
  2. RLC model accuracy <60% (model drift)
  3. Twin state divergence >3% (early consistency warning)
  4. Framework FPS <45 (performance degradation)

INFO ALERTS (logged, weekly review):
  1. New correlation discovered (research value)
  2. Parameter optimization completed (operational info)
  3. Data quality improved (positive trend)
```

---

## CONCLUSION

The three solutions integrate at multiple levels:

1. **Data Flow Level**
   - Clinical reality → Twin state (Solution 3)
   - Twin state → Signals (Solution 3)
   - Signals → Framework agents → Interventions
   - Outcomes → Correlation analysis (Solution 1)

2. **Consistency Level**
   - Twin state invariants guarantee signal correctness
   - Outcome predictions validate signal quality
   - Divergence detection triggers automatic corrections

3. **Optimization Level**
   - RLC detects which signal-outcome relationships exist
   - Research Team optimizes thresholds for outcome prediction
   - Framework improves → Better interventions → Better outcomes

4. **Observability Level**
   - 3D visualization makes system state visible
   - Stakeholders understand what system is doing
   - Decisions informed by visual insights

Together, these solutions create a **completely integrated ecosystem** where clinical reality, computational state, and visual understanding are permanently synchronized and continuously improving.

**The system is alive, self-aware, and learning.**
