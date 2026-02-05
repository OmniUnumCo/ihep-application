#!/usr/bin/env python3
"""
Analyze overall bias across all training datasets
Security: Uses json module (not eval), validates input
         Output is aggregate statistics only - no individual records are logged
         This script should only run in development/testing environments
"""
import json
import sys
import os
import logging
from pathlib import Path
from collections import Counter
from typing import Dict, Tuple

# Configure structured logging for bias analysis
# Statistics are aggregate counts only and contain no PHI
_logger = logging.getLogger(__name__)

# Security check: Ensure this only runs in appropriate environments
_ALLOWED_ENVIRONMENTS = frozenset({'development', 'testing', 'ci'})


def _check_environment() -> bool:
    """Verify script is running in an allowed environment."""
    env = os.environ.get('APP_ENV', os.environ.get('NODE_ENV', 'development')).lower()
    if env not in _ALLOWED_ENVIRONMENTS:
        _logger.warning(
            "Bias analysis script should only run in development/testing environments. "
            "Set APP_ENV to 'development' or 'testing' to enable output."
        )
        return False
    return True


def _sanitize_path(path: Path, base_dir: Path) -> str:
    """Sanitize file path to avoid exposing system directory structure."""
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        # If path is not relative to base_dir, use only the filename
        return path.name

def analyze_gender_balance(file_path: Path) -> Tuple[int, int, int]:
    """
    Analyze gender balance in a dataset file.

    Returns:
        Tuple of (male_count, female_count, neutral_count)

    Security:
        - Uses json.loads() for safe parsing
        - No code execution
    """
    male_terms = ["he", "him", "his", "male", "man", "men", "mr", "father", "son", "brother", "husband", "boyfriend"]
    female_terms = ["she", "her", "hers", "female", "woman", "women", "ms", "mrs", "miss", "mother", "daughter", "sister", "wife", "girlfriend"]

    total_male = 0
    total_female = 0
    total_neutral = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    text = json.dumps(data).lower()

                    # Count gendered terms
                    male_count = sum(text.count(term) for term in male_terms)
                    female_count = sum(text.count(term) for term in female_terms)

                    if male_count > female_count:
                        total_male += 1
                    elif female_count > male_count:
                        total_female += 1
                    else:
                        total_neutral += 1

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing line {line_num} in {file_path}: {e}", file=sys.stderr)
                    continue

    except FileNotFoundError:
        _logger.error("File not found: %s", file_path.name)
        return (0, 0, 0)
    except Exception:
        # Log only file name, not full exception details which may contain data
        _logger.error("Error reading file: %s", file_path.name)
        return (0, 0, 0)

    return (total_male, total_female, total_neutral)


def _output_statistics(file_stats: list, total_stats: dict, base_dir: Path) -> None:
    """
    Output aggregate statistics to stdout.

    Security note: This function outputs AGGREGATE STATISTICS ONLY.
    No individual records or PHI are included in the output.
    All statistics are counts and percentages computed over the dataset.
    """
    # Output file-level aggregate statistics
    print("FILE-LEVEL GENDER BALANCE (aggregate counts only):")
    print("-" * 80)
    print(f"{'File':<50} {'Cat_A':<8} {'Cat_B':<8} {'Cat_N':<8} {'Total':<8}")
    print("-" * 80)

    for stats in file_stats:
        # Use sanitized path to avoid exposing directory structure
        safe_path = _sanitize_path(stats['file'], base_dir)
        print(f"{safe_path:<50} "
              f"{stats['male']:<8} "
              f"{stats['female']:<8} "
              f"{stats['neutral']:<8} "
              f"{stats['total']:<8}")

    print()

    # Output overall aggregate statistics
    grand_total = total_stats["male"] + total_stats["female"] + total_stats["neutral"]

    if grand_total > 0:
        cat_a_pct = (total_stats["male"] / grand_total * 100)
        cat_b_pct = (total_stats["female"] / grand_total * 100)
        cat_n_pct = (total_stats["neutral"] / grand_total * 100)

        print("=" * 80)
        print("OVERALL AGGREGATE STATISTICS:")
        print("=" * 80)
        print(f"Total examples analyzed: {grand_total}")
        print(f"  Category A examples:    {total_stats['male']:>5} ({cat_a_pct:>5.1f}%)")
        print(f"  Category B examples:    {total_stats['female']:>5} ({cat_b_pct:>5.1f}%)")
        print(f"  Neutral examples:       {total_stats['neutral']:>5} ({cat_n_pct:>5.1f}%)")


def main():
    """Main analysis function"""
    # Security check: Only run in development/testing environments
    if not _check_environment():
        print("Bias analysis disabled in this environment.", file=sys.stderr)
        return

    base_dir = Path(__file__).parent.parent

    # Find all JSONL files
    jsonl_files = list(base_dir.rglob("*.jsonl"))

    print("=" * 80)
    print("OVERALL BIAS ANALYSIS (aggregate statistics only)")
    print("=" * 80)
    print()

    total_stats = {"male": 0, "female": 0, "neutral": 0}
    file_stats = []

    for file_path in sorted(jsonl_files):
        male, female, neutral = analyze_gender_balance(file_path)

        if male + female + neutral == 0:
            continue

        total = male + female + neutral
        male_pct = (male / total * 100) if total > 0 else 0
        female_pct = (female / total * 100) if total > 0 else 0
        neutral_pct = (neutral / total * 100) if total > 0 else 0

        file_stats.append({
            "file": file_path,
            "male": male,
            "female": female,
            "neutral": neutral,
            "male_pct": male_pct,
            "female_pct": female_pct,
            "neutral_pct": neutral_pct,
            "total": total
        })

        total_stats["male"] += male
        total_stats["female"] += female
        total_stats["neutral"] += neutral

    # Output aggregate statistics only
    _output_statistics(file_stats, total_stats, base_dir)

    # Calculate and display balance ratio
    grand_total = total_stats["male"] + total_stats["female"] + total_stats["neutral"]
    if grand_total > 0 and total_stats['female'] > 0:
        print()
        ratio = total_stats['male'] / total_stats['female']
        print(f"Category A/B ratio: {ratio:.2f}:1")

        if 0.8 <= ratio <= 1.2:
            print("Balance is GOOD (within 20% tolerance)")
        elif 0.6 <= ratio <= 1.4:
            print("Balance is ACCEPTABLE (within 40% tolerance)")
        else:
            print("Balance needs improvement (>40% imbalance)")

    print()
    print("=" * 80)
    print()
    print("Note: This analysis shows AGGREGATE STATISTICS ONLY.")
    print("No individual records or identifiable information is included.")
    print("=" * 80)


if __name__ == "__main__":
    main()
