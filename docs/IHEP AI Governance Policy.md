# IHEP AI Governance Policy v1.0

**Effective Date:** December 4, 2025  
**Approving Authority:** IHEP Executive Governance Board  
**Compliance Frameworks:** NIST AI Risk Management Framework (AI RMF 1.0), HIPAA Security Rule, FDA Software as a Medical Device (SaMD) Best Practices, WHO Ethics Guidelines for Trustworthy AI in Health.

---

## 1. Purpose and Scope
This policy establishes the governance framework for the design, development, deployment, and monitoring of Artificial Intelligence (AI) and Machine Learning (ML) systems within the Integrated Health Empowerment Program (IHEP). It ensures that all AI assetsâ€”specifically the Digital Twin engine, Morphogenetic AI, and Predictive Analytics modulesâ€”are safe, effective, ethical, and compliant with applicable regulations.

## 2. Governance Structure

### 2.1 Executive Governance Board
*   **Role:** Ultimate accountability for AI strategy and risk acceptance.
*   **Responsibilities:**
    *   Approve high-risk AI system deployments.
    *   Allocate budget for compliance and safety infrastructure.
    *   Review quarterly AI safety and performance reports.

### 2.2 AI Ethics & Safety Committee (AIESC)
*   **Role:** Independent oversight of ethical implications and patient safety.
*   **Composition:** Chief Medical Officer, Chief Information Security Officer (CISO), Lead AI Ethicist, Patient Advocacy Representative, Legal Counsel.
*   **Responsibilities:**
    *   Conduct Ethical Impact Assessments (EIA) for all new models.
    *   Review fairness and bias testing results.
    *   Adjudicate "Go/No-Go" decisions for model deployment based on safety criteria.

### 2.3 Technical Review Board (TRB)
*   **Role:** Technical validation and architectural integrity.
*   **Responsibilities:**
    *   Validate model performance metrics (accuracy, AUC, etc.).
    *   Verify implementation of explainability features (SHAP values).
    *   Audit data lineage and quality.

## 3. AI System Lifecycle Management

### 3.1 Phase I: Clinical Necessity & Conception
*   **Requirement:** No AI project shall commence without a documented **Clinical Necessity Statement** approved by the Medical Director.
*   **Criteria:** The AI solution must solve a validated clinical or operational problem better than existing non-AI alternatives.

### 3.2 Phase II: Design & Development
*   **Data Governance:**
    *   All training data must be fully de-identified in accordance with HIPAA Safe Harbor or Expert Determination methods.
    *   **Data Provenance:** Complete lineage tracking from raw source to training set is mandatory.
    *   **Privacy:** Federated Learning must be used for multi-site training; Differential Privacy (epsilon â‰¤ 1.0) must be applied to shared gradients.
*   **Algorithm Selection:**
    *   "Black box" models are prohibited for clinical decision support unless accompanied by robust explainability methods (e.g., SHAP, LIME).

### 3.3 Phase III: Validation & Verification (V&V)
*   **Performance Testing:** Models must meet pre-defined accuracy thresholds (e.g., >85% AUC for viral suppression prediction) on a held-out test set.
*   **Fairness Testing:**
    *   Mandatory testing for **Disparate Impact** across protected classes (race, gender, age, socioeconomic status).
    *   **Threshold:** Disparate Impact Ratio must be between 0.8 and 1.25.
*   **Adversarial Testing:** Models must undergo stress testing against adversarial attacks and edge cases.

### 3.4 Phase IV: Deployment & Monitoring
*   **Human-in-the-Loop (HITL):** AI predictions for clinical interventions are **decision support only**. A licensed human provider must review and approve all clinical recommendations.
*   **Continuous Monitoring:**
    *   **Drift Detection:** Automated systems must monitor for data drift (input distribution changes) and concept drift (accuracy degradation).
    *   **Threshold:** A 5% drop in performance triggers an automatic rollback or alert for manual review.
*   **Explainability:** All clinician-facing AI outputs must present top contributing factors (SHAP values) to justify the prediction.

### 3.5 Phase V: Retirement
*   Models that no longer meet performance standards or clinical needs must be securely decommissioned.
*   Data used for training retired models must be archived or destroyed according to the IHEP Data Retention Policy.

## 4. Risk Management Framework

IHEP adopts a risk-based approach aligned with the NIST AI RMF:

| Risk Level | Definition | Requirements |
| :--- | :--- | :--- |
| **Critical** | Clinical diagnosis, treatment recommendation, or crisis intervention (e.g., suicide risk). | Full FDA SaMD compliance, HITL mandatory, rigorous external audit, continuous real-time monitoring. |
| **High** | Triage support, resource allocation, personalized health coaching. | Internal AIESC approval, fairness audit, monthly performance review. |
| **Low** | Administrative tasks, scheduling, operational efficiency. | Standard IT validation, automated monitoring. |

## 5. Transparency and Patient Rights

### 5.1 Notification
Patients must be explicitly informed when they are interacting with an AI agent (e.g., Chat Service) or when AI is used to aid their care decisions.

### 5.2 Right to Explanation
Patients have the right to request an explanation of how an AI decision affected their care plan.

### 5.3 Opt-Out
Where clinically feasible, patients should be offered the option to opt-out of AI-driven features in favor of standard manual care processes.

## 6. Incident Response

*   **Adverse Events:** Any patient harm or "near miss" attributed to an AI system must be reported immediately as a **Level 1 Incident**.
*   **Response Protocol:**
    1.  Immediate suspension of the affected AI model.
    2.  Activation of "Standard of Care" fallback protocols.
    3.  Root Cause Analysis (RCA) by the TRB and AIESC.
    4.  Report to regulatory bodies (FDA, OCR) if required.

## 7. Audit and Compliance

*   **Internal Audit:** Quarterly review of AI inventory, performance logs, and bias assessments.
*   **External Audit:** Annual third-party algorithmic audit to validate safety, fairness, and security controls.

## 8. Policy Enforcement
Failure to adhere to this policy may result in disciplinary action, up to and including termination of employment and legal action. Unauthorized deployment of AI models is strictly prohibited.

---
**Approved By:** Jason Jarmacz, Principal Investigator & Project Sponsor  
**Date:** 12/04/2025