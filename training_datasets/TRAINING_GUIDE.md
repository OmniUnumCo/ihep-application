# IHEP Digital Twins - MedGemma Training Guide

## Executive Summary

This comprehensive guide describes the training datasets and methodology for fine-tuning MedGemma (or similar medical foundation models) to power the IHEP Digital Twins ecosystem. The goal is to create an AI assistant capable of providing personalized, evidence-based support for patients managing life-altering conditions including HIV/AIDS, chronic diseases, mental health conditions, and social determinants of health.

## Table of Contents

1. [Overview](#overview)
2. [Dataset Architecture](#dataset-architecture)
3. [Training Categories](#training-categories)
4. [Data Format Specifications](#data-format-specifications)
5. [Quality Assurance](#quality-assurance)
6. [Fine-Tuning Pipeline](#fine-tuning-pipeline)
7. [Evaluation Framework](#evaluation-framework)
8. [Safety and Compliance](#safety-and-compliance)
9. [Deployment Considerations](#deployment-considerations)

---

## Overview

### Vision

The IHEP Digital Twins AI assistant aims to provide:

- **Clinical Decision Support**: Evidence-based guidance for HIV care and chronic disease management
- **Adherence Coaching**: Motivational interviewing and practical strategies for medication adherence
- **Mental Health Support**: Trauma-informed emotional support with appropriate crisis escalation
- **Social Determinants Navigation**: Resource connection for housing, food, transportation, and employment
- **Risk Prediction**: Transparent risk stratification to identify patients needing intervention
- **Personalized Engagement**: Natural, empathetic conversation tailored to individual needs

### Target Conditions

| Condition | Priority | Rationale |
|-----------|----------|-----------|
| HIV/AIDS | Primary | Core focus of IHEP platform |
| Type 2 Diabetes | High | Common comorbidity, complex management |
| Hypertension | High | Cardiovascular risk in HIV population |
| Depression | High | 40%+ prevalence in HIV population |
| Anxiety | High | Common comorbidity affecting adherence |
| Substance Use Disorders | High | Significant barrier to care engagement |
| Chronic Kidney Disease | Medium | Growing concern in aging HIV population |
| Hepatitis C | Medium | Common coinfection |

### Model Selection

**Primary**: MedGemma (Google's medical-domain Gemma)
- Pre-trained on medical literature and clinical data
- Optimized for healthcare question-answering
- Supports instruction fine-tuning

**Alternatives**:
- BioMistral
- Med-PaLM 2 (if accessible)
- Llama 2 + medical fine-tuning
- Custom medical LLM

---

## Dataset Architecture

### Directory Structure

```
training_datasets/
├── clinical/                    # Clinical decision support
│   ├── raw/                     # Expert-crafted examples
│   │   ├── hiv_care_continuum.jsonl
│   │   └── chronic_disease_management.jsonl
│   ├── processed/               # Cleaned and validated
│   └── augmented/               # Synthetically expanded
│
├── adherence/                   # Medication adherence
│   ├── raw/
│   │   └── medication_adherence_patterns.jsonl
│   ├── processed/
│   └── augmented/
│
├── mental_health/               # Mental health support
│   ├── raw/
│   │   └── mental_health_assessments.jsonl
│   ├── processed/
│   └── augmented/
│
├── social_determinants/         # SDOH navigation
│   ├── raw/
│   │   └── sdoh_interventions.jsonl
│   ├── processed/
│   └── augmented/
│
├── risk_prediction/             # Risk stratification
│   ├── raw/
│   │   └── risk_stratification_training.jsonl
│   ├── processed/
│   └── augmented/
│
├── conversational/              # Patient dialogues
│   ├── raw/
│   │   └── patient_dialogues.jsonl
│   ├── processed/
│   └── augmented/
│
├── wearables/                   # Device data interpretation
├── financial_health/            # Financial navigation
├── federated_learning/          # Multi-site data
├── evaluation/                  # Benchmark sets
│
├── configs/
│   └── medgemma_finetune.yaml   # Training configuration
│
├── scripts/
│   ├── generate_training_data.py
│   ├── validate_datasets.py
│   └── preprocess_for_medgemma.py
│
├── processed_for_training/      # Final training-ready data
│   ├── train.jsonl
│   ├── validation.jsonl
│   └── test.jsonl
│
└── README.md
```

### Data Volume Targets

| Category | Raw Examples | Augmented | Total Target |
|----------|--------------|-----------|--------------|
| Clinical | 500+ | 2,000+ | 2,500+ |
| Adherence | 300+ | 1,500+ | 1,800+ |
| Mental Health | 400+ | 2,000+ | 2,400+ |
| Social Determinants | 300+ | 1,200+ | 1,500+ |
| Risk Prediction | 200+ | 1,000+ | 1,200+ |
| Conversational | 500+ | 2,500+ | 3,000+ |
| **Total** | **2,200+** | **10,200+** | **12,400+** |

---

## Training Categories

### 1. Clinical Decision Support

**Purpose**: Enable evidence-based clinical guidance following treatment guidelines.

**Topics**:
- Lab result interpretation (viral load, CD4 count, metabolic panels)
- Medication knowledge (ARVs, drug interactions, side effects)
- Treatment initiation and modification
- Comorbidity management
- Special populations (pregnancy, aging, pediatric)
- Drug resistance and salvage therapy

**Example Format**:
```json
{
  "instruction": "You are a clinical decision support AI for HIV care.",
  "input": "Patient with viral load 1,200 after 5 years undetectable. CD4 450. Reports occasional missed doses. What should we consider?",
  "output": "[Comprehensive clinical analysis with risk factors, differential diagnosis, recommended actions, and evidence citations]",
  "metadata": {
    "category": "clinical",
    "condition": "HIV",
    "severity": "medium",
    "evidence_level": "guideline"
  }
}
```

**Evidence Sources**:
- DHHS HIV Treatment Guidelines
- IAS-USA Resistance Guidelines
- AASLD HCV Guidelines
- ADA Diabetes Standards of Care
- ACC/AHA Cardiovascular Guidelines

### 2. Medication Adherence Coaching

**Purpose**: Support patients in maintaining medication adherence through empathetic, motivational techniques.

**Barrier Categories**:
- Pill fatigue / treatment burden
- Side effects
- Cost and access
- Stigma and disclosure
- Irregular schedules
- Mental health interference
- Regimen complexity

**Approach**: Motivational Interviewing principles
- Express empathy
- Develop discrepancy
- Roll with resistance
- Support self-efficacy

**Example Format**:
```json
{
  "instruction": "You are an AI health coach using motivational interviewing.",
  "input": "I've been missing my HIV medication 2-3 times a week. I'm just tired of taking pills every day.",
  "output": "[Empathetic acknowledgment, exploration of feelings, practical strategies, non-judgmental tone]",
  "metadata": {
    "category": "adherence",
    "barrier": "pill_fatigue",
    "condition": "HIV"
  }
}
```

### 3. Mental Health Support

**Purpose**: Provide trauma-informed emotional support while recognizing crisis situations.

**Assessments**:
- PHQ-9 (depression screening)
- GAD-7 (anxiety screening)
- AUDIT (alcohol use)
- PC-PTSD (trauma screening)

**Crisis Detection**:
- Suicidal ideation (passive and active)
- Self-harm
- Psychotic symptoms
- Severe substance intoxication

**Safety Response Protocol**:
```
IF suicidal_ideation DETECTED:
  1. Acknowledge feelings
  2. Assess immediacy
  3. Provide crisis resources (988, Crisis Text Line)
  4. Encourage professional help
  5. Do not leave conversation abruptly
```

### 4. Social Determinants Navigation

**Purpose**: Connect patients with resources addressing social barriers to health.

**SDOH Domains**:
- Housing (HOPWA, shelters, rapid rehousing)
- Food Security (SNAP, food banks, WIC)
- Transportation (Medicaid NEMT, volunteer drivers)
- Employment (vocational rehab, job training)
- Insurance (Medicaid, ACA, Ryan White)
- Social Support (peer programs, support groups)
- Legal (immigration, discrimination)

**Resource Knowledge**:
- Federal programs (Ryan White, HOPWA, SNAP)
- State-specific programs
- Local AIDS service organizations
- Emergency assistance programs

### 5. Risk Prediction and Stratification

**Purpose**: Identify patients at risk for adverse outcomes to enable proactive intervention.

**Risk Types**:
- Care disengagement
- Viral rebound
- Hospitalization
- Mental health crisis
- Housing instability

**Output Format**:
- Risk score (0-1 scale)
- Contributing factors with weights
- SHAP-style explanations
- Actionable recommendations
- Predicted outcomes with/without intervention

### 6. Conversational Patient Support

**Purpose**: Natural, multi-turn dialogues for patient onboarding, education, and support.

**Conversation Types**:
- New patient onboarding
- Lab result discussions
- Appointment reminders
- Medication education
- Emotional support
- Crisis intervention

---

## Data Format Specifications

### Instruction-Response Format (JSONL)

```json
{
  "instruction": "System prompt defining the AI role",
  "input": "User query or clinical scenario",
  "output": "Expected model response",
  "metadata": {
    "category": "clinical|adherence|mental_health|...",
    "condition": "HIV|diabetes|depression|...",
    "severity": "low|medium|high|critical",
    "evidence_level": "guideline|expert_consensus|research",
    "source": "synthetic|clinical_expert|literature"
  }
}
```

### Multi-Turn Conversation Format (JSONL)

```json
{
  "conversation_id": "unique_identifier",
  "turns": [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User message"},
    {"role": "assistant", "content": "Assistant response"},
    {"role": "user", "content": "Follow-up question"},
    {"role": "assistant", "content": "Follow-up response"}
  ],
  "metadata": {
    "scenario_type": "onboarding|crisis|education|...",
    "outcome": "successful|needs_escalation|...",
    "source": "synthetic"
  }
}
```

### Processed Training Format

```json
{
  "id": "sha256_hash_16chars",
  "text": "<|system|>\nSystem prompt\n</|system|>\n\n<|user|>\nUser input\n</|user|>\n\n<|assistant|>\nAssistant output\n</|assistant|>",
  "metadata": {...}
}
```

---

## Quality Assurance

### Validation Pipeline

```
Raw Data → JSON Validation → PHI Detection →
Harmful Content Filter → Quality Metrics →
Clinical Review → Bias Detection → Approved Data
```

### Validation Checks

1. **Format Validation**
   - Valid JSON structure
   - Required fields present
   - Metadata completeness

2. **PHI Detection**
   - SSN patterns
   - Phone numbers
   - Email addresses
   - Physical addresses
   - Full birth dates

3. **Content Safety**
   - Harmful content patterns
   - Stigmatizing language
   - Inappropriate medical advice

4. **Quality Metrics**
   - Minimum/maximum length
   - Response completeness
   - Appropriate tone

5. **Clinical Accuracy**
   - Guideline adherence
   - Correct medication information
   - Appropriate escalation

6. **Bias Detection**
   - Gender balance
   - Age representation
   - Race/ethnicity sensitivity

### Running Validation

```bash
cd training_datasets
python scripts/validate_datasets.py
```

Output: `validation_report.txt`

---

## Fine-Tuning Pipeline

### Prerequisites

```bash
pip install torch transformers datasets accelerate peft bitsandbytes
pip install wandb tensorboard
```

### Step 1: Data Preprocessing

```bash
python scripts/preprocess_for_medgemma.py
```

This produces:
- `processed_for_training/train.jsonl`
- `processed_for_training/validation.jsonl`
- `processed_for_training/test.jsonl`

### Step 2: Configure Training

Edit `configs/medgemma_finetune.yaml`:

```yaml
model:
  base_model: "google/medgemma-7b"
  precision: "bf16"

lora:
  enabled: true
  r: 64
  alpha: 128

training:
  learning_rate: 2.0e-5
  num_train_epochs: 3
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
```

### Step 3: Launch Training

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "google/medgemma-7b",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Apply LoRA
lora_config = LoraConfig(
    r=64,
    lora_alpha=128,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("json", data_files={
    "train": "processed_for_training/train.jsonl",
    "validation": "processed_for_training/validation.jsonl"
})

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"]
)
trainer.train()
```

### Step 4: Evaluate

```bash
python scripts/evaluate_model.py --checkpoint outputs/checkpoint-best
```

---

## Evaluation Framework

### Automatic Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Perplexity | <10 | Language model quality |
| BLEU | >0.3 | Response similarity |
| ROUGE-L | >0.4 | Content overlap |
| BERTScore | >0.85 | Semantic similarity |

### Clinical Accuracy Evaluation

| Metric | Target | Method |
|--------|--------|--------|
| Guideline Adherence | >90% | Expert review |
| Medication Accuracy | >95% | Fact checking |
| Contraindication Detection | >95% | Case-based testing |
| Appropriate Escalation | >90% | Scenario testing |

### Safety Evaluation

| Metric | Target | Description |
|--------|--------|-------------|
| Crisis Detection Rate | >99% | Detects suicidal ideation |
| PHI Leak Rate | 0% | No PHI in outputs |
| Harmful Content Rate | 0% | No dangerous advice |
| Appropriate Disclaimers | >95% | Recommends providers |

### Bias Evaluation

| Metric | Target | Protected Attributes |
|--------|--------|---------------------|
| Demographic Parity | >0.9 | Gender, Age, Race |
| Equalized Odds | >0.9 | Same response quality across groups |
| Calibration | <0.1 diff | Prediction accuracy across groups |

---

## Safety and Compliance

### HIPAA Compliance

- **Training data contains NO PHI**
- All examples are synthetic or fully de-identified
- Patient ID hashing (SHA-256) in all processing
- Audit logging of data access

### Safety Rails

1. **Crisis Detection**
   - Keyword and pattern matching
   - Immediate resource provision
   - Warm handoff to crisis services

2. **Medical Disclaimers**
   - Automatic disclaimer insertion
   - Provider referral recommendations
   - Scope limitation awareness

3. **Content Filtering**
   - Input/output safety checks
   - Harmful content blocking
   - Prompt injection prevention

### Ethical Considerations

- Avoid diagnosis (screening only)
- Maintain professional boundaries
- Cultural sensitivity
- Accessibility (plain language options)
- Transparency about AI limitations

---

## Deployment Considerations

### Infrastructure

- **Serving**: Google Cloud Run or Vertex AI
- **Latency Target**: <2s for first token
- **Throughput**: 100+ concurrent users
- **Monitoring**: Response quality, safety triggers, latency

### Integration Points

- IHEP Patient Twin Service
- AI Inference Service
- Morphogenetic Framework
- Real-time alerting system

### Continuous Learning

1. **Feedback Collection**: Thumbs up/down, corrections
2. **Performance Monitoring**: Accuracy drift detection
3. **Periodic Retraining**: Monthly data additions
4. **A/B Testing**: New model versions

---

## Getting Started

### Quick Start

```bash
# 1. Generate sample data
python scripts/generate_training_data.py

# 2. Validate datasets
python scripts/validate_datasets.py

# 3. Preprocess for training
python scripts/preprocess_for_medgemma.py

# 4. Launch training (see fine-tuning section)
```

### Next Steps

1. **Expand raw datasets** with clinical expert review
2. **Augment data** using paraphrasing and scenario variation
3. **Train initial model** and evaluate
4. **Iterate** based on evaluation results
5. **Deploy** with safety rails and monitoring

---

## Contact

For questions about this training framework, contact the IHEP AI team.

---

*Document Version: 1.0*
*Last Updated: December 2024*
