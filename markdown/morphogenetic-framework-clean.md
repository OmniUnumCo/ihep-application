# MORPHOGENETIC FRAMEWORK - PRODUCTION SPECIFICATION v3.0
# UTF-8 CLEAN - NO EMOJIS - READY FOR EXECUTION
# Date: November 10, 2025

## EXECUTIVE SUMMARY

Complete production-hardened SDN self-healing framework with all corrections applied.

Core Concept:
- Signals (E, L, S) normalized to [0,1] every 1s tick
- Fields computed via inject + diffuse + decay
- Three operational agents (Weaver, Builder, Scavenger) respond to field state
- Three research agents (Empiricist, Theorist, Optimizer) continuously optimize thresholds
- Cross-coupling creates morphogenetic anticipation
- Stability proven via Lyapunov + spectral analysis

---

## PART 1: SIGNALS (NORMALIZED [0,1])

### Error Signal (E)

Raw measurement:
  E_raw = (crc_errors + packet_drops + retransmits) / total_packets

Baseline adaptation:
  E_baseline = EWMA(E_raw) over 1-hour window
  Recalculate every 10 minutes

Normalization:
  E = (E_raw - E_baseline) / p95(E_baseline)
  Clamp to [0, 3] for outlier protection

Per-link adaptive:
  Datacenter fiber: E_threshold = 0.0001 (0.01% very low noise)
  WAN link: E_threshold = 0.005 (0.5% higher ambient error rate)

Data sources:
  sFlow, NetFlow, IPFIX, INT (in-band telemetry), gNMI/gRPC

---

### Latency Signal (L)

Raw measurement:
  L_raw = queue_delay_ms (from INT) OR RTT/2 (from ICMP/TCP)

SLO calculation:
  L_SLO = p50(L_raw) over stable periods (at least 1 hour)

Normalization:
  L = L_raw / L_SLO
  Clamp to [0, 5] (5x SLO is unacceptable)

Dynamic thresholds (recalculate every 10 minutes):
  theta_L_base = p95(L) over last 1-hour window
  theta_L_hot = p99(L) over last 1-hour window

Per-link variation:
  High-priority links have tighter SLOs
  Low-priority links have more relaxed SLOs

Data sources:
  INT (P4 switches), Performance API, sFlow samples

---

### Spare Capacity Signal (S)

Raw measurement:
  S_raw = 1 - (current_utilization_bps / link_capacity_bps)

Capacity weighting:
  S_weighted = S_raw * (link_capacity / max_capacity_in_network)

Normalization:
  S = S_weighted (already in [0, 1])

Range:
  0 = no capacity available
  1 = full capacity available

Thresholds:
  theta_S_high = 0.70 (70% capacity available)
  theta_S_low = 0.20 (20% capacity available, constrained)
  theta_S_critical = 0.10 (10% capacity, emergency)

Data sources:
  Interface counters from gNMI, sFlow samples

---

## PART 2: FIELD DYNAMICS

### Discrete Update Rule

Formula:
  phi(t+1) = (1-beta) * phi(t) + alpha * source(t) + D * L_norm * phi(t) + C * X(phi)

Component breakdown:

  (1-beta) * phi(t)
    Persistence term (beta = 0.2, decay factor)
    Allows signal to "remember" previous state

  alpha * source(t)
    Injection of new measurements
    alpha values: k_inject_E = 1.0, k_inject_L = 0.8, k_inject_S = 0.6

  D * L_norm * phi(t)
    Diffusion across network graph
    D = min(D_base, 0.25 / deg_max) for stability
    L_norm = I - D^(-1/2) * A * D^(-1/2) (degree-normalized Laplacian)

  C * X(phi)
    Cross-coupling terms (morphogenetic)
    Signals influence each other

---

### Injection (Alpha Coefficients)

k_inject_E = 1.0
  Error signal most critical, full injection

k_inject_L = 0.8
  Latency damped slightly to smooth oscillations

k_inject_S = 0.6
  Capacity most damped to prevent thrashing

Rationale:
  Error detection critical for failures
  Latency less critical but important
  Capacity changes most damped (inertia)

---

### Diffusion (Laplacian Matrix)

Network graph representation:
  V = set of switches/routers/links
  A = adjacency matrix (A[i,j] = 1 if link i-j exists)
  D = degree matrix (D[i,i] = sum of A[i,j] over j)

Normalized Laplacian construction:
  Step 1: Compute D^(-1/2) (diagonal, entry [i,i] = 1/sqrt(degree[i]))
  Step 2: L_norm = I - D^(-1/2) * A * D^(-1/2)
  Step 3: Verify spectrum: eigenvalues lambda in [0, 2]

Diffusion coefficients (base):
  D_E = 0.15
  D_L = 0.20
  D_S = 0.10

Spectral stability cap (CRITICAL):
  D_actual = min(D_base, 0.25 / deg_max)

  Where deg_max = maximum node degree in current graph

  Rationale:
    Discrete stability requires all eigenvalues of (I + D*L_norm) < 1
    L_norm eigenvalues in [0,2], so need D * 2 < 1
    Conservative: D < 0.5
    Safe margin: D <= 0.25/deg_max

Safe/Fast modes:
  Safe mode:
    D_actual = 0.15 / deg_max
    Slower diffusion, more stable
    Use during crisis or initial deployment

  Fast mode:
    D_actual = 0.25 / deg_max
    Faster response, near stability limit
    Use during normal operation

---

### Decay (Lambda Coefficients)

Lambda values:
  lambda_E = 0.05
  lambda_L = 0.08
  lambda_S = 0.03

Decay formula:
  phi_decay = phi(t) * exp(-lambda * delta_t)
  where delta_t = 1 second

Time constants (1/lambda):
  tau_E = 1/0.05 = 20 seconds
  tau_L = 1/0.08 = 12.5 seconds
  tau_S = 1/0.03 = 33 seconds

Physical meaning:
  Error signal decays fastest (errors are transient)
  Latency signal decays medium (recovers in ~12s)
  Capacity signal decays slowest (inertia of resource allocation)

---

### Cross-Coupling (Morphogenetic Anticipation)

Basic coupling matrix:

  dE/dt += 0 * L + 0 * S
  dL/dt += 0.15 * E (errors raise latency via retransmits)
  dS/dt += -0.10 * E (errors consume capacity via retry storms)

Matrix form:
  X(phi) = [[0,      0,      0     ],     [E]
            [0.15,   0,      0     ],  *  [L]
            [-0.10,  0,      0     ]]     [S]

Coupling constants:
  kappa_LE = 0.15 (error to latency coupling)
  kappa_SE = 0.10 (error to capacity coupling)

  Constraints:
    Must be << base inject gains (0.1 - 0.2 of base)
    Keeps cross-influence stable but noticeable

Physical interpretation:
  When error rate E spikes (network congestion):
  - Retransmits increase, which increases latency L
  - Retry storms consume available capacity S
  - System anticipates cascade BEFORE full propagation

Benefit:
  System acts proactively:
    E spike detected -> L field rises -> Weaver reroutes BEFORE page is on fire
    E spike detected -> S field drops -> Builder avoids expanding doomed path

---

## PART 3: AGENT TRIGGERS (THRESHOLDS)

### Detection Windows

Consecutive ticks for triggering:
  hot state: 3 consecutive ticks above theta_hot
  very_hot state: 2 consecutive ticks above theta_very_hot

Sliding window:
  10 ticks (10 seconds) for percentile calculation

---

### Error Thresholds

theta_E_base:
  Definition: 3 sigma above per-link EWMA baseline
  Adaptive: Recalculates every 10 minutes
  Per-link: Varies by optics type and history

  Example values:
    Pristine DC fiber: 0.0001 (0.01%)
    Aging DC fiber: 0.0005 (0.05%)
    Noisy WAN: 0.005 (0.5%)
    Satellite/LTE: 0.01 (1%)

theta_E_hot:
  Definition: 5 sigma above per-link baseline
  Typical: 2-5 times theta_E_base depending on baseline

theta_E_very_hot:
  Definition: 10 sigma above per-link baseline
  Typical: 3-10 times theta_E_hot
  Triggers emergency responses (Scavenger)

---

### Latency Thresholds

theta_L_base:
  Definition: p95(L) over last 1-hour window
  Dynamic: Recalculates every 10 minutes
  Per-link: Can vary 10-50% depending on link type

theta_L_hot:
  Definition: p99(L) over last 1-hour window
  Typical: 1.5-2.0 times theta_L_base
  Triggers Weaver rerouting

theta_L_very_hot:
  Definition: p99.9(L) over last 1-hour window
  Typical: 2-3 times theta_L_hot
  Rarely used, represents extreme degradation

---

### Capacity Thresholds

theta_S_high = 0.70
  Definition: At least 70% spare capacity available
  Triggers: Builder capacity expansion (if E also high)

theta_S_low = 0.20
  Definition: Only 20% spare capacity available
  Triggers: Scavenger isolation (if E very high)

theta_S_critical = 0.10
  Definition: Only 10% spare capacity available
  Action: Emergency alert, all expansion gated

---

## PART 4: OPERATIONAL AGENTS

### WEAVER (Traffic Engineering / Load Balancer)

Role:
  Dynamically reroute flows to lower-latency paths

Trigger condition:
  L_current > theta_L_hot AND (S_alt - S_current) >= 0.1

  Explanation:
    L_current = latency on current path
    S_alt = spare capacity on alternative path
    S_current = spare capacity on current path

  Critical fix from v2.0:
    OLD: Î”S = S(t) - S(t-5) [WRONG - temporal trend]
    NEW: Î”S = S_alt - S_current [CORRECT - spatial difference]

Action:
  Controller API: POST /sdn/ecmp_weights
  {
    "flow_hash_range": [0.7, 0.9],
    "new_path": "alt_path_id"
  }

  ECMP weight adjustment:
    w_alt = w_alt * 1.15
    w_current = w_current * 0.85
    Normalize after adjustment

  Gradual shift strategy:
    Don't shift all 15% at once
    Apply 5% increments every 2 ticks
    Prevents packet reordering and loss

Hysteresis (anti-thrashing):
  Cooldown: 10 ticks (10 seconds) after action
  Revert condition: L_current < theta_L_hot - 0.05 for 5 consecutive ticks
  Rationale: Prevents ping-pong between paths

Parameters:
  shift_fraction = 0.10 to 0.20 (10-20%)
  increment_per_tick = 0.05 (5%)
  min_delta_S_spatial = 0.10
  epsilon_hysteresis = 0.05
  cooldown_ticks = 10

Gradient following (smoothness):
  Compute gradient: grad_L = [L_neighbor1 - L_current, L_neighbor2 - L_current, ...]
  Select: Neighbor with most negative gradient (steepest descent)
  Benefit: Smooth load redistribution instead of hard cutover

---

### BUILDER (Capacity Expansion)

Role:
  Bring up additional capacity or upgrade QoS when errors occur with spare headroom

Trigger condition:
  E_current > theta_E_hot
  AND S_current > theta_S_high
  AND neighbor_quorum_passes
  AND controller_grants_budget

Neighbor quorum (topological consensus):
  q_topo = (count of neighbors with E > theta_E_hot) / (count of total neighbors)
  
  Trigger rule:
    IF q_topo >= 0.60 OR absolute_count >= 2:
      THEN proceed to signal vote

  Tie-breaker (if 0.50 <= q_topo < 0.70):
    q_signal = 0.5*vote_E + 0.3*vote_L + 0.2*vote_S
    Require: q_signal >= 0.67

  Rationale:
    Topological quorum prevents false positives from local sensor noise
    Requires consensus from adjacent nodes that THEY are also experiencing errors
    Signal vote only used to break borderline cases

Actions (in priority order):
  1. Bring up LAG (Link Aggregation Group) member if available
  2. Activate secondary equal-cost path
  3. Increase QoS priority for affected flows
  4. If all exhausted, emit alert for operator intervention

Controller budget mechanism (thundering herd prevention):
  Controller maintains global budget token pool
  Each expansion requires a valid token (60 second lease)
  Rate limiting:
    Max 1 token per node per minute
    Global cap: 20% of network nodes expanding simultaneously
    Backpressure: If token denied, node waits 30 seconds and retries

Rate limits:
  Per node: 1 expansion per minute
  Per window: Max 5 expansions in any 60-second window
  Cooldown after max: 30 ticks (30 seconds)

Hysteresis:
  Cooldown: 30 ticks after hitting rate limit
  Revert condition: E < theta_E_hot - epsilon AND utilization < 60% for 20 ticks
  Action on revert: Deactivate extra capacity gradually

Parameters:
  capacity_increment = 1 (1 LAG member or 1 equal-cost path)
  quorum_threshold_topology = 0.60
  quorum_threshold_signal = 0.67
  budget_lease_duration_seconds = 60
  global_expansion_cap_percent = 0.20

---

### SCAVENGER (Fault Isolation / Circuit Breaker)

Role:
  Drain and disable failing links with exponential backoff recovery

Trigger condition:
  E_current > 2 * theta_E_hot
  AND S_current < theta_S_low

  Rationale:
    Very high error rate (over 2x hot threshold)
    AND severely constrained capacity
    = Link in crisis, isolate immediately

Action sequence:

  Phase 1 - Drain (5 seconds):
    Controller marks link weight = 0
    Gracefully drains existing flows
    BGP route withdrawal (if inter-AS link)
    LSP teardown (if MPLS LSP)

  Phase 2 - Disable (quarantine):
    Link administratively disabled
    Circuit breaker state -> OPEN
    No traffic flows

Circuit breaker FSM:

  CLOSED (normal operation):
    Link active, traffic flows normally
    Trigger on failure: E > 2*theta_E_hot AND S < theta_S_low

  OPEN (quarantined):
    Link disabled, no traffic
    Minimum wait: 30 seconds (initial_backoff)
    Then transition to HALF_OPEN

  HALF_OPEN (testing):
    Sending periodic probe packets
    Measuring E and latency on probes
    If probes successful: transition to CLOSED
    If probes fail: return to OPEN with doubled backoff

Exponential backoff for probes:

  Formula: t_probe = initial_backoff * 2^(attempt_count)
  Sequence: 30s, 60s, 120s, 240s, 300s, 300s, ...
  Max backoff: 300 seconds (5 minutes)

  Rationale:
    Prevents oscillation from repeatedly probing unstable link
    Gives hardware time to recover
    Each failure doubles wait time

Optics/CRC/FEC pre-release checklist (6 checks):

  1. RX optical power within manufacturer spec (DOM API)
  2. TX optical power within manufacturer spec
  3. Temperature < 70 degrees Celsius
  4. CRC error rate < theta_E_low for 10 consecutive probes
  5. FEC uncorrectable error count = 0
  6. Manual operator approval if link was critical (optional gate)

  Probe mechanism:
    Send 100 ICMP or BFD probes at 10ms intervals
    Measure packet loss rate, latency, jitter
    Calculate E based on results

Gradual reintegration:

  Step 1 - Cautious (weight 0.1 = 10% traffic):
    Stable for 60 seconds -> advance to Step 2
    If E > theta_E_hot during Step 1 -> return to OPEN

  Step 2 - Moderate (weight 0.5 = 50% traffic):
    Stable for 120 seconds -> advance to Step 3
    If E > theta_E_hot during Step 2 -> return to OPEN with doubled backoff

  Step 3 - Full (weight 1.0 = 100% traffic):
    Link fully reintegrated
    Circuit breaker state -> CLOSED

Parameters:
  initial_backoff_seconds = 30
  backoff_multiplier = 2.0
  max_backoff_seconds = 300
  probe_count_threshold = 10
  reintegration_weight_schedule = [0.1, 0.5, 1.0]
  reintegration_stability_durations = [60, 120]

---

## PART 5: RESEARCH AGENTS (CONTINUOUS OPTIMIZATION)

### EMPIRICIST (Data Scientist)

Role:
  Observe real-world metrics, identify optimization opportunities

Data collection:
  Per-link measurements: E, L, S (every 1 second)
  Agent action logs: Weaver shifts, Builder expansions, Scavenger quarantines
  System metrics: p50/p95/p99 latencies, error rates, availability
  User impact: % requests affected by degradation

Analysis process (collect for 100-1000 observations):
  Step 1: Gather 1000 samples of system state
  Step 2: Calculate statistics (mean, std_dev, min, max)
  Step 3: Compute correlations (threshold_value vs metric_outcome)
  Step 4: Identify outliers (> 2 sigma deviation)
  Step 5: Generate hypothesis: "If theta_X changes by Y%, then metric_Z improves by W%"
  Step 6: Calculate confidence score
  Step 7: Rank hypotheses by confidence >= 0.7

Confidence calculation:
  confidence = (correlation_strength * sample_size * statistical_significance) / (variance * outlier_count)

Output:
  Statistical Report with top 5 optimization hypotheses
  Each with confidence score, predicted improvement, and reasoning

---

### THEORIST (Mathematical Modeler)

Role:
  Build predictive models, identify optimal parameter regions

Four predictive models:

  Model 1: Dose-Response (Hill Equation)
    Formula: y = K * x^n / (T^n + x^n)
    Purpose: Model how threshold value affects system response
    Application: Identify saturation points in response curves

  Model 2: Bifurcation Analysis (Lyapunov)
    Formula: Lyapunov exponent lambda < 0 (stable) vs > 0 (chaotic)
    Purpose: Find parameter regions where system exhibits stable vs oscillatory behavior
    Application: Predict which threshold combinations cause thrashing

  Model 3: Game Theory (Multi-Agent Coordination)
    Framework: Repeated game with payoff matrix
    Purpose: Optimize threshold combinations for agent cooperation
    Output: Cooperative threshold region recommendations

  Model 4: PID Control (Response Tuning)
    Formula: System response = K / (tau * s + 1)
    Purpose: Tune parameters for minimal settling time and overshoot
    Output: PID gains (P, I, D) for optimal control

Output:
  Mathematical Report with model equations, stability diagrams, recommendations

---

### OPTIMIZER (Experimental Designer)

Role:
  Run controlled tests and validate hypotheses with statistical rigor

Methodology:
  Multi-armed bandit with Thompson sampling
  Balances exploration vs exploitation
  Automatically concentrates traffic on best performers

Four-phase framework:

  Phase 1 - Hypothesis Generation (100 ticks):
    Input: Empiricist report + Theorist predictions
    Process: Rank hypotheses by confidence
    Output: Top 5 threshold adjustment candidates

  Phase 2 - Sandbox Testing (500 ticks per hypothesis):
    Environment: Isolated simulation with controlled conditions
    Inject patterns:
      Steady state: constant E/L/S for 100 ticks
      Latency spike: L -> 0.8 for 20 ticks, return to normal
      Cascade failure: E -> 0.05, S -> 0.15 simultaneously for 10 ticks
      Slow degradation: E increases 0.001 per tick for 50 ticks
      Oscillation: L alternates 0.3 <-> 0.6 every 5 ticks
    Output: Success score for each (hypothesis, pattern) combination

  Phase 3 - Shadow Deployment (10,000 ticks):
    Environment: Production traffic, parallel execution
    Process: Run both old and new thresholds, compare decisions
    Measurement: Win rate = % times new threshold makes better decision
    Gate: Require win_rate >= 60% to proceed to Phase 4

  Phase 4 - Canary Rollout (100,000 ticks):
    Traffic: 10% with new thresholds
    Gate: P(success) >= 95%
    If success: increase to 50%, then 100%
    If failure: automatic rollback to previous values

Success metric (composite):
  Score = 0.4*latency_improvement + 0.3*error_reduction + 0.2*stability + 0.1*efficiency
  Requirement: Score >= 1.15 (15% composite improvement)

Bayesian statistical validation:
  P(new_threshold_better | observed_data) >= 0.95
  Sample size: n = (z_alpha/2 + z_beta)^2 * sigma^2 / delta^2

Output:
  Experiment Results with phase metrics and deployment plan

---

## PART 6: STABILITY ANALYSIS

### Lyapunov Stability (Spectrum-Based)

Lyapunov function:
  V(phi) = ||phi||^2 = sum_i phi_i^2

Derivative:
  dV/dt = 2 * phi^T * (D * L_norm * phi - lambda * phi + bounded_injection)

Stability condition:
  If D * lambda_max(L_norm) < 1, then:
    dV/dt <= -2 * lambda * V + C

Conclusion:
  Exponential decay to bounded region
  Time constant: tau = 1 / (2*lambda - D*lambda_max)

L_norm spectrum:
  L_norm eigenvalues are in [0, 2]
  lambda_max(L_norm) <= 2

Practical constraint:
  D <= 0.25 / deg_max
  This ensures D * 2 < 1 for any graph

---

### Discrete Stability (Z-Transform)

Discrete update:
  phi[k+1] = ((1-beta)*I + D*L_norm) * phi[k] + bounded_source

Stability requirement:
  All eigenvalues of ((1-beta)*I + D*L_norm) must satisfy |lambda| < 1

Eigenvalue analysis:
  Eigenvalues = (1-beta) + D * eigenvalue(L_norm)
  Range: (1-beta) + D * [0, 2]

With beta = 0.2, D = 0.15/deg_max:
  min_lambda = 0.8 + 0 = 0.8
  max_lambda = 0.8 + 0.3/deg_max
  For deg_max > 1.5: max_lambda < 1.0 (stable)

Conclusion:
  System is stable for typical network topologies (deg_max >= 2)

---

## PART 7: SECURITY

### mTLS Authentication

Mechanism:
  Agents authenticate to controller via mutual TLS
  Controller verifies agent certificate
  Agent verifies controller certificate

Key management:
  Agent keys rotated every 7 days via PKI
  Compromised certificates immediately revoked via CRL (Certificate Revocation List)
  Each agent has unique identity certificate

---

### Signed Intents

Each action signed:
  ECMP weight shift
  LAG member bringup
  Link disable/drain
  QoS priority adjustment

Signature verification:
  Controller verifies signature before executing intent
  Signature = HMAC-SHA256(action_payload, agent_key)
  If verification fails: action rejected, incident logged

---

### Least Privilege Access Control

Weaver permissions:
  Can only adjust ECMP weights
  Cannot disable links
  Cannot change QoS
  Cannot modify other agents' actions

Builder permissions:
  Can only request capacity tokens
  Controller decides approval
  Cannot directly execute expansion
  Cannot disable links

Scavenger permissions:
  Can only drain and disable links
  Cannot reroute traffic
  Cannot change capacity or QoS
  Cannot override other agents

Enforcement:
  RBAC (Role-Based Access Control) on all intents
  Each intent validated against agent role before execution

---

### Forensic Audit Logging

Pre-action snapshot:
  Log phi_E, phi_L, phi_S fields across all network nodes
  Timestamp: exact moment before action

Post-action snapshot:
  Log phi_E, phi_L, phi_S fields 5 ticks after action
  Timestamp: exact moment 5s after action

Action metadata:
  Agent ID
  Action timestamp
  Trigger condition that caused action
  Action parameters
  Signature
  Result (success/failure)

Log format (JSON):
  {
    "timestamp": "2025-11-10T10:47:00Z",
    "agent": "weaver",
    "action": "shift_ecmp_weights",
    "trigger": "L_hot=true, S_alt_current=0.12",
    "parameters": {"shift_fraction": 0.15, "target_path": "path_alt"},
    "pre_state": {"E": [0.01, 0.02, ...], "L": [0.4, 0.5, ...], "S": [0.6, 0.7, ...]},
    "post_state": {"E": [...], "L": [...], "S": [...]},
    "signature": "sha256_hex_string",
    "result": "success"
  }

Storage:
  Immutable append-only log (Kafka, Splunk, or similar)
  30 days hot storage (rapid access)
  1 year archive storage

Forensic queries:
  "What was field state when link X was quarantined?"
  "Show all Builder expansions in last 24 hours"
  "Was there an error spike before this latency increase?"

---

## PART 8: TELEMETRY INTEGRATION

### Data Pipeline

Collectors:
  sFlow agents on all switches (flow sampling)
  NetFlow v9 / IPFIX agents (exporters)
  P4 switches with INT (In-Band Network Telemetry)
  gNMI/gRPC streaming subscriptions (1s cadence)

Aggregation:
  Time-series database (InfluxDB, Prometheus, VictoriaMetrics)
  Stores per-link metrics

Field computation service:
  Background daemon that:
    1. Fetches raw telemetry from time-series DB
    2. Computes E, L, S normalized signals
    3. Builds L_norm for current network graph
    4. Calculates phi_E, phi_L, phi_S fields
    5. Publishes results to controller API

Controller exposure:
  RESTful API endpoint: GET /api/network/fields
  Returns: current phi state across all nodes
  Agents query this every 1s tick

---

### Signal Data Sources

Error (E):
  CRC errors: from switch interface counters (gNMI)
  Packet drops: from IPFIX records
  Retransmits: from TCP flow samples (SFlow)
  Formula: (crc + drops + retrans) / total_packets

Latency (L):
  Queue depth: from INT telemetry (if P4 switch)
  RTT: from BFD or TCP handshakes
  One-way delay: L_raw = queue_delay OR RTT/2

Capacity (S):
  Interface utilization: from gNMI counter query
  Port rate: from switch specifications
  S_raw = 1 - (current_bps / port_capacity_bps)

---

## PART 9: SIMULATION AND TESTING

### Mininet Harness Setup

Topology:
  10-50 network nodes (switches)
  Can represent fat-tree, Clos, or any topology
  End hosts attached to edge switches
  Traffic generators for load

Controller:
  Ryu or ONOS with custom northbound API
  Exposes /api/network/fields endpoint
  Accepts agent intents via /api/intents

Agents:
  Deployed as controller applications
  Query fields every 1s tick
  Submit intents when triggers fire

Visualization:
  Real-time heatmap of phi_E, phi_L, phi_S gradients
  Color intensity = field value
  Shows how fields diffuse across topology

---

### Fault Injection Scenarios

Scenario 1: Link Failure
  Command: ip link set dev s1-eth1 down
  Expected: Scavenger quarantine, Weaver reroute
  Measure: Convergence time to stable state

Scenario 2: Latency Spike
  Command: tc qdisc add dev s1-eth1 root netem delay 500ms
  Expected: phi_L diffusion, Weaver shift to alternate path
  Measure: Response time, accuracy of rerouting decision

Scenario 3: Packet Loss
  Command: tc qdisc add dev s1-eth1 root netem loss 5%
  Expected: phi_E rises, cross-coupling to phi_L
  Measure: False positive rate, stability

Scenario 4: Cascade Failure
  Command: Fail 3 links simultaneously
  Expected: Cross-coupled response, Builder avoids expansion on doomed path
  Measure: Cascade containment, total impact

Scenario 5: Oscillation Test
  Command: Toggle link up/down every 5 seconds for 5 minutes
  Expected: Hysteresis prevents thrashing, controlled response
  Measure: Action count, oscillation score

---

### Validation Metrics

Convergence time:
  How long until phi fields stabilize after fault?
  Target: < 20 seconds
  Measure: time from fault injection to stable state

False positive rate:
  Percentage of unnecessary actions
  Target: < 5%
  Measure: actions that didn't improve outcome

Coverage:
  Percentage of faults correctly detected and mitigated
  Target: > 95%
  Measure: successful interventions / total faults

Stability (no thrashing):
  Oscillation score = (# agent state changes) / (# faults)
  Target: < 1.5 (each fault causes <1.5 oscillations)
  Measure: state machine transitions

---

## PART 10: DEPLOYMENT CHECKLIST

Phase 1: Simulation (Week 1-2)
  [ ] Deploy Mininet topology with 20 nodes
  [ ] Install Ryu or ONOS controller
  [ ] Implement field computation service
  [ ] Deploy Weaver, Builder, Scavenger as controller apps
  [ ] Run fault injection scenarios
  [ ] Validate metrics: convergence < 20s, false positive < 5%, coverage > 95%

Phase 2: Lab Testbed (Week 3-4)
  [ ] Deploy on 5-10 physical switches
  [ ] Integrate real telemetry (sFlow, gNMI, INT)
  [ ] Test with production-like traffic
  [ ] Validate optics/CRC/FEC checklist
  [ ] Measure latency and error improvements

Phase 3: Shadow Deployment (Week 5-8)
  [ ] Deploy to production network, shadow mode
  [ ] Log what agents WOULD do (no execution)
  [ ] Compare vs current playbook/manual responses
  [ ] Measure win_rate: % times agents make better decisions
  [ ] Gate: require win_rate >= 70%

Phase 4: Canary Rollout (Week 9-12)
  [ ] Enable agents on 10% of network (low-priority links)
  [ ] Monitor latency, errors, availability
  [ ] If stable 2 weeks -> 50%
  [ ] If stable 4 weeks -> 100%
  [ ] Automatic rollback if P(success) < 90%

---

## PART 11: QUICK START

For immediate testing:

1. Clone this specification to your repo as clean UTF-8 text
2. In Mininet: create 20-node fat-tree topology
3. Run Ryu controller with this framework code
4. Inject link failure: see Scavenger quarantine the link
5. Inject latency spike: see Weaver reroute around it
6. Inject cascade: observe cross-coupling (E -> L -> S sequence)
7. Monitor convergence time and false positive rate

Expected results:
  Convergence: 5-20 seconds
  False positives: <5% of actions
  Coverage: >95% of faults detected

---

## PART 12: NOTES FOR IMPLEMENTATION

Encoding:
  All source code: UTF-8, no BOM
  All config files: UTF-8, no BOM
  All logs: UTF-8, valid JSON

No emojis or special characters:
  Use ASCII letters, numbers, standard punctuation only
  Use [PASSED], [FAILED], [ALERT] instead of checkmarks/X marks
  Use -> instead of arrows, etc.

Code style:
  Python: flake8 compliant, UTF-8 encoding declaration
  JavaScript: standard JSON.parse(), valid UTF-8
  C/C++: -std=c++17, UTF-8 locale

Compatibility:
  Target: Python 3.8+, Node.js 14+, Go 1.16+
  Test on Linux, macOS, Windows
  No platform-specific encoding assumptions

---

END OF SPECIFICATION
Version: 3.0 - SDN Production Ready
Date: November 10, 2025
Status: All corrections applied, UTF-8 clean, no emojis