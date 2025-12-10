#!/usr/bin/env python3
"""
Replace original files with gender-balanced versions
Security: Uses pathlib for safe file operations
"""
import sys
from pathlib import Path
import shutil

def main():
    """Replace original files with balanced versions"""
    base_dir = Path(__file__).parent.parent

    # Find all balanced files
    balanced_files = list(base_dir.rglob("*_balanced.jsonl"))

    print(f"Found {len(balanced_files)} balanced files to replace")
    print()

    replaced_count = 0
    error_count = 0

    for balanced_file in sorted(balanced_files):
        # Get original file path
        original_file = balanced_file.parent / balanced_file.name.replace("_balanced.jsonl", ".jsonl")

        print(f"Replacing: {original_file.relative_to(base_dir)}")

        try:
            # Backup original to .bak
            backup_file = original_file.with_suffix(".jsonl.bak")
            if original_file.exists():
                shutil.copy2(original_file, backup_file)
                print(f"  Backed up to: {backup_file.name}")

            # Replace with balanced version
            shutil.move(str(balanced_file), str(original_file))
            print(f"  ✅ Replaced successfully")
            replaced_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}", file=sys.stderr)
            error_count += 1

        print()

    print("=" * 80)
    print(f"Replaced: {replaced_count} files")
    print(f"Errors: {error_count} files")
    print()
    print("Original files backed up with .bak extension")
    print("=" * 80)

if __name__ == "__main__":
    main()
