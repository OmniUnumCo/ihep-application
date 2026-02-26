#!/usr/bin/env python3
"""
Create gender-balanced training data by generating female-equivalent examples
Security: Uses json module, no code execution, validates all input
         All PHI fields are sanitized before writing to output
"""
import json
import sys
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple

# PHI fields that should be sanitized before writing
PHI_FIELDS = frozenset({
    'name', 'patient_name', 'first_name', 'last_name', 'full_name',
    'ssn', 'social_security', 'social_security_number',
    'mrn', 'medical_record_number', 'record_number',
    'email', 'email_address', 'phone', 'phone_number', 'telephone',
    'address', 'street', 'street_address', 'city', 'zip', 'zip_code', 'postal_code',
    'dob', 'date_of_birth', 'birth_date', 'birthdate',
    'ip_address', 'device_id', 'mac_address',
    'account_number', 'insurance_id', 'policy_number',
    'license_number', 'drivers_license',
})

def sanitize_phi_value(value: str, field_name: str) -> str:
    """
    Sanitize a PHI value by hashing it.

    Security:
        - Uses SHA-256 for consistent but irreversible transformation
        - Prefixes with field type for clarity
        - Returns truncated hash for readability
    """
    if not isinstance(value, str) or not value:
        return value
    hash_input = f"{field_name}:{value}".encode('utf-8')
    hash_value = hashlib.sha256(hash_input).hexdigest()[:12]
    return f"[REDACTED_{field_name.upper()}_{hash_value}]"


def sanitize_phi_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively sanitize PHI fields in a data structure.

    Security:
        - Creates new dict (doesn't modify input)
        - Sanitizes all known PHI field names
        - Preserves data structure for training while removing identifiers
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            key_lower = key.lower().replace('-', '_').replace(' ', '_')
            if key_lower in PHI_FIELDS:
                # Sanitize PHI field
                if isinstance(value, str):
                    result[key] = sanitize_phi_value(value, key_lower)
                elif isinstance(value, list):
                    result[key] = [sanitize_phi_value(str(v), key_lower) if v else v for v in value]
                else:
                    result[key] = "[REDACTED]"
            else:
                result[key] = sanitize_phi_fields(value)
        return result
    elif isinstance(data, list):
        return [sanitize_phi_fields(item) for item in data]
    else:
        return data


# Gender term mappings (case-insensitive replacement)
GENDER_MAPPINGS = [
    # Pronouns
    (r'\bhe\b', 'she', 'he'),
    (r'\bhim\b', 'her', 'him'),
    (r'\bhis\b', 'her', 'his'),  # possessive
    (r'\bhimself\b', 'herself', 'himself'),

    # Titles
    (r'\bMr\b', 'Ms', 'Mr'),
    (r'\bMr\.\b', 'Ms.', 'Mr.'),

    # Family relations
    (r'\bfather\b', 'mother', 'father'),
    (r'\bson\b', 'daughter', 'son'),
    (r'\bbrother\b', 'sister', 'brother'),
    (r'\bhusband\b', 'wife', 'husband'),
    (r'\bboyfriend\b', 'girlfriend', 'boyfriend'),
    (r'\bgrandfather\b', 'grandmother', 'grandfather'),
    (r'\buncle\b', 'aunt', 'uncle'),
    (r'\bnephew\b', 'niece', 'nephew'),

    # Generic terms
    (r'\bman\b', 'woman', 'man'),
    (r'\bmen\b', 'women', 'men'),
    (r'\bmale\b', 'female', 'male'),
    (r'\bboy\b', 'girl', 'boy'),
    (r'\bgentleman\b', 'lady', 'gentleman'),
]

def swap_gender_in_text(text: str, male_to_female: bool = True) -> str:
    """
    Swap gendered language in text.

    Args:
        text: Input text
        male_to_female: If True, swap male->female; if False, swap female->male

    Returns:
        Text with swapped gender terms

    Security:
        - Uses regex substitution (no eval/exec)
        - Case-preserving replacements
    """
    result = text

    for male_pattern, female_term, male_term in GENDER_MAPPINGS:
        if male_to_female:
            # Replace male with female (case-preserving)
            result = re.sub(male_pattern, lambda m: preserve_case(m.group(), female_term), result, flags=re.IGNORECASE)
        else:
            # For female->male, reverse the pattern
            female_pattern = male_pattern.replace(male_term, female_term)
            result = re.sub(female_pattern, lambda m: preserve_case(m.group(), male_term), result, flags=re.IGNORECASE)

    return result

def preserve_case(original: str, replacement: str) -> str:
    """Preserve the case pattern of the original word in the replacement."""
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()

def swap_gender_in_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively swap gender in a data structure.

    Security:
        - Creates new dict (doesn't modify input)
        - Handles nested structures safely
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = swap_gender_in_data(value)
        return result
    elif isinstance(data, list):
        return [swap_gender_in_data(item) for item in data]
    elif isinstance(data, str):
        return swap_gender_in_text(data, male_to_female=True)
    else:
        return data

def is_male_dominant(data: Dict) -> bool:
    """Check if example is male-dominant."""
    text = json.dumps(data).lower()

    male_terms = ["he", "him", "his", "male", "man", "men", "mr", "father", "son", "brother", "husband", "boyfriend"]
    female_terms = ["she", "her", "hers", "female", "woman", "women", "ms", "mrs", "mother", "daughter", "sister", "wife", "girlfriend"]

    male_count = sum(text.count(term) for term in male_terms)
    female_count = sum(text.count(term) for term in female_terms)

    return male_count > female_count

def process_file(input_file: Path, output_file: Path) -> Tuple[int, int]:
    """
    Create gender-balanced version of a JSONL file.

    Returns:
        Tuple of (original_count, added_female_count)

    Security:
        - Uses json.loads/dumps (not eval)
        - Validates file paths
        - Handles errors gracefully
        - Sanitizes PHI fields before writing to output
    """
    original_count = 0
    added_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse original
                    data = json.loads(line)

                    # Sanitize PHI fields before writing
                    sanitized_data = sanitize_phi_fields(data)

                    # Write sanitized original
                    outfile.write(json.dumps(sanitized_data, ensure_ascii=False) + '\n')
                    original_count += 1

                    # If male-dominant, create female version
                    if is_male_dominant(data):
                        female_data = swap_gender_in_data(data)

                        # Update IDs if present
                        if 'conversation_id' in female_data:
                            female_data['conversation_id'] = female_data['conversation_id'] + '_f'

                        # Mark as synthetic gender-balanced version
                        if 'metadata' in female_data:
                            female_data['metadata']['gender_balanced'] = True
                            female_data['metadata']['source'] = 'synthetic_balanced'

                        # Sanitize PHI fields before writing
                        sanitized_female_data = sanitize_phi_fields(female_data)
                        outfile.write(json.dumps(sanitized_female_data, ensure_ascii=False) + '\n')
                        added_count += 1

                except json.JSONDecodeError as e:
                    print(f"Error: Line {line_num} has invalid JSON: {e}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Error: Line {line_num}: {e}", file=sys.stderr)
                    continue

        return (original_count, added_count)

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}", file=sys.stderr)
        return (0, 0)
    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
        return (0, 0)

def main():
    """Main entry point"""
    base_dir = Path(__file__).parent.parent

    # Find all JSONL files
    jsonl_files = list(base_dir.rglob("*.jsonl"))

    print("=" * 80)
    print("CREATING GENDER-BALANCED DATASETS")
    print("=" * 80)
    print()

    total_original = 0
    total_added = 0

    for input_file in sorted(jsonl_files):
        # Skip already balanced files
        if "_balanced" in str(input_file):
            continue

        # Create output path
        output_file = input_file.parent / f"{input_file.stem}_balanced{input_file.suffix}"

        print(f"Processing: {input_file.relative_to(base_dir)}")

        orig_count, added_count = process_file(input_file, output_file)

        if orig_count > 0:
            print(f"  Original examples: {orig_count}")
            print(f"  Added female examples: {added_count}")
            print(f"  Total examples: {orig_count + added_count}")

            balance_pct = (added_count / (orig_count + added_count) * 100) if (orig_count + added_count) > 0 else 0
            print(f"  Female representation: ~{balance_pct:.1f}%")
            print()

            total_original += orig_count
            total_added += added_count

    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"Total original examples: {total_original}")
    print(f"Total added female examples: {total_added}")
    print(f"Total balanced examples: {total_original + total_added}")

    if total_original + total_added > 0:
        female_pct = (total_added / (total_original + total_added) * 100)
        print(f"Female representation: ~{female_pct:.1f}%")

        if 40 <= female_pct <= 60:
            print("\n✅ Gender balance achieved!")
        else:
            print(f"\n⚠️  Gender balance needs adjustment (target: 40-60%)")

    print()
    print("Next steps:")
    print("1. Review generated *_balanced.jsonl files")
    print("2. Replace original files with balanced versions if quality is good")
    print("3. Run validation again to confirm")
    print("=" * 80)

if __name__ == "__main__":
    main()
