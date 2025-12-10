#!/usr/bin/env python3
"""
Dataset Validation Script for MedGemma Training Data

This script validates training datasets for:
- JSON format correctness
- Required field presence
- Content safety (no PHI, harmful content)
- Clinical accuracy markers
- Bias detection
- Quality metrics

All validation is logged for quality assurance tracking.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import hashlib

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
CATEGORIES = [
    "clinical",
    "adherence",
    "mental_health",
    "social_determinants",
    "risk_prediction",
    "conversational",
    "wearables",
    "financial_health",
]

# PHI patterns to flag
PHI_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b[A-Z]{2}\d{6,8}\b',  # State ID patterns
    r'\b\d{10}\b',  # Phone numbers (basic)
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email (except example domains)
    r'\b\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b',  # Street addresses
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Full dates
]

# Harmful content patterns
HARMFUL_PATTERNS = [
    r'\b(kill|murder|suicide method|how to die)\b',  # Explicit harm
    r'\b(hate|slur)\b',  # Hate speech markers
]

# Required metadata fields
REQUIRED_INSTRUCTION_FIELDS = ["instruction", "input", "output"]
REQUIRED_CONVERSATION_FIELDS = ["conversation_id", "turns"]
REQUIRED_METADATA = ["category", "source"]

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ValidationResult:
    """Result of validating a single example."""
    file_path: str
    line_number: int
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class DatasetReport:
    """Comprehensive validation report for a dataset."""
    dataset_path: str
    total_examples: int
    valid_examples: int
    invalid_examples: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    category_distribution: Dict[str, int] = field(default_factory=dict)
    severity_distribution: Dict[str, int] = field(default_factory=dict)
    phi_risks: List[Dict] = field(default_factory=list)
    bias_indicators: List[Dict] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    validation_time: str = ""

# ============================================================================
# Validation Functions
# ============================================================================

def check_json_format(line: str, line_num: int) -> Tuple[bool, Any, List[str]]:
    """Check if line is valid JSON."""
    errors = []
    try:
        data = json.loads(line)
        return True, data, errors
    except json.JSONDecodeError as e:
        errors.append(f"Line {line_num}: Invalid JSON - {str(e)}")
        return False, None, errors

def check_required_fields(data: Dict, line_num: int, is_conversation: bool = False) -> List[str]:
    """Check for required fields in training example."""
    errors = []

    if is_conversation:
        required = REQUIRED_CONVERSATION_FIELDS
    else:
        required = REQUIRED_INSTRUCTION_FIELDS

    for field in required:
        if field not in data:
            errors.append(f"Line {line_num}: Missing required field '{field}'")

    # Check metadata if present
    if "metadata" in data:
        for meta_field in REQUIRED_METADATA:
            if meta_field not in data["metadata"]:
                errors.append(f"Line {line_num}: Missing metadata field '{meta_field}'")

    return errors

def check_phi_presence(text: str, line_num: int) -> List[Dict]:
    """Check for potential PHI in text."""
    risks = []

    for pattern in PHI_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Skip if it's clearly synthetic/example data
            if not any(skip in text.lower() for skip in ["example", "sample", "test", "xxx-xx-xxxx"]):
                risks.append({
                    "line": line_num,
                    "pattern": pattern,
                    "matches": matches[:3],  # First 3 matches only
                    "severity": "high"
                })

    return risks

def check_harmful_content(text: str, line_num: int) -> List[str]:
    """Check for potentially harmful content."""
    warnings = []

    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            warnings.append(f"Line {line_num}: Potential harmful content pattern detected")
            break

    return warnings

def check_content_quality(data: Dict, line_num: int) -> Tuple[List[str], Dict[str, float]]:
    """Check content quality metrics."""
    warnings = []
    metrics = {}

    # Check input/output length
    if "input" in data:
        input_len = len(data["input"])
        if input_len < 20:
            warnings.append(f"Line {line_num}: Input too short ({input_len} chars)")
        elif input_len > 5000:
            warnings.append(f"Line {line_num}: Input very long ({input_len} chars)")
        metrics["avg_input_length"] = input_len

    if "output" in data:
        output_len = len(data["output"])
        if output_len < 50:
            warnings.append(f"Line {line_num}: Output too short ({output_len} chars)")
        metrics["avg_output_length"] = output_len

    # Check for placeholder content
    if "output" in data and "[Generated" in data["output"]:
        warnings.append(f"Line {line_num}: Contains placeholder output (not production-ready)")

    return warnings, metrics

def check_clinical_markers(data: Dict, line_num: int) -> List[str]:
    """Check for clinical accuracy markers."""
    warnings = []

    # Check for evidence level in metadata
    if "metadata" in data:
        if "evidence_level" not in data.get("metadata", {}):
            warnings.append(f"Line {line_num}: Missing evidence_level in clinical data")

    # Check for appropriate disclaimers in medical advice
    if "output" in data:
        output = data["output"].lower()
        medical_terms = ["medication", "treatment", "diagnosis", "prescribe"]

        if any(term in output for term in medical_terms):
            disclaimer_terms = ["consult", "provider", "professional", "doctor", "clinician"]
            if not any(term in output for term in disclaimer_terms):
                warnings.append(f"Line {line_num}: Medical advice may need provider referral language")

    return warnings

def check_bias_indicators(data: Dict, line_num: int) -> List[Dict]:
    """Check for potential bias in training data."""
    indicators = []

    text = json.dumps(data).lower()

    # Check for demographic imbalance markers
    gender_terms = {
        "male": ["he", "him", "his", "male", "man", "men"],
        "female": ["she", "her", "hers", "female", "woman", "women"]
    }

    # Count gendered language
    male_count = sum(text.count(term) for term in gender_terms["male"])
    female_count = sum(text.count(term) for term in gender_terms["female"])

    if male_count > 0 or female_count > 0:
        ratio = male_count / max(female_count, 1)
        if ratio > 3 or ratio < 0.33:
            indicators.append({
                "line": line_num,
                "type": "gender_imbalance",
                "ratio": round(ratio, 2),
                "male_count": male_count,
                "female_count": female_count
            })

    # Check for potentially stigmatizing language
    stigma_terms = ["addict", "junkie", "crazy", "psycho", "non-compliant"]
    for term in stigma_terms:
        if term in text:
            indicators.append({
                "line": line_num,
                "type": "stigmatizing_language",
                "term": term
            })

    return indicators

def validate_file(filepath: Path) -> DatasetReport:
    """Validate a single JSONL file."""
    report = DatasetReport(
        dataset_path=str(filepath),
        total_examples=0,
        valid_examples=0,
        invalid_examples=0,
        validation_time=datetime.now().isoformat()
    )

    category_counts = Counter()
    severity_counts = Counter()
    all_quality_metrics = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                report.total_examples += 1
                is_valid = True

                # Check JSON format
                json_valid, data, json_errors = check_json_format(line, line_num)
                report.errors.extend(json_errors)

                if not json_valid:
                    report.invalid_examples += 1
                    continue

                # Determine if conversation format
                is_conversation = "turns" in data

                # Check required fields
                field_errors = check_required_fields(data, line_num, is_conversation)
                if field_errors:
                    is_valid = False
                    report.errors.extend(field_errors)

                # Check for PHI
                text_content = json.dumps(data)
                phi_risks = check_phi_presence(text_content, line_num)
                if phi_risks:
                    report.phi_risks.extend(phi_risks)
                    is_valid = False

                # Check for harmful content
                harmful_warnings = check_harmful_content(text_content, line_num)
                report.warnings.extend(harmful_warnings)

                # Check content quality
                quality_warnings, quality_metrics = check_content_quality(data, line_num)
                report.warnings.extend(quality_warnings)
                all_quality_metrics.append(quality_metrics)

                # Check clinical markers (for clinical data)
                if data.get("metadata", {}).get("category") == "clinical":
                    clinical_warnings = check_clinical_markers(data, line_num)
                    report.warnings.extend(clinical_warnings)

                # Check bias indicators
                bias_indicators = check_bias_indicators(data, line_num)
                if bias_indicators:
                    report.bias_indicators.extend(bias_indicators)

                # Track distributions
                if "metadata" in data:
                    cat = data["metadata"].get("category", "unknown")
                    category_counts[cat] += 1

                    sev = data["metadata"].get("severity", "unknown")
                    severity_counts[sev] += 1

                if is_valid:
                    report.valid_examples += 1
                else:
                    report.invalid_examples += 1

        # Aggregate metrics
        report.category_distribution = dict(category_counts)
        report.severity_distribution = dict(severity_counts)

        if all_quality_metrics:
            avg_input = sum(m.get("avg_input_length", 0) for m in all_quality_metrics) / len(all_quality_metrics)
            avg_output = sum(m.get("avg_output_length", 0) for m in all_quality_metrics) / len(all_quality_metrics)
            report.quality_metrics = {
                "avg_input_length": round(avg_input, 2),
                "avg_output_length": round(avg_output, 2),
                "valid_percentage": round(report.valid_examples / max(report.total_examples, 1) * 100, 2)
            }

    except Exception as e:
        report.errors.append(f"File error: {str(e)}")

    return report

def generate_validation_report(reports: List[DatasetReport]) -> str:
    """Generate a comprehensive validation report."""
    lines = [
        "=" * 70,
        "MEDGEMMA TRAINING DATA VALIDATION REPORT",
        f"Generated: {datetime.now().isoformat()}",
        "=" * 70,
        ""
    ]

    # Summary statistics
    total_examples = sum(r.total_examples for r in reports)
    total_valid = sum(r.valid_examples for r in reports)
    total_invalid = sum(r.invalid_examples for r in reports)
    total_phi_risks = sum(len(r.phi_risks) for r in reports)
    total_bias_indicators = sum(len(r.bias_indicators) for r in reports)

    lines.extend([
        "SUMMARY",
        "-" * 40,
        f"Total Datasets: {len(reports)}",
        f"Total Examples: {total_examples}",
        f"Valid Examples: {total_valid} ({round(total_valid/max(total_examples,1)*100,1)}%)",
        f"Invalid Examples: {total_invalid}",
        f"PHI Risks Found: {total_phi_risks}",
        f"Bias Indicators: {total_bias_indicators}",
        ""
    ])

    # Per-dataset details
    lines.extend([
        "DATASET DETAILS",
        "-" * 40
    ])

    for report in reports:
        lines.extend([
            f"\n{Path(report.dataset_path).name}:",
            f"  Examples: {report.total_examples}",
            f"  Valid: {report.valid_examples}",
            f"  Invalid: {report.invalid_examples}",
            f"  Errors: {len(report.errors)}",
            f"  Warnings: {len(report.warnings)}",
            f"  PHI Risks: {len(report.phi_risks)}",
            f"  Bias Indicators: {len(report.bias_indicators)}"
        ])

        if report.category_distribution:
            lines.append(f"  Categories: {report.category_distribution}")

        if report.quality_metrics:
            lines.append(f"  Quality Metrics: {report.quality_metrics}")

    # Error details
    all_errors = []
    for report in reports:
        all_errors.extend(report.errors[:10])  # First 10 errors per file

    if all_errors:
        lines.extend([
            "",
            "ERRORS (First 50)",
            "-" * 40
        ])
        lines.extend(all_errors[:50])

    # PHI Risk details
    all_phi_risks = []
    for report in reports:
        all_phi_risks.extend(report.phi_risks[:5])

    if all_phi_risks:
        lines.extend([
            "",
            "PHI RISKS (Requires Review)",
            "-" * 40
        ])
        for risk in all_phi_risks[:20]:
            lines.append(f"  Line {risk['line']}: {risk['pattern']} - {risk['matches']}")

    # Bias indicator details
    all_bias = []
    for report in reports:
        all_bias.extend(report.bias_indicators[:5])

    if all_bias:
        lines.extend([
            "",
            "BIAS INDICATORS (Requires Review)",
            "-" * 40
        ])
        for indicator in all_bias[:20]:
            lines.append(f"  Line {indicator['line']}: {indicator['type']}")

    lines.extend([
        "",
        "=" * 70,
        "END OF REPORT",
        "=" * 70
    ])

    return "\n".join(lines)

def main():
    """Main validation function."""
    print("=" * 60)
    print("MedGemma Training Data Validation")
    print("=" * 60)
    print()

    reports = []

    # Find all JSONL files
    for category in CATEGORIES:
        category_dir = BASE_DIR / category
        if not category_dir.exists():
            print(f"Skipping {category} - directory not found")
            continue

        for subdir in ["raw", "processed", "augmented"]:
            subdir_path = category_dir / subdir
            if not subdir_path.exists():
                continue

            for jsonl_file in subdir_path.glob("*.jsonl"):
                print(f"Validating: {jsonl_file.name}")
                report = validate_file(jsonl_file)
                reports.append(report)

                status = "OK" if report.invalid_examples == 0 else "ISSUES"
                print(f"  Status: {status} ({report.valid_examples}/{report.total_examples} valid)")

    # Generate and save report
    if reports:
        validation_report = generate_validation_report(reports)

        report_path = BASE_DIR / "validation_report.txt"
        with open(report_path, 'w') as f:
            f.write(validation_report)

        print()
        print("=" * 60)
        print(f"Validation complete. Report saved to: {report_path}")
        print("=" * 60)
        print()
        print(validation_report)
    else:
        print("No datasets found to validate.")

if __name__ == "__main__":
    main()
