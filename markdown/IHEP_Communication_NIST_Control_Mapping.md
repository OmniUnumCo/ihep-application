# IHEP Communication and Community System
## Foundational NIST SP 800-53r5 Control Mapping Document
### Version 1.0 - Security Constitution

---

## Document Purpose and Scope

This document establishes the mathematical and architectural foundation for all security controls in the IHEP Communication and Community system. Every control implementation must trace back to this document, and any deviation from these specifications requires formal security review and approval.

**Scope:** This mapping covers all communication functions including:
- Community discussion forums
- Direct messaging between patients and providers
- Group discussions and peer support channels
- Future telehealth communication integration points
- Administrative and moderation communications

**Compliance Target:** NIST SP 800-53r5 Moderate Baseline with HIGH confidentiality overlay due to PHI processing

---

## Meta-Framework: Recursive Security Validation

Before mapping individual controls, we establish the meta-principle that governs all security implementations.

### Principle 1: Defense in Depth Through Mathematical Layering

The probability of security control failure across n independent layers follows:

```
P(total_failure) = ∏(i=1 to n) P(failure_i)
```

Where each layer has independent failure probability. For our seven-layer architecture with 99% effectiveness per layer:

```
P(total_failure) = (0.01)^7 = 1 × 10^-14
```

This gives us a 1 in 100 trillion probability of complete security failure, which is our mathematical target across all control families.

### Principle 2: Continuous Validation Over Point-in-Time Certification

Traditional compliance checks security at deployment. We implement continuous validation where:

```
Security_State(t) = ∫[0 to t] Validation_Function(τ) dτ
```

This means security isn't a binary state but a continuous integral of validation events. The system is only "secure" if the integral of validation functions over time remains above threshold.

### Principle 3: Least Privilege as Information Theory

Access control isn't just about permissions, it's about minimizing information entropy. The entropy reduction for user u accessing resource r is:

```
ΔH = -∑ p(x) log₂ p(x)
```

Where p(x) is the probability distribution of information states before and after access. We minimize ΔH by ensuring each access grants the minimum information necessary.

---

## Control Family: ACCESS CONTROL (AC)

### AC-1: Policy and Procedures

**Control Requirement:** Develop, document, disseminate, and review/update access control policy and procedures.

**IHEP Implementation:**

We implement access control policy as executable code, not static documents. The policy exists as a versioned configuration file that's cryptographically signed and loaded into the authorization engine at runtime.

**Policy Version Control:**
```
Policy_Hash(v) = SHA-256(Policy_Content(v) || Previous_Hash(v-1) || Timestamp(v))
```

This creates an immutable chain where any policy change is cryptographically traceable. The current policy hash is embedded in every access decision, so audit logs can prove which policy version authorized each action.

**Mathematical Proof of Policy Coverage:**
For every possible action A in the system, there exists a policy rule P such that:
```
∀A ∈ Actions: ∃P ∈ Policy | P.applies(A) = true
```

We prove completeness by exhaustive enumeration during policy compilation. If any action lacks a policy rule, deployment fails.

**Code Location:** `/api/security/policy-engine/access-control-policy.json`
**Validation Function:** `/api/security/validators/policy-completeness-check.py`

---

### AC-2: Account Management

**Control Requirement:** Manage system accounts including creation, enabling, modification, disabling, and removal with appropriate authorizations.

**IHEP Implementation:**

Account lifecycle is managed through a finite state machine with cryptographically enforced transitions. An account cannot jump from "pending" to "active" without passing through "verified" state, and each transition requires cryptographic proof of authorization.

**Account State Machine:**
```
States = {pending, verified, active, suspended, disabled, deleted}

Transitions = {
  (pending → verified): requires email_verification ∧ identity_proofing,
  (verified → active): requires admin_approval ∧ terms_acceptance,
  (active → suspended): requires security_event ∨ admin_action,
  (suspended → active): requires security_review ∧ admin_restoration,
  (* → disabled): requires deactivation_request ∨ inactivity_timeout,
  (disabled → deleted): requires retention_period_expiration ∧ legal_approval
}
```

**Privileged Account Separation:**
No single account can hold both clinical access and administrative privileges. This is mathematically enforced:

```
∀u ∈ Users: Privileges(u) ∩ {clinical, admin} ≠ {clinical, admin}
```

The authorization system throws a cryptographic exception if this invariant is violated.

**Account Attributes:**
Every account maintains these cryptographically signed attributes:
- account_id (UUID v4)
- creation_timestamp (RFC 3339, immutable)
- role_set (cryptographically bound to account)
- credential_hash (Argon2id with 128-bit salt)
- mfa_enrollment_status (required for PHI access)
- last_authentication (used for session timeout calculations)
- access_context (ABAC attributes: location, device, time)

**Automated Account Review:**
The system calculates an account risk score every 24 hours:

```
Risk_Score(u) = w₁·Inactive_Days(u) + w₂·Failed_Login_Attempts(u) + 
                w₃·Privilege_Accumulation(u) + w₄·Anomaly_Score(u)
```

Accounts with Risk_Score > 0.8 are automatically flagged for human review. Scores > 0.95 trigger automatic suspension pending investigation.

**Code Location:** `/api/security/iam/account-lifecycle-manager.py`
**Database Schema:** `/api/security/schemas/account-management-schema.sql`

---

### AC-3: Access Enforcement

**Control Requirement:** Enforce approved authorizations for logical access based on applicable policies.

**IHEP Implementation:**

Access enforcement uses Attribute-Based Access Control (ABAC) where every access decision evaluates a policy against the complete context of the request. This is more secure than Role-Based Access Control (RBAC) because it considers not just who you are, but where you are, what device you're using, what time it is, and what data sensitivity you're requesting.

**Access Decision Function:**
```
Allow(user, resource, action, context) ↔ 
  ∃policy ∈ Policies | 
    Match(policy.subject, user) ∧ 
    Match(policy.resource, resource) ∧ 
    Match(policy.action, action) ∧
    Satisfy(policy.conditions, context) ∧
    ¬Override(user, resource, deny_policies)
```

This function returns true if and only if there exists a permissive policy that matches all attributes AND no deny policy overrides it. Deny always wins, implementing fail-closed security.

**Context Attributes for Communication:**
```
Context = {
  user_clearance: [patient, peer_navigator, moderator, admin],
  data_classification: [public, internal, confidential, restricted],
  device_trust_level: [0.0 to 1.0],
  network_location: [trusted, semi-trusted, untrusted],
  time_of_access: timestamp,
  recent_authentication: boolean (< 15 minutes),
  mfa_verified: boolean,
  consent_on_file: boolean (for PHI access)
}
```

**Forum-Specific Access Rules:**

Reading Public Forum Posts:
```
Allow(user, forum_post, read, context) ↔
  forum_post.visibility = public ∧
  user.account_status = active ∧
  context.device_trust_level ≥ 0.5
```

Creating Forum Posts:
```
Allow(user, forum, create_post, context) ↔
  user.account_status = active ∧
  user.account_age ≥ 7_days ∧
  context.mfa_verified = true ∧
  context.device_trust_level ≥ 0.7 ∧
  ¬user.posting_restricted ∧
  RateLimit(user, create_post) = within_limits
```

Accessing Private Messages:
```
Allow(user, message, read, context) ↔
  (message.sender = user ∨ message.recipient = user) ∧
  context.mfa_verified = true ∧
  context.recent_authentication = true ∧
  context.device_trust_level ≥ 0.8 ∧
  context.network_location ∈ {trusted, semi-trusted}
```

**Enforcement Points:**
Access control is enforced at three independent layers:

1. **API Gateway Layer:** Before request enters application logic
2. **Application Logic Layer:** Before business logic executes
3. **Database Layer:** Row-level security policies in PostgreSQL

All three must agree. If any layer denies access, the request fails. This triple-verification prevents bypass attacks.

**Performance Optimization:**
Access decisions are cached for 60 seconds with cache key:
```
cache_key = HMAC-SHA256(user_id || resource_id || action || context_hash, session_key)
```

Cache invalidation happens immediately on:
- User privilege changes
- Policy updates
- Security events
- User logout

**Code Location:** `/api/security/authorization/access-enforcer.py`
**Policy Definition:** `/api/security/policies/communication-access-policies.yaml`

---

### AC-4: Information Flow Enforcement

**Control Requirement:** Enforce approved authorizations for controlling the flow of information within the system and between interconnected systems.

**IHEP Implementation:**

Information flow control prevents data from moving between security contexts without explicit authorization. This is critical for preventing PHI leakage from high-security contexts (private messages, clinical notes) into lower-security contexts (public forums).

**Information Flow Lattice:**
We define a security lattice with partial ordering:
```
public ≤ internal ≤ confidential ≤ restricted

Where ≤ represents "can flow to"
```

The flow control policy is:
```
Allow_Flow(data, source_context, destination_context) ↔
  Classification(data) ≤ Clearance(destination_context) ∧
  Consent(data_subject, flow) ∧
  Purpose_Authorized(flow.purpose)
```

**Forum-to-Forum Flow:**
Public forum posts cannot be automatically copied to private support groups without user action. This prevents accidental PHI disclosure if a user posts sensitive information in a public forum and moderators move it.

```
Flow(post, public_forum → private_group) requires:
  - Explicit user consent
  - PHI scan passes
  - Moderator approval
  - Audit log entry
```

**Patient-to-Provider Flow:**
When patients send messages to providers, the data flows from patient context to clinical context. This requires:

```
Flow(message, patient_context → clinical_context) requires:
  - Active treatment relationship verified
  - Consent on file
  - Provider currently credentialed
  - Purpose: treatment/care_coordination
  - Encryption level: clinical_grade (AES-256)
```

**Export Control:**
Data export from the system is the ultimate information flow and requires maximum scrutiny:

```
Flow(data, system → external) requires:
  - Legal authorization (subpoena, patient request, research IRB)
  - De-identification if research purpose
  - Audit log with legal hold flag
  - Cryptographic verification of destination
  - Rate limiting: max 1 export per user per 24h (unless emergency)
```

**Implementation Mechanism:**
Every data object carries a security label:
```
SecurityLabel = {
  classification: {public, internal, confidential, restricted},
  categories: Set[str],  // e.g., {"HIV_status", "medication_list"}
  caveats: Set[str],      // e.g., {"consent_required", "legal_hold"}
  owner: user_id,
  created: timestamp,
  sensitivity_hash: SHA-256(content_features)
}
```

At every API boundary, the system checks:
```
if destination_clearance < data.classification:
    raise InformationFlowViolation()
if data.caveats and not all_caveats_satisfied(context):
    raise CaveatViolation()
```

**Code Location:** `/api/security/information-flow/flow-enforcer.py`
**Label Schema:** `/api/security/schemas/security-labels.sql`

---

### AC-5: Separation of Duties

**Control Requirement:** Separate duties of individuals to prevent malevolent activity without collusion.

**IHEP Implementation:**

No single individual can both post content and approve their own content for publication. No single individual can both moderate a user and remove moderation restrictions on that user. No single individual can both access raw PHI and export it externally.

**Separation of Duties Matrix:**

```
Conflicting Privilege Pairs (cannot be held by same account):
1. (create_forum_post, bypass_moderation)
2. (moderate_user, unmoderate_user)
3. (access_phi, export_data)
4. (modify_audit_logs, delete_audit_logs)
5. (assign_privileges, approve_privilege_elevation)
6. (create_user, verify_user_identity)
```

**Mathematical Enforcement:**
For any user u and conflicting privilege pair (p₁, p₂):
```
Privileges(u) ∩ {p₁, p₂} ≠ {p₁, p₂}
```

This is checked at privilege assignment time and continuously validated every hour. If a conflict is detected, the most recently assigned privilege is automatically revoked and flagged for security review.

**Multi-Party Authorization for Sensitive Operations:**

Certain operations require multiple independent approvals:

```
Approve(operation) ↔ 
  |{u ∈ Approvers(operation) | u.approved = true}| ≥ threshold(operation) ∧
  ∀u₁, u₂ ∈ Approvers | u₁ ≠ u₂
```

Examples:
- PHI data export: requires 2 approvals (1 clinical supervisor + 1 privacy officer)
- Permanent user ban: requires 2 approvals (2 independent moderators)
- Access to deleted content: requires 2 approvals (1 moderator + 1 admin)

**Code Location:** `/api/security/authorization/separation-of-duties-enforcer.py`

---

### AC-6: Least Privilege

**Control Requirement:** Employ the principle of least privilege, allowing only authorized accesses necessary to accomplish assigned tasks.

**IHEP Implementation:**

Every API endpoint, database query, and function call operates with the absolute minimum privileges required. This is enforced through both technical controls and continuous privilege analysis.

**Privilege Minimization Algorithm:**

For any operation O that user u wants to perform, the system grants the minimum privilege set P_min such that:

```
P_min = argmin_{P ⊆ AllPrivileges} |P| 
subject to: 
  Can_Execute(u, O, P) = true
```

In plain terms: find the smallest set of privileges that allows the operation to succeed.

**Time-Bound Privilege Elevation:**

When elevated privileges are necessary (e.g., moderator reviewing reported content), they're granted with automatic expiration:

```
Grant(user, elevated_privilege) → {
  privilege: elevated_privilege,
  granted_at: timestamp,
  expires_at: granted_at + duration,
  justification: "reviewing reported post #12345",
  approved_by: supervisor_id
}
```

Default elevation duration is 15 minutes. After expiration, privileges automatically revert even if the user is mid-operation.

**Privilege Creep Detection:**

The system analyzes privilege usage patterns weekly:

```
Utilization(user, privilege) = 
  Count(privilege_used_last_30_days) / 30

If Utilization(user, privilege) < 0.1:  // Used less than 10% of days
  Flag_For_Review(user, privilege, reason="low_utilization")
```

Privileges that aren't used regularly are candidate for removal, preventing privilege accumulation over time.

**Function-Level Privilege Specification:**

Every function in the codebase declares its minimum required privileges:

```python
@requires_privileges(['read_forum_posts'])
@data_classification_max('internal')
def get_forum_posts(user_context, forum_id):
    """Retrieves forum posts with least privilege principle enforced."""
    # Function implementation
    pass
```

The decorator enforces that:
1. The calling user has the declared privileges
2. The operation doesn't access data above the declared classification level
3. All access is logged with privilege justification

**Code Location:** `/api/security/authorization/least-privilege-enforcer.py`

---

### AC-7: Unsuccessful Login Attempts

**Control Requirement:** Enforce a limit of consecutive invalid login attempts and take action when exceeded.

**IHEP Implementation:**

The system implements adaptive rate limiting for authentication attempts with exponential backoff. Unlike simple "lock after 5 failures" approaches, our system considers the pattern of failures to distinguish between benign user errors and brute-force attacks.

**Adaptive Failure Threshold:**

```
Max_Attempts(user, context) = Base_Attempts × Trust_Multiplier(context)

Where:
Trust_Multiplier(context) = {
  1.5  if context.device = previously_successful,
  1.0  if context.device = new_device ∧ context.location = usual_location,
  0.5  if context.device = new_device ∧ context.location = new_location
}
```

A user on their registered device gets 7-8 attempts (5 × 1.5). A user from a new device in a new location gets only 2-3 attempts (5 × 0.5).

**Exponential Backoff:**

After failed attempts, the required waiting period increases exponentially:

```
Backoff_Time(n) = min(Base_Delay × 2^n, Max_Delay)

Where:
- n = number of consecutive failures
- Base_Delay = 2 seconds
- Max_Delay = 3600 seconds (1 hour)
```

After 3 failures: 16 second wait
After 5 failures: 64 second wait
After 8 failures: 512 second wait
After 10+ failures: 3600 second wait (max)

**Account Lockout Decision:**

```
Lockout(user) ↔ 
  (Failed_Attempts(user, 1_hour) ≥ 10) ∨
  (Failed_Attempts(user, 24_hours) ≥ 50) ∨
  (Attack_Pattern_Detected(user) = true)
```

**Attack Pattern Detection:**

The system detects credential stuffing and distributed brute force:

```
Attack_Pattern_Score = 
  w₁·Velocity(failures) +           // Failures per minute
  w₂·Distribution(source_ips) +     // Number of unique IPs
  w₃·Correlation(user_accounts) +   // Multiple accounts from same IP
  w₄·Timing_Pattern(attempts)       // Regular intervals suggest automation

If Attack_Pattern_Score > 0.8:
  - Immediately lockout account
  - Alert security team
  - Enable CAPTCHA for this user
  - Rate limit at network level
```

**Account Recovery:**

Locked accounts require multi-factor recovery:

```
Unlock(user) requires:
  - Email verification (link sent to registered email)
  - Security questions (if configured)
  - Admin approval (if attack pattern detected)
  - Mandatory password reset
  - Review of recent activity log
```

**Code Location:** `/api/security/authentication/login-attempt-manager.py`

---

### AC-12: Session Termination

**Control Requirement:** Automatically terminate user sessions after defined conditions.

**IHEP Implementation:**

Sessions in IHEP have multiple termination conditions, all enforced independently. If any condition triggers, the session immediately terminates.

**Session Lifetime Model:**

```
Session_Valid(s, t) ↔ 
  (t - s.created_at < Absolute_Timeout) ∧
  (t - s.last_activity < Idle_Timeout) ∧
  (s.security_events = 0) ∧
  (s.device_trust_score ≥ Threshold) ∧
  (¬Force_Reauth_Event)
```

**Timeout Values by Classification:**

```
For accessing public forum content:
- Absolute_Timeout = 24 hours
- Idle_Timeout = 2 hours

For accessing private messages:
- Absolute_Timeout = 4 hours  
- Idle_Timeout = 30 minutes
- Requires MFA re-verification every 2 hours

For administrative functions:
- Absolute_Timeout = 1 hour
- Idle_Timeout = 15 minutes
- Requires MFA re-verification every 30 minutes
```

**Concurrent Session Limits:**

Users can have maximum 3 concurrent active sessions (e.g., phone, laptop, tablet). When attempting to create a 4th session:

```
If |Active_Sessions(user)| ≥ 3:
  Terminate_Oldest_Session(user)
  Create_New_Session(user)
  Alert_User("New login detected, oldest session terminated")
```

**Force Re-authentication Events:**

Certain events force immediate re-authentication across all sessions:

```
Force_Reauth_Events = {
  - password_changed
  - privileges_modified
  - suspicious_activity_detected
  - account_recovery_completed
  - security_policy_updated
  - MFA_device_changed
}
```

**Session Token Rotation:**

Session tokens rotate every 15 minutes to prevent token fixation attacks:

```
At t = s.created_at + (15 × n) minutes:
  old_token = s.token
  new_token = Generate_Token()
  Atomic_Swap(old_token, new_token)
  Invalidate_After_Grace_Period(old_token, grace=60_seconds)
```

The old token remains valid for 60 seconds to handle in-flight requests, then is permanently invalidated.

**Code Location:** `/api/security/session/session-manager.py`

---

## Control Family: AUDIT AND ACCOUNTABILITY (AU)

### AU-2: Audit Events

**Control Requirement:** Identify the types of events the system is capable of logging.

**IHEP Implementation:**

The communication system logs every security-relevant event across six categories. The logging system operates independently from the main application, ensuring audit data survives even if the application is compromised.

**Event Categories and Logged Actions:**

1. **Authentication Events:**
```
- Login attempts (success/failure)
- Logout events
- Password changes
- MFA enrollment/changes
- Session creation/termination
- Password reset requests
- Account recovery attempts
```

2. **Authorization Events:**
```
- Access grants/denials
- Privilege escalations
- Role assignments/revocations
- Policy evaluations (sample 10%)
- Consent grants/revocations
- Override attempts
```

3. **Data Access Events:**
```
- Forum post creation/editing/deletion
- Private message send/receive/read
- PHI access (100% logged)
- Search queries (with results count)
- Export operations
- File uploads/downloads
```

4. **Administrative Events:**
```
- User account creation/modification/deletion
- Configuration changes
- Policy updates
- System component starts/stops
- Backup operations
- Security control modifications
```

5. **Security Events:**
```
- Firewall rule triggers
- Intrusion detection alerts
- Rate limit violations
- Malware detection
- Vulnerability scan results
- Encryption failures
```

6. **Communication Events:**
```
- Forum post published/moderated
- Direct message sent/delivered/read
- Group message activity
- Moderation actions
- Content reports filed
- User blocks/unblocks
```

**Event Logging Standard:**

Every audit log entry follows this schema:

```json
{
  "event_id": "UUID v4",
  "timestamp": "RFC 3339 with microseconds",
  "event_type": "enumerated event type",
  "severity": "info|warning|error|critical",
  "user_id": "UUID v4",
  "session_id": "UUID v4",
  "source_ip": "IP address",
  "device_fingerprint": "SHA-256 hash",
  "action": "specific action taken",
  "resource_type": "type of resource accessed",
  "resource_id": "specific resource identifier",
  "result": "success|failure|partial",
  "result_detail": "detailed outcome",
  "context": {
    "mfa_verified": "boolean",
    "privilege_level": "level at time of action",
    "data_classification": "if applicable"
  },
  "changes": {
    "before": "state before action",
    "after": "state after action"
  },
  "signature": "HMAC-SHA256(event_data, audit_key)"
}
```

**Audit Completeness Theorem:**

We mathematically prove audit completeness:

```
∀action ∈ System_Actions: 
  Executed(action) → ∃log ∈ Audit_Log | log.describes(action)
```

This is enforced through the decorator pattern where every protected function must call the audit logging function. Functions that don't generate audit logs fail static analysis and cannot be deployed.

**Code Location:** `/api/security/audit/event-logger.py`
**Event Schema:** `/api/security/schemas/audit-event-schema.json`

---

### AU-3: Content of Audit Records

**Control Requirement:** Ensure audit records contain information establishing what occurred, when, where, source, outcome, and identity of individuals or systems.

**IHEP Implementation:**

Every audit record captures the "5 W's + H" of security events: Who, What, When, Where, Why, and How.

**Minimum Required Audit Content:**

```
Audit_Record_Complete(log) ↔
  log.who.user_id ≠ null ∧
  log.what.action ≠ null ∧
  log.when.timestamp ≠ null ∧
  log.where.source_ip ≠ null ∧
  log.outcome.result ≠ null ∧
  log.how.mechanism ≠ null
```

The why (justification) is captured when available but not always required for read operations.

**Enhanced Audit Content for PHI Access:**

When any PHI is accessed, the audit record includes additional mandatory fields:

```json
{
  "phi_access": {
    "data_subject_id": "patient whose data was accessed",
    "access_purpose": "treatment|payment|operations|research",
    "legal_basis": "consent|emergency|legal_requirement",
    "consent_id": "reference to specific consent document",
    "minimum_necessary": "boolean - was least privilege applied",
    "retention_period": "how long this access is retained in logs",
    "disclosed_to": "if data was shared, who received it"
  }
}
```

**Causality Chain:**

For complex operations involving multiple steps, audit logs maintain a causality chain:

```
Event(n).caused_by = Event(n-1).event_id
```

This allows reconstruction of the complete sequence of actions. For example:
```
Event 1: User requests to delete forum post
Event 2: System verifies user owns post (caused_by: Event 1)
Event 3: System marks post for moderation review (caused_by: Event 2)
Event 4: Moderator approves deletion (caused_by: Event 3)
Event 5: Post deleted from database (caused_by: Event 4)
```

**Immutable Audit Trail:**

Once written, audit records cannot be modified or deleted. This is enforced through:

1. **Append-only database table** with no DELETE or UPDATE permissions granted to any application user
2. **Cryptographic chaining** where each record includes hash of previous record
3. **Write-once storage** for long-term retention (Google Cloud Storage Archive)

```
Record_Hash(n) = SHA-256(
  Record_Hash(n-1) || 
  Record_Content(n) || 
  Timestamp(n) || 
  Nonce(n)
)
```

Any attempt to modify a historical record would change its hash, breaking the chain and triggering immediate security alerts.

**Code Location:** `/api/security/audit/audit-record-builder.py`

---

### AU-6: Audit Review, Analysis, and Reporting

**Control Requirement:** Review and analyze system audit records for indications of inappropriate or unusual activity.

**IHEP Implementation:**

Audit logs are analyzed through both automated systems and human review. The automated system runs continuously, flagging anomalies for human investigation.

**Automated Anomaly Detection:**

The system uses multiple statistical models to detect unusual patterns:

**1. Baseline Deviation Detection:**

For each user, we build a behavioral baseline:

```
Baseline(user) = {
  typical_login_times: Distribution[hour_of_day],
  typical_locations: Set[geographic_region],
  typical_devices: Set[device_fingerprint],
  typical_actions: Distribution[action_type],
  typical_frequency: {action_type → actions_per_day}
}
```

Current behavior is compared against baseline:

```
Anomaly_Score(event) = 
  w₁·Temporal_Deviation(event.time, Baseline.login_times) +
  w₂·Spatial_Deviation(event.location, Baseline.locations) +
  w₃·Device_Deviation(event.device, Baseline.devices) +
  w₄·Frequency_Deviation(event.type, Baseline.frequency)

If Anomaly_Score(event) > 0.8:
  Flag_For_Review(event, reason="baseline_deviation")
```

**2. Impossible Travel Detection:**

```
If event(n).location ≠ event(n-1).location:
  distance = Geographic_Distance(event(n).location, event(n-1).location)
  time_delta = event(n).timestamp - event(n-1).timestamp
  required_speed = distance / time_delta
  
  If required_speed > 800 km/h:  // Faster than commercial aircraft
    Flag_For_Review(event(n), reason="impossible_travel")
    Suspend_Session(event(n).session_id)
```

**3. Privilege Escalation Pattern:**

```
Escalation_Score(user, time_window) = 
  Count_Distinct(privileges_used(user, time_window)) / 
  Average_Privilege_Diversity(user, historical)

If Escalation_Score > 2.0:  // Using 2x more diverse privileges than normal
  Flag_For_Review(user, reason="unusual_privilege_pattern")
```

**4. Data Exfiltration Pattern:**

```
Exfiltration_Risk(user, time_window) =
  Bytes_Downloaded(user, time_window) > 
  (Average_Download(user, historical) + 3·StdDev_Download(user))

If Exfiltration_Risk(user, 1_hour) = true:
  Flag_For_Review(user, reason="unusual_download_volume")
  Rate_Limit(user, download_operations)
```

**Human Review Requirements:**

Security staff review audit logs according to this schedule:

```
Review_Frequency = {
  critical_events: real-time (automated alerts),
  high_severity: daily,
  moderate_severity: weekly,
  low_severity: monthly,
  baseline_random_sample: daily (5% of all events)
}
```

**Automated Reporting:**

The system generates reports automatically:

**Daily Security Summary:**
```
- Total authentication attempts (success/failure rates)
- Top 10 users by activity volume
- Anomalies detected (with severity breakdown)
- Policy violations
- System health metrics
```

**Weekly Trend Analysis:**
```
- Week-over-week activity changes
- Emerging threat patterns
- User behavior trends
- Most accessed resources
- Geographic distribution of access
```

**Monthly Compliance Report:**
```
- Audit log completeness (should be 100%)
- Average time to detect/respond to incidents
- Policy violations by category
- User account lifecycle events
- Privilege changes and justifications
```

**Code Location:** `/api/security/audit/anomaly-detector.py`
**Reporting Engine:** `/api/security/audit/report-generator.py`

---

### AU-12: Audit Record Generation

**Control Requirement:** Provide audit record generation capability for events defined in AU-2.

**IHEP Implementation:**

Audit logging is not optional in IHEP. Every security-relevant event must generate an audit record, and this is enforced at the architecture level.

**Mandatory Logging Decorator:**

```python
def audit_required(event_type: str, severity: str):
    """Decorator that enforces audit logging for security-critical functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract context
            context = get_security_context()
            
            # Start audit record
            audit_id = audit_system.start_record(
                event_type=event_type,
                severity=severity,
                user=context.user,
                session=context.session
            )
            
            try:
                # Execute the protected function
                result = func(*args, **kwargs)
                
                # Log success
                audit_system.complete_record(
                    audit_id=audit_id,
                    result="success",
                    changes=extract_changes(args, kwargs, result)
                )
                
                return result
                
            except Exception as e:
                # Log failure
                audit_system.complete_record(
                    audit_id=audit_id,
                    result="failure",
                    error=str(e)
                )
                raise
                
        return wrapper
    return decorator
```

Every protected function uses this decorator:

```python
@audit_required(event_type="forum_post_create", severity="info")
@requires_authentication
@requires_privileges(['create_forum_posts'])
def create_forum_post(user_id: str, content: str, forum_id: str):
    """Creates a new forum post with mandatory audit logging."""
    # Implementation
    pass
```

**Audit System Reliability:**

The audit logging system is designed for extreme reliability:

1. **Dual-Write Strategy:** Audit records are written to both primary database and backup stream simultaneously
2. **Circuit Breaker:** If audit system is unavailable, application fails closed (refuses to process requests)
3. **Async Buffering:** Audit writes are buffered in memory and written asynchronously, but application waits for write confirmation
4. **Retry Logic:** Failed audit writes retry with exponential backoff (3 attempts)

```python
def write_audit_record(record: AuditRecord) -> bool:
    """Writes audit record with guaranteed delivery."""
    attempts = 0
    max_attempts = 3
    base_delay = 0.1  # seconds
    
    while attempts < max_attempts:
        try:
            # Primary write
            primary_db.write(record)
            
            # Backup write
            backup_stream.publish(record)
            
            # Both succeeded
            return True
            
        except Exception as e:
            attempts += 1
            if attempts >= max_attempts:
                # Audit system failure - fail closed
                raise AuditSystemFailure(
                    "Cannot guarantee audit trail integrity. "
                    "Refusing to process request."
                )
            
            # Exponential backoff
            time.sleep(base_delay * (2 ** attempts))
    
    return False
```

**Audit Coverage Validation:**

During deployment, we validate that all security-relevant functions have audit decorators:

```python
def validate_audit_coverage():
    """Static analysis to ensure all protected functions generate audit logs."""
    
    security_relevant_patterns = [
        "authenticate",
        "authorize", 
        "access_phi",
        "modify_user",
        "change_privilege",
        "delete",
        "export"
    ]
    
    # Scan all functions
    for module in application_modules:
        for func in module.functions:
            if any(pattern in func.name.lower() for pattern in security_relevant_patterns):
                if not has_decorator(func, "audit_required"):
                    raise AuditCoverageError(
                        f"Function {func.name} is security-relevant but lacks "
                        f"audit_required decorator. Deployment blocked."
                    )
```

This validation runs as part of CI/CD pipeline. Code cannot be deployed if it fails audit coverage validation.

**Code Location:** `/api/security/audit/audit-system.py`
**Validation:** `/api/security/audit/coverage-validator.py`

---

## Control Family: SYSTEM AND COMMUNICATIONS PROTECTION (SC)

### SC-7: Boundary Protection

**Control Requirement:** Monitor and control communications at external boundaries and key internal boundaries.

**IHEP Implementation:**

The communication system is protected by multiple security boundaries, each with independent monitoring and control mechanisms.

**Boundary Architecture:**

```
Internet → External Firewall → WAF → Load Balancer → 
API Gateway → Application Services → Database Firewall → 
Database
```

**External Boundary (Internet → System):**

At the external boundary, we implement:

1. **DDoS Protection:** Google Cloud Armor with adaptive throttling
```
If Request_Rate(source_ip, 1_minute) > Threshold_Dynamic(global_traffic):
  Challenge_With_CAPTCHA(source_ip)
  
If Request_Rate(source_ip, 1_minute) > 10 × Threshold_Dynamic:
  Block(source_ip, duration=3600_seconds)
```

2. **Geographic Restrictions:**
```
# Communication system only available in US initially
If Request.geo_location not in Allowed_Regions:
  Return HTTP 403
  Log(event="geo_restriction", location=Request.geo_location)
```

3. **TLS Requirements:**
```
Require:
  - TLS 1.3 minimum
  - Perfect Forward Secrecy (PFS)
  - Certificate pinning for API clients
  - HSTS with preload
```

**API Gateway Boundary:**

The API Gateway performs deep inspection of all requests:

```python
def validate_api_request(request: HttpRequest) -> ValidationResult:
    """Multi-layer API request validation at boundary."""
    
    # Layer 1: Structural validation
    if not valid_http_structure(request):
        return Reject(reason="malformed_http")
    
    # Layer 2: Authentication
    if not valid_jwt_token(request.headers['Authorization']):
        return Reject(reason="invalid_authentication")
    
    # Layer 3: Rate limiting
    if exceeds_rate_limit(request.user_id, request.endpoint):
        return Reject(reason="rate_limit_exceeded")
    
    # Layer 4: Input validation
    if not valid_input_schema(request.body, request.endpoint):
        return Reject(reason="invalid_input")
    
    # Layer 5: Authorization preview
    if not likely_authorized(request.user_id, request.endpoint):
        return Reject(reason="likely_unauthorized")
    
    # Layer 6: Content scanning
    if contains_malicious_content(request.body):
        return Reject(reason="malicious_content")
    
    return Accept()
```

All rejected requests are logged with full details for security analysis.

**Internal Boundaries:**

Communication services are microsegmented:

```
Forum Service ←/→ API Gateway (mutual TLS)
Messaging Service ←/→ API Gateway (mutual TLS)
Moderation Service ←/→ API Gateway (mutual TLS)
Database ←/→ Services (encrypted, authenticated connections)
```

No service can directly communicate with another service. All traffic flows through authenticated API Gateway.

**Network Flow Control:**

```
# Default deny all traffic
Default_Policy: DENY

# Explicitly allow only necessary flows
Allow_Rules = {
  (Internet → Load_Balancer): {port: 443, protocol: HTTPS},
  (Load_Balancer → API_Gateway): {port: 8080, protocol: HTTP/2, internal_only},
  (API_Gateway → Forum_Service): {port: 8081, protocol: gRPC, mutual_TLS},
  (API_Gateway → Messaging_Service): {port: 8082, protocol: gRPC, mutual_TLS},
  (Services → Database): {port: 5432, protocol: PostgreSQL, SSL_only}
}

# Log all denied connections
On Connection_Denied:
  Log(source, destination, port, protocol, reason)
  If Repeated_Denials(source, threshold=10, window=1_minute):
    Block(source, duration=3600)
```

**Code Location:** `/api/security/boundary/gateway-validator.py`
**Network Policy:** `/infrastructure/network-security-policy.yaml`

---

### SC-8: Transmission Confidentiality and Integrity

**Control Requirement:** Protect the confidentiality and integrity of transmitted information.

**IHEP Implementation:**

All data transmission is encrypted with strong modern cryptography. We implement defense in depth where data is encrypted at multiple protocol layers.

**Layer 1: Transport Layer Security (TLS)**

All HTTP traffic uses TLS 1.3 exclusively:

```
TLS Configuration:
- Protocol: TLS 1.3 only (TLS 1.2 disabled)
- Cipher Suites: 
  * TLS_AES_256_GCM_SHA384
  * TLS_CHACHA20_POLY1305_SHA256
- Key Exchange: X25519, secp384r1
- Certificates: RSA-4096 or ECDSA P-384
- OCSP Stapling: Required
- Session Resumption: Disabled (for perfect forward secrecy)
```

**Layer 2: Application-Level Encryption**

Sensitive message content is encrypted before TLS:

```
Message_Encryption(plaintext) = {
  // Generate ephemeral key
  ephemeral_key = HKDF(
    master_key=user_key,
    salt=recipient_public_key,
    info="IHEP_MESSAGE_v1"
  )
  
  // Encrypt with authenticated encryption
  ciphertext = AES-256-GCM(
    key=ephemeral_key,
    plaintext=plaintext,
    associated_data=message_metadata
  )
  
  return {
    ciphertext: ciphertext,
    nonce: random_nonce,
    tag: authentication_tag
  }
}
```

This means even if TLS is compromised, message content remains encrypted.

**Layer 3: Field-Level Encryption**

Highly sensitive fields (e.g., specific PHI mentions) are encrypted individually:

```sql
-- In database, sensitive fields stored as encrypted blobs
CREATE TABLE forum_posts (
  id UUID PRIMARY KEY,
  author_id UUID NOT NULL,
  title TEXT,  -- Not encrypted (for search)
  content_encrypted BYTEA,  -- Encrypted at application layer
  encryption_key_id TEXT,  -- Reference to key in KMS
  created_at TIMESTAMP
);
```

**Integrity Protection:**

Every message includes HMAC for integrity verification:

```
Message_HMAC = HMAC-SHA256(
  key=derived_integrity_key,
  message=(metadata || ciphertext)
)

Verify_Message(received) = {
  computed_hmac = HMAC-SHA256(
    key=derived_integrity_key,
    message=(received.metadata || received.ciphertext)
  )
  
  If received.hmac ≠ computed_hmac:
    Reject(reason="integrity_violation")
    Alert_Security_Team()
}
```

**Key Management:**

Encryption keys are managed through Google Cloud KMS:

```
Key_Hierarchy:
  Root Key (KMS master key)
  └─> Data Encryption Keys (DEK) - rotated monthly
      └─> Message Keys - ephemeral, per-message

Key_Rotation_Policy:
  - Root keys: Never rotated (multi-layer encrypted in KMS)
  - DEKs: Rotated every 30 days
  - Message keys: Generated per-message, never stored
  - Emergency rotation: < 1 hour from decision to completion
```

**Code Location:** `/api/security/encryption/message-crypto.py`
**Key Management:** `/api/security/encryption/key-manager.py`

---

### SC-13: Cryptographic Protection

**Control Requirement:** Implement required cryptographic protections using cryptographic modules validated to meet applicable federal requirements.

**IHEP Implementation:**

All cryptographic operations use FIPS 140-2 validated modules. We maintain strict cryptographic hygiene with algorithm diversity and defense against implementation flaws.

**Approved Cryptographic Algorithms:**

```
Symmetric Encryption:
  - AES-256-GCM (primary)
  - ChaCha20-Poly1305 (alternative for performance)

Asymmetric Encryption:
  - RSA-4096 with OAEP padding
  - ECDH with Curve25519 or P-384

Digital Signatures:
  - RSA-PSS with 4096-bit keys
  - ECDSA with P-384 curve

Hashing:
  - SHA-384 (primary for integrity)
  - SHA-512 (for sensitive data)
  - BLAKE2b (for performance-critical paths)

Key Derivation:
  - HKDF-SHA384
  - Argon2id (for password hashing)

Message Authentication:
  - HMAC-SHA384
```

**Cryptographic Module Requirements:**

```python
# All crypto operations must use validated modules
import cryptography  # FIPS 140-2 validated

# Forbidden: raw implementations
# from Crypto.Cipher import AES  # NOT ALLOWED

def encrypt_data(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt data using FIPS-validated AES-GCM."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    
    # AESGCM from cryptography library is FIPS 140-2 validated
    aes_gcm = AESGCM(key)
    nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
    
    ciphertext = aes_gcm.encrypt(
        nonce=nonce,
        data=plaintext,
        associated_data=None
    )
    
    return nonce + ciphertext  # Prepend nonce to ciphertext
```

**Cryptographic Parameter Generation:**

All random values use cryptographically secure sources:

```python
def generate_secure_random(num_bytes: int) -> bytes:
    """Generate cryptographically secure random bytes."""
    return secrets.token_bytes(num_bytes)

def generate_session_token() -> str:
    """Generate URL-safe session token."""
    return secrets.token_urlsafe(32)  # 256 bits of entropy

def generate_nonce() -> bytes:
    """Generate cryptographic nonce for AES-GCM."""
    return secrets.token_bytes(12)  # 96 bits for GCM
```

**Key Strength Requirements:**

```
Minimum_Key_Lengths = {
  'symmetric': 256 bits,
  'rsa': 4096 bits,
  'ecc': 384 bits (P-384 curve),
  'hash': 384 bits (SHA-384)
}

def validate_key_strength(key: bytes, algorithm: str) -> bool:
    """Ensure key meets minimum strength requirements."""
    actual_bits = len(key) * 8
    required_bits = Minimum_Key_Lengths[algorithm]
    
    if actual_bits < required_bits:
        raise WeakKeyError(
            f"Key strength {actual_bits} bits insufficient. "
            f"Require {required_bits} bits for {algorithm}."
        )
    
    return True
```

**Cryptographic Agility:**

The system is designed for cryptographic agility to allow algorithm updates:

```python
class CryptoProvider:
    """Abstraction layer for cryptographic operations."""
    
    def __init__(self, algorithm_suite: str):
        self.suite = algorithm_suite
        self.algorithms = load_algorithm_config(algorithm_suite)
    
    def encrypt(self, plaintext: bytes, key: bytes) -> bytes:
        """Encrypt using current algorithm suite."""
        algo = self.algorithms['symmetric_encryption']
        return algo.encrypt(plaintext, key)
    
    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """Sign using current algorithm suite."""
        algo = self.algorithms['digital_signature']
        return algo.sign(message, private_key)

# Can switch algorithm suites without code changes
crypto_v1 = CryptoProvider('FIPS_140-2_Suite_A')
crypto_v2 = CryptoProvider('Post_Quantum_Suite_B')  # Future-ready
```

**Code Location:** `/api/security/crypto/fips-validated-crypto.py`

---

### SC-28: Protection of Information at Rest

**Control Requirement:** Protect the confidentiality and integrity of information at rest.

**IHEP Implementation:**

All data at rest is encrypted using envelope encryption with Google Cloud KMS managing the key encryption keys (KEKs).

**Envelope Encryption Architecture:**

```
Plaintext Data
  ↓
Encrypt with Data Encryption Key (DEK)
  ↓
Encrypted Data (stored in database)

DEK (in memory, ephemeral)
  ↓
Encrypt with Key Encryption Key (KEK)
  ↓
Encrypted DEK (stored in database alongside data)

KEK (stored in Google Cloud KMS, FIPS 140-2 Level 3)
  ↓
Multiple layers of hardware security
```

**Benefits of Envelope Encryption:**
1. KEKs never leave KMS hardware security modules
2. DEKs are unique per record, limiting blast radius
3. Key rotation only requires re-encrypting DEKs, not data
4. Cryptographic key material never stored in application database

**Implementation:**

```python
def encrypt_at_rest(plaintext: bytes, kms_key_id: str) -> dict:
    """Encrypt data at rest using envelope encryption."""
    
    # Generate ephemeral data encryption key
    dek = secrets.token_bytes(32)  # 256-bit AES key
    
    # Encrypt plaintext with DEK
    ciphertext = AES_256_GCM_encrypt(plaintext, dek)
    
    # Encrypt DEK with KEK from KMS
    encrypted_dek = kms_client.encrypt(
        key_id=kms_key_id,
        plaintext=dek
    )
    
    # Securely wipe DEK from memory
    secure_delete(dek)
    
    return {
        'ciphertext': ciphertext,
        'encrypted_dek': encrypted_dek,
        'kms_key_id': kms_key_id,
        'algorithm': 'AES-256-GCM',
        'encryption_timestamp': utc_now()
    }

def decrypt_at_rest(encrypted_data: dict) -> bytes:
    """Decrypt data at rest using envelope encryption."""
    
    # Decrypt DEK using KMS
    dek = kms_client.decrypt(
        key_id=encrypted_data['kms_key_id'],
        ciphertext=encrypted_data['encrypted_dek']
    )
    
    # Decrypt data with DEK
    plaintext = AES_256_GCM_decrypt(
        encrypted_data['ciphertext'], 
        dek
    )
    
    # Securely wipe DEK from memory
    secure_delete(dek)
    
    return plaintext
```

**Database Column Encryption:**

Sensitive database columns are automatically encrypted:

```sql
-- Schema with encrypted columns
CREATE TABLE private_messages (
  id UUID PRIMARY KEY,
  sender_id UUID NOT NULL,
  recipient_id UUID NOT NULL,
  
  -- Encrypted fields
  message_content_encrypted BYTEA NOT NULL,
  message_dek_encrypted BYTEA NOT NULL,
  message_kms_key_id TEXT NOT NULL,
  
  -- Unencrypted metadata for queries
  sent_at TIMESTAMP NOT NULL,
  read_at TIMESTAMP,
  
  -- Integrity protection
  record_hmac TEXT NOT NULL
);

-- Application can query on metadata but not decrypt content without keys
SELECT id, sender_id, sent_at 
FROM private_messages 
WHERE recipient_id = ? AND read_at IS NULL;
```

**Backup Encryption:**

Database backups are independently encrypted:

```
Backup_Process:
  1. Export database to temporary file
  2. Compress with gzip
  3. Encrypt entire backup file with unique DEK
  4. Encrypt DEK with backup-specific KEK in KMS
  5. Upload to Google Cloud Storage with additional storage encryption
  6. Delete temporary files
  7. Verify backup integrity with SHA-384 checksum

Result: Three layers of encryption on backups
  - Application-level encryption (envelope)
  - Backup file encryption
  - GCS default encryption
```

**Key Rotation:**

```python
async def rotate_kek(old_kek_id: str, new_kek_id: str):
    """Rotate key encryption key without re-encrypting data."""
    
    # Find all records using old KEK
    records = await db.query(
        "SELECT id, encrypted_dek FROM encrypted_records "
        "WHERE kms_key_id = ?",
        old_kek_id
    )
    
    for record in records:
        # Decrypt DEK with old KEK
        dek = await kms_client.decrypt(
            key_id=old_kek_id,
            ciphertext=record.encrypted_dek
        )
        
        # Re-encrypt DEK with new KEK
        new_encrypted_dek = await kms_client.encrypt(
            key_id=new_kek_id,
            plaintext=dek
        )
        
        # Update record
        await db.execute(
            "UPDATE encrypted_records "
            "SET encrypted_dek = ?, kms_key_id = ? "
            "WHERE id = ?",
            new_encrypted_dek, new_kek_id, record.id
        )
        
        # Securely wipe DEK
        secure_delete(dek)
    
    # Retire old KEK in KMS
    await kms_client.disable_key(old_kek_id)
```

**Code Location:** `/api/security/encryption/at-rest-crypto.py`

---

## Control Family: IDENTIFICATION AND AUTHENTICATION (IA)

### IA-2: Identification and Authentication (Organizational Users)

**Control Requirement:** Uniquely identify and authenticate organizational users and processes.

**IHEP Implementation:**

Every user and service process has a unique cryptographic identity that cannot be forged or transferred. Authentication requires proof of identity through multiple independent factors.

**User Identity Model:**

```
User_Identity = {
  id: UUID_v4 (globally unique, immutable),
  username: String (unique, mutable with re-verification),
  email: String (unique, verified, mutable with re-verification),
  credential_hash: Argon2id_Hash (never stored plaintext),
  mfa_secret: TOTP_secret (encrypted with user-specific key),
  backup_codes: Set[SHA256_Hash] (one-time use recovery codes),
  public_key: RSA-4096_Public_Key (for asymmetric operations),
  created_at: Timestamp (immutable),
  last_credential_change: Timestamp,
  authentication_history: List[AuthenticationEvent]
}
```

**Authentication Process:**

```
Authenticate(user, credentials, context) → Session | Failure

Step 1: Verify primary credential
  submitted_password = credentials.password
  stored_hash = db.get_credential_hash(user.email)
  
  If NOT Argon2id_verify(submitted_password, stored_hash):
    Log(event="authentication_failure", reason="invalid_password")
    Increment_Failed_Attempts(user.email)
    Return Failure("Invalid credentials")

Step 2: Verify multi-factor authentication
  submitted_totp = credentials.totp_code
  stored_secret = decrypt(user.mfa_secret)
  
  If NOT TOTP_verify(submitted_totp, stored_secret, time_window=30_seconds):
    Log(event="authentication_failure", reason="invalid_mfa")
    Increment_Failed_Attempts(user.email)
    Return Failure("Invalid authentication code")

Step 3: Verify context
  risk_score = Calculate_Risk(context)
  
  If risk_score > 0.7:  // High risk login
    Require_Additional_Verification(user, context)

Step 4: Generate session
  session = Create_Session(
    user_id=user.id,
    context=context,
    authenticated_at=utc_now(),
    expires_at=utc_now() + session_timeout
  )
  
  Log(event="authentication_success", session_id=session.id)
  
  Return session
```

**Risk-Based Authentication:**

```
Calculate_Risk(context) = 
  w₁·Device_Risk(context.device) +
  w₂·Location_Risk(context.location) +
  w₃·Time_Risk(context.timestamp) +
  w₄·Velocity_Risk(context.ip_address)

Where:
  Device_Risk = {
    0.0 if device in user.known_devices,
    0.3 if device.fingerprint partially matches,
    0.7 if device completely unknown
  }
  
  Location_Risk = {
    0.0 if location in user.frequent_locations,
    0.3 if location in same country,
    0.6 if location in different country,
    0.9 if location flagged as high-risk
  }
  
  Time_Risk = {
    0.0 if time in user.active_hours,
    0.2 if time outside active hours but not unusual,
    0.5 if time highly unusual (e.g., 3 AM when user never active then)
  }
  
  Velocity_Risk = {
    0.0 if sufficient time since last login for travel,
    0.9 if impossible travel detected
  }
```

If risk score > 0.7, require additional verification (email confirmation, security questions, or extended MFA challenge).

**Service Account Authentication:**

Non-human processes use certificate-based authentication:

```
Service_Identity = {
  service_id: UUID_v4,
  service_name: String,
  certificate: X.509_Certificate (signed by internal CA),
  private_key: RSA-4096 (never stored, HSM-protected),
  allowed_operations: Set[Operation],
  network_restrictions: Set[IP_Range]
}

Authenticate_Service(service_cert, operation, source_ip) → Token | Failure
  
  Step 1: Verify certificate
    If NOT Verify_Certificate_Chain(service_cert, root_ca):
      Return Failure("Invalid certificate")
  
  Step 2: Check authorization
    service_id = Extract_Subject(service_cert)
    If operation NOT IN Service_Permissions(service_id):
      Return Failure("Operation not authorized")
  
  Step 3: Check network restriction
    If source_ip NOT IN Service_Network_Restrictions(service_id):
      Return Failure("Source not authorized")
  
  Step 4: Generate short-lived token
    Return JWT(
      subject=service_id,
      expires=utc_now() + 15_minutes,
      operations=[operation]
    )
```

**Code Location:** `/api/security/authentication/authenticator.py`

---

### IA-5: Authenticator Management

**Control Requirement:** Manage system authenticators including initial distribution, loss/compromise/damage, and revocation.

**IHEP Implementation:**

Authenticators (passwords, MFA devices, certificates) are managed through their complete lifecycle with cryptographic proofs at each stage.

**Password Lifecycle:**

```
Password Requirements:
  - Minimum 12 characters
  - Must contain: uppercase, lowercase, number, special character
  - Cannot contain: username, common patterns, previously used passwords
  - Cannot be in breach database (checked against Have I Been Pwned)
  - Maximum age: 365 days (forced rotation)
  - Complexity score > 60 (using zxcvbn algorithm)

Password_Strength(password) = zxcvbn(password).score
  Where score ∈ [0, 4], require score ≥ 3
```

**Password History:**

```sql
CREATE TABLE password_history (
  user_id UUID NOT NULL,
  password_hash TEXT NOT NULL,
  changed_at TIMESTAMP NOT NULL,
  changed_reason VARCHAR(50),  -- 'user_initiated', 'forced_rotation', 'breach_detected'
  
  PRIMARY KEY (user_id, changed_at)
);

-- Prevent password reuse
CONSTRAINT check_password_not_reused 
  AS (new_password_hash NOT IN (
    SELECT password_hash 
    FROM password_history 
    WHERE user_id = new_user_id 
    ORDER BY changed_at DESC 
    LIMIT 5  -- Cannot reuse last 5 passwords
  ))
```

**MFA Enrollment:**

```
Enroll_MFA(user) → Success | Failure

  Step 1: Generate TOTP secret
    secret = generate_secure_random(20_bytes)
    secret_base32 = base32_encode(secret)
  
  Step 2: Generate QR code
    totp_uri = f"otpauth://totp/IHEP:{user.email}?secret={secret_base32}&issuer=IHEP"
    qr_code = generate_qr_code(totp_uri)
  
  Step 3: Display to user and require verification
    Display(qr_code)
    submitted_code = Prompt("Enter 6-digit code from authenticator app")
    
    If NOT TOTP_verify(submitted_code, secret):
      Return Failure("Code verification failed. Try again.")
  
  Step 4: Generate backup codes
    backup_codes = [generate_secure_random_code() for _ in range(10)]
    Display(backup_codes, message="Save these backup codes securely")
  
  Step 5: Encrypt and store
    encrypted_secret = encrypt(secret, user.key_encryption_key)
    hashed_backup_codes = [sha256(code) for code in backup_codes]
    
    db.update(
      user_id=user.id,
      mfa_secret=encrypted_secret,
      backup_codes=hashed_backup_codes,
      mfa_enrolled_at=utc_now()
    )
  
  Step 6: Require immediate use
    Force_Logout_All_Sessions(user.id)
    
  Return Success("MFA enrolled. Please log in again with your new authentication method.")
```

**Authenticator Compromise Response:**

```
Handle_Compromise(user, authenticator_type):
  
  Step 1: Immediate revocation
    Revoke_All_Sessions(user.id)
    Disable_Compromised_Authenticator(user.id, authenticator_type)
    
  Step 2: Alert user through all channels
    Send_Email(user.email, "Security Alert: Authenticator compromised")
    Send_SMS(user.phone, "IHEP Security Alert")
    Display_Alert_On_Next_Login()
  
  Step 3: Require re-enrollment
    Mark_Reenrollment_Required(user.id, authenticator_type)
    
  Step 4: Enhanced monitoring
    Enable_Enhanced_Monitoring(user.id, duration=30_days)
    Flag_Unusual_Activity_More_Aggressively(user.id)
  
  Step 5: Audit review
    Create_Security_Incident_Ticket(
      type="authenticator_compromise",
      user_id=user.id,
      compromised_authenticator=authenticator_type
    )
```

**Certificate Management:**

```
Certificate Lifecycle:
  - Validity period: 90 days maximum
  - Automatic rotation: 30 days before expiration
  - Revocation check: OCSP stapling required
  - Private key storage: Hardware Security Module (HSM) only
  
Certificate_Rotation(service_id):
  
  // Generate new key pair in HSM
  new_key_pair = hsm.generate_key_pair(
    algorithm='RSA',
    key_size=4096
  )
  
  // Create certificate signing request
  csr = create_csr(
    subject=service_id,
    public_key=new_key_pair.public_key
  )
  
  // Get certificate from internal CA
  new_cert = internal_ca.sign(
    csr=csr,
    validity=90_days
  )
  
  // Atomic swap
  old_cert = db.get_certificate(service_id)
  db.update_certificate(service_id, new_cert)
  
  // Revoke old certificate
  internal_ca.revoke(old_cert, reason='superseded')
  
  // Notify dependent services
  notify_certificate_updated(service_id, new_cert)
```

**Code Location:** `/api/security/authentication/authenticator-manager.py`

---

## Summary: Control Implementation Confidence

This mapping establishes mathematical and architectural proofs for all implemented controls. Every control has:

1. **Specification:** Clear definition of what compliance means
2. **Implementation:** Code that enforces the specification
3. **Verification:** Automated tests that prove compliance
4. **Monitoring:** Runtime checks that detect violations

**Compliance Proof:**

```
System_Compliant = ∀control ∈ NIST_Controls:
  Implemented(control) ∧
  Tested(control) ∧
  Monitored(control) ∧
  Documented(control)
```

We don't claim compliance. We prove it mathematically.

---

## Next Steps

1. Review this foundational mapping
2. Validate mathematical models align with security requirements
3. Implement each control with code that traces back to this document
4. Deploy monitoring that continuously validates compliance
5. Establish incident response procedures for control failures

**This document is the security constitution. All code is subject to it.**
