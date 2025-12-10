#!/usr/bin/env python3
"""
Analyze overall bias across all training datasets
Security: Uses json module (not eval), validates input
"""
import json
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, Tuple

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
        print(f"File not found: {file_path}", file=sys.stderr)
        return (0, 0, 0)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return (0, 0, 0)

    return (total_male, total_female, total_neutral)

def main():
    """Main analysis function"""
    base_dir = Path(__file__).parent.parent

    # Find all JSONL files
    jsonl_files = list(base_dir.rglob("*.jsonl"))

    print("=" * 80)
    print("OVERALL BIAS ANALYSIS")
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
            "file": file_path.relative_to(base_dir),
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

    # Print file-level statistics
    print("FILE-LEVEL GENDER BALANCE:")
    print("-" * 80)
    print(f"{'File':<50} {'Male':<8} {'Female':<8} {'Neutral':<8} {'Total':<8}")
    print("-" * 80)

    for stats in file_stats:
        print(f"{str(stats['file']):<50} "
              f"{stats['male']:<8} "
              f"{stats['female']:<8} "
              f"{stats['neutral']:<8} "
              f"{stats['total']:<8}")

    print()

    # Print overall statistics
    grand_total = total_stats["male"] + total_stats["female"] + total_stats["neutral"]

    if grand_total > 0:
        male_pct = (total_stats["male"] / grand_total * 100)
        female_pct = (total_stats["female"] / grand_total * 100)
        neutral_pct = (total_stats["neutral"] / grand_total * 100)

        print("=" * 80)
        print("OVERALL STATISTICS:")
        print("=" * 80)
        print(f"Total examples analyzed: {grand_total}")
        print(f"  Male-dominant examples:    {total_stats['male']:>5} ({male_pct:>5.1f}%)")
        print(f"  Female-dominant examples:  {total_stats['female']:>5} ({female_pct:>5.1f}%)")
        print(f"  Gender-neutral examples:   {total_stats['neutral']:>5} ({neutral_pct:>5.1f}%)")
        print()

        # Calculate balance ratio
        if total_stats['female'] > 0:
            ratio = total_stats['male'] / total_stats['female']
            print(f"Male/Female ratio: {ratio:.2f}:1")

            if 0.8 <= ratio <= 1.2:
                print("✅ Gender balance is GOOD (within 20% tolerance)")
            elif 0.6 <= ratio <= 1.4:
                print("⚠️  Gender balance is ACCEPTABLE (within 40% tolerance)")
            else:
                print("❌ Gender balance needs improvement (>40% imbalance)")

        print()
        print("=" * 80)
        print()
        print("Note: Individual examples with gender bias flags are EXPECTED and")
        print("appropriate when describing specific patient scenarios. What matters")
        print("is the OVERALL dataset balance, which is shown above.")
        print("=" * 80)

if __name__ == "__main__":
    main()
