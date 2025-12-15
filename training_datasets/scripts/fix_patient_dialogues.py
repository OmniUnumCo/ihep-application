#!/usr/bin/env python3
"""
Secure script to fix patient_dialogues.jsonl by adding missing 'category' field
Security: Uses json module (not eval), validates input, handles errors gracefully
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

def fix_patient_dialogues(input_file: Path, output_file: Path) -> None:
    """
    Add 'category' field to metadata of patient dialogue conversations.

    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file

    Security:
        - Uses json.loads() for safe parsing (not eval)
        - Validates data structure before modification
        - Handles errors gracefully
    """
    fixed_count = 0
    error_count = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            for line_num, line in enumerate(infile, 1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                try:
                    # Security: Use json.loads (not eval) for safe parsing
                    conversation = json.loads(line)

                    # Validate structure
                    if not isinstance(conversation, dict):
                        print(f"Warning: Line {line_num} is not a dict, skipping", file=sys.stderr)
                        error_count += 1
                        continue

                    if 'metadata' not in conversation:
                        print(f"Warning: Line {line_num} missing metadata, skipping", file=sys.stderr)
                        error_count += 1
                        continue

                    if not isinstance(conversation['metadata'], dict):
                        print(f"Warning: Line {line_num} metadata is not a dict, skipping", file=sys.stderr)
                        error_count += 1
                        continue

                    # Add category field if missing
                    if 'category' not in conversation['metadata']:
                        conversation['metadata']['category'] = 'conversational'
                        fixed_count += 1
                        print(f"Fixed line {line_num}: Added category='conversational'")

                    # Security: Use json.dumps for safe serialization
                    output_line = json.dumps(conversation, ensure_ascii=False)
                    outfile.write(output_line + '\n')

                except json.JSONDecodeError as e:
                    print(f"Error: Line {line_num} has invalid JSON: {e}", file=sys.stderr)
                    error_count += 1
                    continue
                except Exception as e:
                    print(f"Error: Line {line_num} unexpected error: {e}", file=sys.stderr)
                    error_count += 1
                    continue

        print(f"\nSummary:")
        print(f"  Fixed: {fixed_count} conversations")
        print(f"  Errors: {error_count} conversations")

    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied accessing files", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point"""
    # Define paths
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "conversational" / "raw" / "patient_dialogues.jsonl"
    output_file = base_dir / "conversational" / "raw" / "patient_dialogues_fixed.jsonl"

    print(f"Input file:  {input_file}")
    print(f"Output file: {output_file}")
    print()

    # Check input exists
    if not input_file.exists():
        print(f"Error: Input file does not exist: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Fix the file
    fix_patient_dialogues(input_file, output_file)

    # If successful, replace original
    print(f"\nReplacing original file with fixed version...")
    try:
        import shutil
        shutil.move(str(output_file), str(input_file))
        print(f"Success! Fixed file saved to: {input_file}")
    except Exception as e:
        print(f"Error replacing file: {e}", file=sys.stderr)
        print(f"Fixed version saved as: {output_file}")
        sys.exit(1)

if __name__ == "__main__":
    main()
