"""
CLI tool for KJV Restored Names Converter
"""

import argparse
import json
import sys
from pathlib import Path
from converter import RestoredNamesConverter


def main():
    parser = argparse.ArgumentParser(
        description='Convert KJV Bible text to restored Hebrew names'
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input text or file path (if not provided, reads from stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (if not provided, writes to stdout)'
    )
    
    parser.add_argument(
        '-v', '--verse-aware',
        action='store_true',
        help='Enable verse-aware mode (checks for verse-specific overrides)'
    )
    
    parser.add_argument(
        '-w', '--enforce-witnesses',
        action='store_true',
        help='Only apply overrides that have witnesses'
    )
    
    parser.add_argument(
        '--overrides-file',
        default='overrides.json',
        help='Path to overrides.json file (default: overrides.json)'
    )
    
    parser.add_argument(
        '--add-override',
        nargs=4,
        metavar=('VERSE_REF', 'REPLACEMENT', 'WITNESSES', 'REQUIRE_WITNESS'),
        help='Add an override. VERSE_REF format: "Book Chapter:Verse". WITNESSES: comma-separated list (e.g., "cepher,dabar_yahuah"). REQUIRE_WITNESS: true/false'
    )
    
    parser.add_argument(
        '--list-overrides',
        action='store_true',
        help='List all current overrides'
    )
    
    parser.add_argument(
        '--remove-override',
        metavar='VERSE_REF',
        help='Remove an override for the specified verse reference'
    )
    
    args = parser.parse_args()
    
    converter = RestoredNamesConverter(overrides_file=args.overrides_file)
    
    # Handle override management commands
    if args.add_override:
        verse_ref, replacement, witnesses_str, require_witness_str = args.add_override
        witnesses = [w.strip() for w in witnesses_str.split(',')] if witnesses_str else []
        require_witness = require_witness_str.lower() == 'true'
        converter.add_override(verse_ref, replacement, witnesses, require_witness)
        print(f"Added override for {verse_ref}")
        return
    
    if args.list_overrides:
        if converter.overrides:
            print("Current overrides:")
            for verse_ref, override_data in converter.overrides.items():
                witnesses = override_data.get('witnesses', [])
                require_witness = override_data.get('require_witness', False)
                print(f"  {verse_ref}:")
                print(f"    Replacement: {override_data.get('replacement', 'N/A')}")
                print(f"    Witnesses: {', '.join(witnesses) if witnesses else 'None'}")
                print(f"    Require witness: {require_witness}")
        else:
            print("No overrides found.")
        return
    
    if args.remove_override:
        if args.remove_override in converter.overrides:
            del converter.overrides[args.remove_override]
            converter.save_overrides()
            print(f"Removed override for {args.remove_override}")
        else:
            print(f"No override found for {args.remove_override}")
        return
    
    # Handle text conversion
    # Read input
    if args.input:
        input_path = Path(args.input)
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # Treat as literal text
            text = args.input
    else:
        # Read from stdin
        text = sys.stdin.read()
    
    if not text.strip():
        print("Error: No input text provided", file=sys.stderr)
        sys.exit(1)
    
    # Convert text
    verse_ref = None
    if args.verse_aware:
        # Try to parse verse reference from text
        parsed = converter.parse_verse_reference(text)
        if parsed:
            verse_ref = converter.get_verse_key(*parsed)
    
    converted = converter.convert_text(
        text,
        verse_ref=verse_ref,
        verse_aware=args.verse_aware,
        enforce_witnesses=args.enforce_witnesses
    )
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(converted)
    else:
        print(converted)


if __name__ == '__main__':
    main()

