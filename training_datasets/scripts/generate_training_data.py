#!/usr/bin/env python3
"""
MedGemma Training Data Generation Pipeline for IHEP Digital Twins

This script generates comprehensive synthetic training data for fine-tuning
MedGemma or similar medical LLMs for the IHEP digital twins ecosystem.

Categories:
- Clinical decision support (HIV care, chronic diseases)
- Medication adherence interventions
- Mental health assessments and support
- Social determinants of health navigation
- Risk stratification and prediction
- Patient-AI conversational dialogues

All data is synthetic - no PHI is used or generated.
"""

import json
import random
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIRS = {
    "clinical": BASE_DIR / "clinical" / "processed",
    "adherence": BASE_DIR / "adherence" / "processed",
    "mental_health": BASE_DIR / "mental_health" / "processed",
    "social_determinants": BASE_DIR / "social_determinants" / "processed",
    "risk_prediction": BASE_DIR / "risk_prediction" / "processed",
    "conversational": BASE_DIR / "conversational" / "processed",
    "wearables": BASE_DIR / "wearables" / "processed",
    "financial_health": BASE_DIR / "financial_health" / "processed",
}

# ============================================================================
# Enums and Data Classes
# ============================================================================

class Condition(Enum):
    HIV = "HIV"
    DIABETES = "Type 2 Diabetes"
    HYPERTENSION = "Hypertension"
    DEPRESSION = "Depression"
    ANXIETY = "Anxiety"
    SUBSTANCE_USE = "Substance Use Disorder"
    CARDIOVASCULAR = "Cardiovascular Disease"
    CKD = "Chronic Kidney Disease"
    HEPATITIS_C = "Hepatitis C"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AdherenceBarrier(Enum):
    PILL_FATIGUE = "pill_fatigue"
    SIDE_EFFECTS = "side_effects"
    COST = "cost_financial"
    STIGMA = "stigma_disclosure"
    SCHEDULE = "irregular_schedule"
    ACCESS = "insurance_access"
    COMPLEXITY = "regimen_complexity"
    MENTAL_HEALTH = "mental_health"

class SdohDomain(Enum):
    HOUSING = "housing"
    FOOD = "food_security"
    TRANSPORTATION = "transportation"
    EMPLOYMENT = "employment"
    INSURANCE = "insurance"
    SOCIAL_SUPPORT = "social_support"
    SAFETY = "personal_safety"
    EDUCATION = "health_literacy"

@dataclass
class PatientProfile:
    """Synthetic patient profile for training data generation."""
    patient_id: str
    age: int
    gender: str
    conditions: List[str]
    hiv_status: Optional[str] = None  # "newly_diagnosed", "stable", "complex"
    viral_load: Optional[int] = None
    cd4_count: Optional[int] = None
    medication_regimen: Optional[str] = None
    adherence_rate: Optional[float] = None
    phq9_score: Optional[int] = None
    gad7_score: Optional[int] = None
    housing_status: Optional[str] = None
    insurance_status: Optional[str] = None
    employment_status: Optional[str] = None
    social_support: Optional[str] = None

    @classmethod
    def generate_random(cls) -> 'PatientProfile':
        """Generate a random patient profile for training data."""
        patient_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
        age = random.randint(18, 75)
        gender = random.choice(["male", "female", "non-binary", "transgender_female", "transgender_male"])

        # Generate conditions
        conditions = ["HIV"]  # Primary focus
        if random.random() < 0.3:
            conditions.append("Type 2 Diabetes")
        if random.random() < 0.35:
            conditions.append("Hypertension")
        if random.random() < 0.4:
            conditions.append("Depression")
        if random.random() < 0.25:
            conditions.append("Anxiety")

        # HIV-specific attributes
        hiv_status = random.choice(["newly_diagnosed", "stable", "complex"])

        if hiv_status == "newly_diagnosed":
            viral_load = random.randint(10000, 500000)
            cd4_count = random.randint(150, 500)
        elif hiv_status == "stable":
            viral_load = 0 if random.random() < 0.9 else random.randint(50, 500)
            cd4_count = random.randint(400, 1200)
        else:  # complex
            viral_load = random.randint(500, 50000)
            cd4_count = random.randint(100, 400)

        # Medication and adherence
        medication_regimen = random.choice([
            "Biktarvy", "Triumeq", "Dovato", "Genvoya", "Symtuza"
        ])
        adherence_rate = random.uniform(0.5, 1.0)

        # Mental health
        phq9_score = random.randint(0, 27)
        gad7_score = random.randint(0, 21)

        # Social determinants
        housing_status = random.choice(["stable", "unstable", "homeless"])
        insurance_status = random.choice(["medicaid", "private", "marketplace", "uninsured", "ryan_white"])
        employment_status = random.choice(["employed", "unemployed", "disabled", "student", "retired"])
        social_support = random.choice(["strong", "moderate", "limited", "none"])

        return cls(
            patient_id=patient_id,
            age=age,
            gender=gender,
            conditions=conditions,
            hiv_status=hiv_status,
            viral_load=viral_load,
            cd4_count=cd4_count,
            medication_regimen=medication_regimen,
            adherence_rate=adherence_rate,
            phq9_score=phq9_score,
            gad7_score=gad7_score,
            housing_status=housing_status,
            insurance_status=insurance_status,
            employment_status=employment_status,
            social_support=social_support
        )

@dataclass
class TrainingExample:
    """Base training example for MedGemma fine-tuning."""
    instruction: str
    input: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class ConversationExample:
    """Multi-turn conversation training example."""
    conversation_id: str
    turns: List[ConversationTurn]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        return json.dumps({
            "conversation_id": self.conversation_id,
            "turns": [{"role": t.role, "content": t.content} for t in self.turns],
            "metadata": self.metadata
        }, ensure_ascii=False)

# ============================================================================
# Data Generation Templates
# ============================================================================

# Clinical scenarios for HIV care
HIV_CLINICAL_TEMPLATES = [
    {
        "scenario": "viral_rebound",
        "instruction": "You are a clinical decision support AI for HIV care. Provide evidence-based guidance following DHHS HIV treatment guidelines.",
        "input_template": "Patient with {duration} HIV history, previously undetectable for {stable_years} years. Current viral load: {vl} copies/mL. CD4: {cd4}. Medication: {regimen}. {additional_context} What should we consider?",
        "factors": {
            "duration": ["2-year", "5-year", "10-year", "15-year", "20-year"],
            "stable_years": ["1", "2", "3", "5", "8"],
            "vl": [150, 500, 1200, 5000, 15000],
            "cd4": [250, 350, 450, 550, 650],
            "regimen": ["Biktarvy", "Triumeq", "Dovato", "Genvoya"],
            "additional_context": [
                "Patient reports occasional missed doses.",
                "Recent job loss and insurance change.",
                "Started new medication for hypertension.",
                "Reports increased alcohol use recently.",
                "Pharmacy records show 45-day gaps in refills."
            ]
        }
    },
    {
        "scenario": "new_diagnosis",
        "instruction": "You are a clinical decision support AI for HIV care. Provide evidence-based guidance following DHHS HIV treatment guidelines.",
        "input_template": "Newly diagnosed HIV patient. CD4: {cd4}. Viral load: {vl}. Age: {age}. {comorbidities}. {special_considerations}. What's the approach?",
        "factors": {
            "cd4": [150, 250, 350, 450, 550],
            "vl": [50000, 150000, 300000, 500000],
            "age": [22, 28, 35, 45, 58],
            "comorbidities": [
                "No significant comorbidities.",
                "History of depression.",
                "Type 2 diabetes, A1C 7.5%.",
                "Hepatitis B coinfection.",
                "Chronic kidney disease stage 3."
            ],
            "special_considerations": [
                "Patient is anxious about starting medications.",
                "Patient has substance use history.",
                "Patient lives in unstable housing.",
                "Patient is pregnant, 12 weeks.",
                "Patient is incarcerated."
            ]
        }
    }
]

# Adherence intervention templates
ADHERENCE_TEMPLATES = [
    {
        "barrier": AdherenceBarrier.PILL_FATIGUE,
        "input_template": "I've been missing my HIV medication {frequency} lately. {reason}.",
        "factors": {
            "frequency": ["once or twice a week", "2-3 times a week", "almost every day"],
            "reason": [
                "I'm just tired of taking pills every day.",
                "Some days I just don't see the point.",
                "It reminds me that I have HIV and I hate that.",
                "I feel fine so I don't think I need it.",
                "I forget because my routine is messed up."
            ]
        }
    },
    {
        "barrier": AdherenceBarrier.COST,
        "input_template": "My HIV medication costs {situation}. {consequence}.",
        "factors": {
            "situation": [
                "more than I can afford",
                "keep going up every month",
                "my whole paycheck some months"
            ],
            "consequence": [
                "I've been skipping doses to make it last longer.",
                "I haven't been able to refill this month.",
                "I'm having to choose between medication and rent.",
                "I stopped taking them entirely because I can't afford it.",
                "I'm rationing my pills."
            ]
        }
    }
]

# Mental health screening interpretation templates
MENTAL_HEALTH_TEMPLATES = [
    {
        "assessment": "PHQ9",
        "score_ranges": [
            {"min": 0, "max": 4, "severity": "minimal"},
            {"min": 5, "max": 9, "severity": "mild"},
            {"min": 10, "max": 14, "severity": "moderate"},
            {"min": 15, "max": 19, "severity": "moderately_severe"},
            {"min": 20, "max": 27, "severity": "severe"}
        ],
        "input_template": "I just took the PHQ-9 and scored {score}. {additional_context}",
        "additional_contexts": [
            "What does that mean?",
            "Is that bad?",
            "I've been feeling really down lately.",
            "I don't feel that bad, is the test wrong?",
            "This is the highest I've ever scored."
        ]
    },
    {
        "assessment": "GAD7",
        "score_ranges": [
            {"min": 0, "max": 4, "severity": "minimal"},
            {"min": 5, "max": 9, "severity": "mild"},
            {"min": 10, "max": 14, "severity": "moderate"},
            {"min": 15, "max": 21, "severity": "severe"}
        ],
        "input_template": "My GAD-7 score was {score}. {additional_context}",
        "additional_contexts": [
            "I feel anxious all the time.",
            "I can't seem to relax even when nothing is wrong.",
            "I'm worried about everything.",
            "My anxiety is affecting my work.",
            "I've started having panic attacks."
        ]
    }
]

# ============================================================================
# Data Generation Functions
# ============================================================================

def generate_clinical_training_data(num_examples: int = 100) -> List[TrainingExample]:
    """Generate clinical decision support training examples."""
    examples = []

    for _ in range(num_examples):
        template = random.choice(HIV_CLINICAL_TEMPLATES)

        # Fill in template with random factors
        input_text = template["input_template"]
        for factor, options in template["factors"].items():
            input_text = input_text.replace(f"{{{factor}}}", str(random.choice(options)))

        # Generate a comprehensive response (in production, these would be
        # carefully crafted by clinical experts)
        example = TrainingExample(
            instruction=template["instruction"],
            input=input_text,
            output="[Generated clinical response - see clinical/raw for examples]",
            metadata={
                "category": "clinical",
                "scenario": template["scenario"],
                "condition": "HIV",
                "generated": datetime.now().isoformat(),
                "source": "synthetic_generator"
            }
        )
        examples.append(example)

    return examples

def generate_adherence_training_data(num_examples: int = 100) -> List[TrainingExample]:
    """Generate medication adherence intervention training examples."""
    examples = []

    for _ in range(num_examples):
        template = random.choice(ADHERENCE_TEMPLATES)

        input_text = template["input_template"]
        for factor, options in template["factors"].items():
            input_text = input_text.replace(f"{{{factor}}}", random.choice(options))

        example = TrainingExample(
            instruction="You are an AI health coach specialized in medication adherence support for patients with chronic conditions. Provide empathetic, evidence-based guidance using motivational interviewing techniques.",
            input=input_text,
            output="[Generated adherence response - see adherence/raw for examples]",
            metadata={
                "category": "adherence",
                "barrier": template["barrier"].value,
                "condition": "HIV",
                "generated": datetime.now().isoformat(),
                "source": "synthetic_generator"
            }
        )
        examples.append(example)

    return examples

def generate_mental_health_training_data(num_examples: int = 100) -> List[TrainingExample]:
    """Generate mental health assessment and support training examples."""
    examples = []

    for _ in range(num_examples):
        template = random.choice(MENTAL_HEALTH_TEMPLATES)

        # Pick a score within one of the ranges
        score_range = random.choice(template["score_ranges"])
        score = random.randint(score_range["min"], score_range["max"])

        input_text = template["input_template"].format(
            score=score,
            additional_context=random.choice(template["additional_contexts"])
        )

        example = TrainingExample(
            instruction="You are a compassionate AI mental health support assistant integrated into a healthcare platform. You provide trauma-informed, evidence-based support while recognizing when professional intervention is needed.",
            input=input_text,
            output="[Generated mental health response - see mental_health/raw for examples]",
            metadata={
                "category": "mental_health",
                "assessment": template["assessment"],
                "score": score,
                "severity": score_range["severity"],
                "generated": datetime.now().isoformat(),
                "source": "synthetic_generator"
            }
        )
        examples.append(example)

    return examples

def generate_risk_prediction_training_data(num_examples: int = 50) -> List[TrainingExample]:
    """Generate risk stratification training examples."""
    examples = []

    for _ in range(num_examples):
        patient = PatientProfile.generate_random()

        # Build patient profile input
        profile_parts = [
            f"Age: {patient.age}, {patient.gender.replace('_', ' ').title()}",
            f"HIV duration: {random.choice(['1 year', '3 years', '5 years', '10 years', '15 years'])}",
            f"Current viral load: {'Undetectable' if patient.viral_load == 0 else f'{patient.viral_load} copies/mL'}",
            f"CD4 count: {patient.cd4_count}",
            f"Medication: {patient.medication_regimen}",
            f"Adherence (self-report): {int(patient.adherence_rate * 100)}%",
            f"PHQ-9 score: {patient.phq9_score}",
            f"Housing: {patient.housing_status.replace('_', ' ').title()}",
            f"Insurance: {patient.insurance_status.replace('_', ' ').title()}",
            f"Social support: {patient.social_support.replace('_', ' ').title()}"
        ]

        input_text = "Patient Profile:\n- " + "\n- ".join(profile_parts) + "\n\nAssess risk level and provide recommendations."

        example = TrainingExample(
            instruction="You are an AI clinical decision support system for risk stratification in HIV care. Analyze patient data to identify risk levels for disengagement from care, viral rebound, and adverse outcomes. Provide actionable recommendations with explanations.",
            input=input_text,
            output="[Generated risk assessment - see risk_prediction/raw for examples]",
            metadata={
                "category": "risk_prediction",
                "patient_profile": asdict(patient),
                "generated": datetime.now().isoformat(),
                "source": "synthetic_generator"
            }
        )
        examples.append(example)

    return examples

def generate_sdoh_training_data(num_examples: int = 100) -> List[TrainingExample]:
    """Generate social determinants of health training examples."""
    examples = []

    sdoh_scenarios = [
        {
            "domain": SdohDomain.HOUSING,
            "inputs": [
                "I just got evicted and I'm living in my car. I have HIV and don't know how to keep taking my medications.",
                "I'm about to lose my apartment because I can't pay rent. What resources are available?",
                "I've been couch surfing for months and it's affecting my health. Where can I get help?"
            ]
        },
        {
            "domain": SdohDomain.FOOD,
            "inputs": [
                "I can't afford to eat healthy with my diabetes. Fresh food is too expensive.",
                "I don't have enough food at home and I'm worried about my nutrition affecting my HIV treatment.",
                "I live in a food desert. The only store nearby has mostly junk food."
            ]
        },
        {
            "domain": SdohDomain.TRANSPORTATION,
            "inputs": [
                "I can't get to my doctor appointments because I don't have reliable transportation.",
                "The bus doesn't run near my clinic and I can't afford Uber.",
                "I missed my last appointment because my car broke down and I have no money to fix it."
            ]
        },
        {
            "domain": SdohDomain.EMPLOYMENT,
            "inputs": [
                "I lost my job because of my health issues. Now I have no income.",
                "I want to work but I'm worried about disclosing my HIV status to employers.",
                "I can't find a job that accommodates my medical appointments."
            ]
        }
    ]

    for scenario in sdoh_scenarios:
        for input_text in scenario["inputs"]:
            example = TrainingExample(
                instruction="You are an AI care navigator specialized in addressing social determinants of health (SDOH). You help connect patients with resources for housing, food security, transportation, employment, and other social needs while maintaining a compassionate, non-judgmental approach.",
                input=input_text,
                output="[Generated SDOH response - see social_determinants/raw for examples]",
                metadata={
                    "category": "social_determinants",
                    "domain": scenario["domain"].value,
                    "condition": "HIV",
                    "generated": datetime.now().isoformat(),
                    "source": "synthetic_generator"
                }
            )
            examples.append(example)

    return examples

def generate_wearables_training_data(num_examples: int = 50) -> List[TrainingExample]:
    """Generate wearable device data interpretation training examples."""
    examples = []

    wearable_scenarios = [
        {
            "data_type": "heart_rate",
            "input_template": "My smartwatch shows my resting heart rate has been {trend} over the past {period}. Current average: {value} bpm. {context}",
            "factors": {
                "trend": ["increasing", "decreasing", "fluctuating"],
                "period": ["week", "two weeks", "month"],
                "value": [65, 72, 85, 95, 110],
                "context": [
                    "I've been feeling more tired than usual.",
                    "I started a new medication recently.",
                    "I've been under a lot of stress at work.",
                    "I haven't changed anything in my routine.",
                    "I've been drinking more coffee lately."
                ]
            }
        },
        {
            "data_type": "sleep",
            "input_template": "My sleep tracker shows I'm averaging {hours} hours of sleep with {quality} quality. {pattern}. {concern}",
            "factors": {
                "hours": ["4-5", "5-6", "6-7", "7-8"],
                "quality": ["poor", "fair", "good"],
                "pattern": [
                    "I wake up multiple times at night",
                    "I have trouble falling asleep",
                    "I wake up too early and can't get back to sleep",
                    "My sleep is fragmented"
                ],
                "concern": [
                    "How does this affect my HIV treatment?",
                    "Should I be worried about my health?",
                    "What can I do to improve this?",
                    "Is this related to my medication?"
                ]
            }
        }
    ]

    for _ in range(num_examples):
        scenario = random.choice(wearable_scenarios)

        input_text = scenario["input_template"]
        for factor, options in scenario["factors"].items():
            input_text = input_text.replace(f"{{{factor}}}", str(random.choice(options)))

        example = TrainingExample(
            instruction="You are an AI health coach that interprets wearable device data in the context of chronic disease management. Provide personalized insights and recommendations while recognizing the limitations of consumer wearable data.",
            input=input_text,
            output="[Generated wearables interpretation - would include device-specific guidance]",
            metadata={
                "category": "wearables",
                "data_type": scenario["data_type"],
                "generated": datetime.now().isoformat(),
                "source": "synthetic_generator"
            }
        )
        examples.append(example)

    return examples

def save_training_data(examples: List[TrainingExample], output_path: Path, filename: str):
    """Save training examples to JSONL file."""
    output_path.mkdir(parents=True, exist_ok=True)
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(example.to_jsonl() + '\n')

    print(f"Saved {len(examples)} examples to {filepath}")

def main():
    """Main function to generate all training datasets."""
    print("=" * 60)
    print("MedGemma Training Data Generation Pipeline")
    print("IHEP Digital Twins Ecosystem")
    print("=" * 60)
    print()

    # Generate and save clinical data
    print("Generating clinical training data...")
    clinical_examples = generate_clinical_training_data(num_examples=200)
    save_training_data(clinical_examples, OUTPUT_DIRS["clinical"], "clinical_training.jsonl")

    # Generate and save adherence data
    print("Generating adherence training data...")
    adherence_examples = generate_adherence_training_data(num_examples=200)
    save_training_data(adherence_examples, OUTPUT_DIRS["adherence"], "adherence_training.jsonl")

    # Generate and save mental health data
    print("Generating mental health training data...")
    mental_health_examples = generate_mental_health_training_data(num_examples=150)
    save_training_data(mental_health_examples, OUTPUT_DIRS["mental_health"], "mental_health_training.jsonl")

    # Generate and save risk prediction data
    print("Generating risk prediction training data...")
    risk_examples = generate_risk_prediction_training_data(num_examples=100)
    save_training_data(risk_examples, OUTPUT_DIRS["risk_prediction"], "risk_training.jsonl")

    # Generate and save SDOH data
    print("Generating SDOH training data...")
    sdoh_examples = generate_sdoh_training_data(num_examples=100)
    save_training_data(sdoh_examples, OUTPUT_DIRS["social_determinants"], "sdoh_training.jsonl")

    # Generate and save wearables data
    print("Generating wearables training data...")
    wearables_examples = generate_wearables_training_data(num_examples=100)
    save_training_data(wearables_examples, OUTPUT_DIRS["wearables"], "wearables_training.jsonl")

    print()
    print("=" * 60)
    print("Training data generation complete!")
    print(f"Total examples generated: {len(clinical_examples) + len(adherence_examples) + len(mental_health_examples) + len(risk_examples) + len(sdoh_examples) + len(wearables_examples)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
