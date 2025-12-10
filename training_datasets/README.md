# MedGemma Training Datasets for IHEP Digital Twins Ecosystem

## Overview

This directory contains comprehensive training datasets for fine-tuning MedGemma (or similar medical LLMs) to power the IHEP Digital Twins ecosystem. The datasets are specifically designed to address **life-altering conditions** including:

- HIV/AIDS management and care continuum
- Chronic disease management (diabetes, hypertension, cardiovascular)
- Mental health conditions (depression, anxiety, PTSD)
- Substance use disorders
- Social determinants of health challenges

## Directory Structure

```
training_datasets/
├── clinical/                    # Clinical data and medical knowledge
│   ├── raw/                     # Original clinical scenarios
│   ├── processed/               # Cleaned and formatted data
│   └── augmented/               # Synthetically expanded data
│
├── adherence/                   # Medication adherence patterns
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── mental_health/               # Mental health assessments
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── social_determinants/         # SDOH factors
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── risk_prediction/             # Risk stratification data
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── conversational/              # Patient-AI dialogue training
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── wearables/                   # Wearable device data interpretation
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── financial_health/            # Financial wellness training
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
├── federated_learning/          # Multi-site federated datasets
│   ├── raw/
│   ├── processed/
│   └── augmented/
│
└── evaluation/                  # Benchmark and evaluation sets
    ├── raw/
    ├── processed/
    └── augmented/
```

## Dataset Categories

### 1. Clinical Training Data (`clinical/`)
- Lab result interpretation (viral load, CD4 count, metabolic panels)
- Medication knowledge (ARVs, interactions, side effects)
- Clinical decision support scenarios
- Treatment guidelines and protocols
- Comorbidity management

### 2. Adherence Training Data (`adherence/`)
- Medication adherence pattern recognition
- Barrier identification and intervention strategies
- Motivational interviewing dialogues
- Appointment adherence scenarios
- Care retention strategies

### 3. Mental Health Training Data (`mental_health/`)
- PHQ-9 and GAD-7 interpretation
- Crisis detection and intervention
- Trauma-informed care responses
- Cognitive behavioral therapy support
- Wellness coaching dialogues

### 4. Social Determinants Training Data (`social_determinants/`)
- Housing instability interventions
- Food security resources
- Transportation barriers
- Employment support
- Social support network building

### 5. Risk Prediction Training Data (`risk_prediction/`)
- Disengagement risk factors
- Viral rebound prediction
- Hospitalization risk
- Mental health crisis prediction
- Comprehensive risk stratification

### 6. Conversational Training Data (`conversational/`)
- Patient onboarding dialogues
- Health education conversations
- Appointment reminders and follow-ups
- Emotional support interactions
- Care coordination communications

### 7. Wearables Training Data (`wearables/`)
- Biometric data interpretation
- Sleep pattern analysis
- Activity level coaching
- Heart rate variability insights
- Stress detection and response

### 8. Financial Health Training Data (`financial_health/`)
- Benefits navigation
- Medical debt counseling
- Insurance optimization
- Financial assistance programs
- Employment opportunities

### 9. Federated Learning Data (`federated_learning/`)
- Multi-site aggregated patterns
- Privacy-preserving insights
- Cross-institutional knowledge
- Population health trends

### 10. Evaluation Data (`evaluation/`)
- Benchmark test sets
- Safety evaluation scenarios
- Bias detection tests
- Clinical accuracy validation

## Data Format Standards

### Instruction-Response Format (JSONL)
```json
{
  "instruction": "System prompt or context",
  "input": "User query or patient scenario",
  "output": "Expected model response",
  "metadata": {
    "category": "clinical|adherence|mental_health|...",
    "condition": "HIV|diabetes|depression|...",
    "severity": "low|medium|high|critical",
    "evidence_level": "guideline|expert_consensus|research",
    "cultural_context": "general|specific_population",
    "language": "en",
    "source": "synthetic|clinical_expert|literature"
  }
}
```

### Conversation Format (JSONL)
```json
{
  "conversation_id": "uuid",
  "turns": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "metadata": {
    "scenario_type": "onboarding|crisis|education|...",
    "patient_profile": {...},
    "outcome": "successful|needs_escalation|..."
  }
}
```

## HIPAA Compliance

All training data in this repository is either:
1. **Fully synthetic** - Generated using clinical expert knowledge without any PHI
2. **De-identified** - Processed according to HIPAA Safe Harbor or Expert Determination
3. **Publicly available** - From published literature or public health resources

**No Protected Health Information (PHI) is stored in these datasets.**

## Training Pipeline

1. **Data Generation**: Run `python scripts/generate_training_data.py`
2. **Validation**: Run `python scripts/validate_datasets.py`
3. **Preprocessing**: Run `python scripts/preprocess_for_medgemma.py`
4. **Fine-tuning**: Use `configs/medgemma_finetune.yaml`
5. **Evaluation**: Run `python scripts/evaluate_model.py`

## Quality Assurance

Each dataset undergoes:
- Clinical accuracy review
- Bias detection analysis
- Safety evaluation (harmful content filtering)
- Cultural sensitivity review
- Readability assessment

## Contributing

When adding new training data:
1. Follow the format standards above
2. Include appropriate metadata
3. Ensure no PHI is present
4. Add to the appropriate category directory
5. Update the data manifest

## License

Training datasets are for internal IHEP use only. Commercial use requires explicit authorization.
