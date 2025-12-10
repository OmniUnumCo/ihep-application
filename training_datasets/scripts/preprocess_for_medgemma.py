#!/usr/bin/env python3
"""
MedGemma Preprocessing Pipeline for IHEP Training Data

This script preprocesses raw training data into formats optimized for
MedGemma fine-tuning, including:
- Tokenization and formatting
- Prompt template application
- Data augmentation
- Train/validation/test splits
- Quality filtering

Compatible with HuggingFace Transformers and custom training pipelines.
"""

import json
import yaml
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from collections import defaultdict

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "configs" / "medgemma_finetune.yaml"
OUTPUT_DIR = BASE_DIR / "processed_for_training"

# ============================================================================
# Prompt Templates
# ============================================================================

SYSTEM_PROMPTS = {
    "clinical": """You are a clinical decision support AI for HIV care and chronic disease management. You provide evidence-based guidance following DHHS HIV treatment guidelines and established clinical protocols. Always be thorough, accurate, and recommend consulting with healthcare providers for clinical decisions.""",

    "adherence": """You are an AI health coach specialized in medication adherence support for patients with chronic conditions. Use motivational interviewing techniques and empathetic communication. Address barriers without judgment and provide practical, actionable solutions. Recognize when to escalate to human healthcare providers.""",

    "mental_health": """You are a compassionate AI mental health support assistant integrated into a healthcare platform. You provide trauma-informed, evidence-based support while recognizing when professional intervention is needed. You never diagnose but help identify concerns and connect people with appropriate resources. If someone expresses suicidal ideation, immediately provide crisis resources.""",

    "social_determinants": """You are an AI care navigator specialized in addressing social determinants of health (SDOH). You help connect patients with resources for housing, food security, transportation, employment, and other social needs while maintaining a compassionate, non-judgmental approach.""",

    "risk_prediction": """You are an AI clinical decision support system for risk stratification in HIV care. Analyze patient data to identify risk levels for disengagement from care, viral rebound, and adverse outcomes. Provide actionable recommendations with explanations that are transparent and understandable to clinicians.""",

    "conversational": """You are a compassionate AI health assistant for the IHEP digital health platform. You provide personalized health guidance, medication reminders, appointment support, and emotional support while maintaining HIPAA compliance. You speak in a warm, professional tone and recognize when to escalate to human providers.""",

    "wearables": """You are an AI health coach that interprets wearable device data in the context of chronic disease management. Provide personalized insights and recommendations while recognizing the limitations of consumer wearable data. Always frame interpretations appropriately and recommend professional evaluation when concerning patterns are detected.""",

    "financial_health": """You are an AI financial wellness navigator for healthcare. You help patients navigate insurance, medication costs, financial assistance programs, and employment benefits. You provide accurate information about resources while being sensitive to financial stress and its health impacts."""
}

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ProcessedExample:
    """A processed training example ready for fine-tuning."""
    id: str
    text: str  # Full formatted text for training
    input_ids: Optional[List[int]] = None
    attention_mask: Optional[List[int]] = None
    labels: Optional[List[int]] = None
    metadata: Dict[str, Any] = None

@dataclass
class DatasetStats:
    """Statistics for a processed dataset."""
    total_examples: int
    avg_length: float
    min_length: int
    max_length: int
    category_distribution: Dict[str, int]
    train_count: int
    val_count: int
    test_count: int

# ============================================================================
# Preprocessing Functions
# ============================================================================

def load_config() -> Dict:
    """Load the fine-tuning configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {}

def load_jsonl(filepath: Path) -> List[Dict]:
    """Load a JSONL file."""
    examples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return examples

def get_category_from_path(filepath: Path) -> str:
    """Extract category from file path."""
    parts = filepath.parts
    for category in SYSTEM_PROMPTS.keys():
        if category in parts:
            return category
    # Try to infer from parent directory
    parent = filepath.parent.parent.name
    if parent in SYSTEM_PROMPTS:
        return parent
    return "conversational"  # default

def format_instruction_example(
    example: Dict,
    category: str,
    include_system: bool = True
) -> str:
    """Format an instruction-following example for training."""
    parts = []

    # System prompt
    if include_system:
        system_prompt = SYSTEM_PROMPTS.get(category, SYSTEM_PROMPTS["conversational"])
        parts.append(f"<|system|>\n{system_prompt}\n</|system|>")

    # Instruction (if separate from input)
    if "instruction" in example and example["instruction"]:
        # Only include if different from system prompt
        if example["instruction"] != system_prompt:
            parts.append(f"<|instruction|>\n{example['instruction']}\n</|instruction|>")

    # User input
    if "input" in example:
        parts.append(f"<|user|>\n{example['input']}\n</|user|>")

    # Assistant output
    if "output" in example:
        parts.append(f"<|assistant|>\n{example['output']}\n</|assistant|>")

    return "\n\n".join(parts)

def format_conversation_example(
    example: Dict,
    category: str = "conversational"
) -> str:
    """Format a multi-turn conversation for training."""
    parts = []

    if "turns" not in example:
        return ""

    for turn in example["turns"]:
        role = turn.get("role", "user")
        content = turn.get("content", "")

        if role == "system":
            parts.append(f"<|system|>\n{content}\n</|system|>")
        elif role == "user":
            parts.append(f"<|user|>\n{content}\n</|user|>")
        elif role == "assistant":
            parts.append(f"<|assistant|>\n{content}\n</|assistant|>")

    return "\n\n".join(parts)

def generate_example_id(example: Dict) -> str:
    """Generate a unique ID for an example."""
    content = json.dumps(example, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')

    return text.strip()

def apply_quality_filter(example: Dict, text: str) -> bool:
    """Filter out low-quality examples."""
    # Skip very short outputs
    if "output" in example and len(example["output"]) < 50:
        return False

    # Skip placeholder outputs
    if "[Generated" in text or "TODO" in text:
        return False

    # Skip examples with broken formatting
    if text.count("<|") != text.count("|>"):
        return False

    # Skip examples that are too long (will be truncated anyway)
    if len(text) > 20000:
        return False

    return True

def augment_example(example: Dict, category: str) -> List[Dict]:
    """Apply data augmentation to create variations."""
    augmented = [example]  # Original example

    # Only augment non-placeholder examples
    if "output" in example and "[Generated" in example["output"]:
        return augmented

    # Paraphrasing variations for inputs
    if "input" in example and random.random() < 0.3:
        variations = [
            ("I'm", "I am"),
            ("don't", "do not"),
            ("can't", "cannot"),
            ("it's", "it is"),
            ("I've", "I have"),
        ]

        augmented_input = example["input"]
        for old, new in random.sample(variations, min(2, len(variations))):
            augmented_input = augmented_input.replace(old, new)

        if augmented_input != example["input"]:
            new_example = example.copy()
            new_example["input"] = augmented_input
            augmented.append(new_example)

    return augmented

def split_data(
    examples: List[ProcessedExample],
    train_ratio: float = 0.85,
    val_ratio: float = 0.10,
    test_ratio: float = 0.05,
    seed: int = 42
) -> Tuple[List, List, List]:
    """Split examples into train/val/test sets."""
    random.seed(seed)
    shuffled = examples.copy()
    random.shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    train = shuffled[:train_end]
    val = shuffled[train_end:val_end]
    test = shuffled[val_end:]

    return train, val, test

def process_file(filepath: Path, config: Dict) -> List[ProcessedExample]:
    """Process a single JSONL file."""
    examples = load_jsonl(filepath)
    category = get_category_from_path(filepath)
    processed = []

    for example in examples:
        # Determine format
        if "turns" in example:
            text = format_conversation_example(example, category)
        else:
            text = format_instruction_example(example, category)

        # Clean text
        text = clean_text(text)

        # Quality filter
        if not apply_quality_filter(example, text):
            continue

        # Create processed example
        example_id = generate_example_id(example)
        metadata = example.get("metadata", {})
        metadata["source_file"] = str(filepath)
        metadata["category"] = category

        processed_example = ProcessedExample(
            id=example_id,
            text=text,
            metadata=metadata
        )
        processed.append(processed_example)

        # Augmentation
        if config.get("augmentation", {}).get("enabled", False):
            augmented = augment_example(example, category)
            for aug_example in augmented[1:]:  # Skip original
                if "turns" in aug_example:
                    aug_text = format_conversation_example(aug_example, category)
                else:
                    aug_text = format_instruction_example(aug_example, category)
                aug_text = clean_text(aug_text)

                if apply_quality_filter(aug_example, aug_text):
                    aug_id = generate_example_id(aug_example) + "_aug"
                    processed.append(ProcessedExample(
                        id=aug_id,
                        text=aug_text,
                        metadata={**metadata, "augmented": True}
                    ))

    return processed

def save_dataset(
    examples: List[ProcessedExample],
    output_path: Path,
    format: str = "jsonl"
):
    """Save processed examples to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "jsonl":
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                record = {
                    "id": example.id,
                    "text": example.text,
                    "metadata": example.metadata
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

    elif format == "parquet":
        # Requires pandas and pyarrow
        try:
            import pandas as pd
            df = pd.DataFrame([
                {"id": e.id, "text": e.text, **e.metadata}
                for e in examples
            ])
            df.to_parquet(output_path.with_suffix('.parquet'))
        except ImportError:
            print("Warning: pandas/pyarrow not available, saving as JSONL")
            save_dataset(examples, output_path, format="jsonl")

def compute_stats(examples: List[ProcessedExample]) -> DatasetStats:
    """Compute statistics for a processed dataset."""
    lengths = [len(e.text) for e in examples]
    categories = defaultdict(int)

    for e in examples:
        cat = e.metadata.get("category", "unknown")
        categories[cat] += 1

    return DatasetStats(
        total_examples=len(examples),
        avg_length=sum(lengths) / len(lengths) if lengths else 0,
        min_length=min(lengths) if lengths else 0,
        max_length=max(lengths) if lengths else 0,
        category_distribution=dict(categories),
        train_count=0,  # Set after split
        val_count=0,
        test_count=0
    )

def main():
    """Main preprocessing pipeline."""
    print("=" * 60)
    print("MedGemma Preprocessing Pipeline")
    print("IHEP Digital Twins Training Data")
    print("=" * 60)
    print()

    # Load configuration
    config = load_config()

    # Find all raw data files
    raw_dirs = [
        BASE_DIR / "clinical" / "raw",
        BASE_DIR / "adherence" / "raw",
        BASE_DIR / "mental_health" / "raw",
        BASE_DIR / "social_determinants" / "raw",
        BASE_DIR / "risk_prediction" / "raw",
        BASE_DIR / "conversational" / "raw",
        BASE_DIR / "wearables" / "raw",
        BASE_DIR / "financial_health" / "raw",
    ]

    all_examples = []

    for raw_dir in raw_dirs:
        if not raw_dir.exists():
            continue

        for jsonl_file in raw_dir.glob("*.jsonl"):
            print(f"Processing: {jsonl_file.name}")
            examples = process_file(jsonl_file, config)
            all_examples.extend(examples)
            print(f"  -> {len(examples)} examples")

    print()
    print(f"Total examples: {len(all_examples)}")

    if not all_examples:
        print("No examples to process.")
        return

    # Compute statistics
    stats = compute_stats(all_examples)
    print(f"Average length: {stats.avg_length:.0f} chars")
    print(f"Category distribution: {stats.category_distribution}")

    # Split data
    print()
    print("Splitting data...")
    train, val, test = split_data(all_examples)
    stats.train_count = len(train)
    stats.val_count = len(val)
    stats.test_count = len(test)

    print(f"Train: {len(train)}")
    print(f"Validation: {len(val)}")
    print(f"Test: {len(test)}")

    # Save datasets
    print()
    print("Saving processed datasets...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    save_dataset(train, OUTPUT_DIR / "train.jsonl")
    save_dataset(val, OUTPUT_DIR / "validation.jsonl")
    save_dataset(test, OUTPUT_DIR / "test.jsonl")

    # Save combined for some training frameworks
    save_dataset(all_examples, OUTPUT_DIR / "all_data.jsonl")

    # Save statistics
    stats_dict = asdict(stats)
    stats_dict["processed_at"] = datetime.now().isoformat()
    with open(OUTPUT_DIR / "dataset_stats.json", 'w') as f:
        json.dump(stats_dict, f, indent=2)

    print()
    print("=" * 60)
    print("Preprocessing complete!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
