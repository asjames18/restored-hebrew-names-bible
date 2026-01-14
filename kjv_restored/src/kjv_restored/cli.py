"""Command-line interface for KJV Restored Names Converter."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from kjv_restored.config import Config
from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.io import ConversionIO
from kjv_restored.checklist import ChecklistGenerator
from kjv_restored.assembler import BibleAssembler
from kjv_restored.export_docx import DOCXExporter
from kjv_restored.export_pdf import PDFExporter
from kjv_restored.books import normalize_book_name


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='Convert KJV Bible text to restored Hebrew names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m kjv_restored --in sample_input.txt --out out.txt
  python -m kjv_restored --in verses.json --format json --out out.json
  python -m kjv_restored --in input.txt --format pipe --strict --report report.json
  python -m kjv_restored --make-checklist checklist.json --in verses.json
        """
    )
    
    parser.add_argument(
        '--in',
        dest='input_file',
        type=str,
        help='Input file path (if not provided, reads from stdin)'
    )
    
    parser.add_argument(
        '--out',
        dest='output_file',
        type=str,
        help='Output file path (if not provided, writes to stdout)'
    )
    
    parser.add_argument(
        '--format',
        choices=['plain', 'json', 'pipe'],
        default='plain',
        help='Input/output format: plain (default), json (verse objects), pipe (one per line)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict mode (validates conversions)'
    )
    
    parser.add_argument(
        '--report',
        type=str,
        help='Generate conversion report JSON file'
    )
    
    parser.add_argument(
        '--overrides',
        type=str,
        help='Path to overrides.json file (default: overrides.json)'
    )
    
    parser.add_argument(
        '--enforce-witnesses',
        action='store_true',
        help='Only apply overrides that have witnesses'
    )
    
    parser.add_argument(
        '--no-verse-aware',
        action='store_true',
        help='Disable verse-aware mode (ignore overrides)'
    )
    
    parser.add_argument(
        '--make-checklist',
        type=str,
        metavar='OUTPUT_FILE',
        help='Generate override checklist from JSON input (requires --in)'
    )
    
    # Build Bible arguments
    parser.add_argument(
        '--build-bible',
        action='store_true',
        help='Build full Bible document (requires --kjv, --outdir, --title)'
    )
    parser.add_argument(
        '--kjv',
        type=str,
        help='Path to KJV verses JSON file (for build-bible)'
    )
    parser.add_argument(
        '--outdir',
        type=str,
        help='Output directory for generated files (for build-bible)'
    )
    parser.add_argument(
        '--title',
        type=str,
        default='The Restored Names KJV',
        help='Document title for build-bible (default: "The Restored Names KJV")'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='v1.0',
        help='Version string for build-bible (default: "v1.0")'
    )
    parser.add_argument(
        '--fail-on-unwitnessed',
        action='store_true',
        help='Fail if YAH-short overrides lack required witnesses (for build-bible)'
    )
    
    return parser


def save_report(report_path: Path, report: dict) -> None:
    """Save conversion report to JSON file."""
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def handle_build_bible(args) -> int:
    """
    Handle build-bible command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Validate required arguments
    if not args.kjv:
        print("Error: --build-bible requires --kjv to specify KJV verses JSON file", file=sys.stderr)
        return 1
    
    if not args.outdir:
        print("Error: --build-bible requires --outdir to specify output directory", file=sys.stderr)
        return 1
    
    kjv_path = Path(args.kjv)
    if not kjv_path.exists():
        print(f"Error: KJV file not found: {kjv_path}", file=sys.stderr)
        return 1
    
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Prepare paths
    overrides_path = Path(args.overrides) if args.overrides else Path("overrides.json")
    
    # Create configuration
    config = Config.from_args(
        overrides_file=str(overrides_path),
        strict=args.strict,
        enforce_witnesses=args.enforce_witnesses or args.fail_on_unwitnessed,
        verse_aware=not args.no_verse_aware
    )
    
    # Initialize converter and assembler
    converter = RestoredNamesConverter(config=config)
    assembler = BibleAssembler(converter)
    
    # Load verses
    print(f"Loading verses from {kjv_path}...", file=sys.stderr)
    verses = assembler.load_verses(kjv_path)
    print(f"Loaded {len(verses)} verses", file=sys.stderr)
    
    # Progress callback
    verse_count = 0
    def progress_callback(book=None, chapter=None, verse=None):
        nonlocal verse_count
        verse_count += 1
        if verse_count % 1000 == 0:
            print(f"Processed {verse_count} verses...", file=sys.stderr)
    
    # Collect books for TOC
    books_list = []
    for verse in verses:
        book = verse.get('book', '')
        normalized = normalize_book_name(book)
        if normalized not in books_list:
            books_list.append(normalized)
    
    # Export to DOCX
    print("Generating DOCX...", file=sys.stderr)
    try:
        # Reset converter tracking for fresh pass
        converter._applied_overrides = []
        converter._heuristic_replacements = []
        converter._ambiguous_lords = []
        
        docx_exporter = DOCXExporter(args.title, args.version)
        docx_path = outdir / "restored_names_kjv.docx"
        events = assembler.assemble(verses, progress_callback=progress_callback)
        docx_exporter.export(events, docx_path, progress_callback)
        print(f"Generated: {docx_path}", file=sys.stderr)
    except ImportError as e:
        print(f"Warning: DOCX export unavailable: {e}", file=sys.stderr)
        print("Install python-docx: pip install python-docx", file=sys.stderr)
    except Exception as e:
        print(f"Error generating DOCX: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    
    # Export to PDF
    print("Generating PDF...", file=sys.stderr)
    try:
        # Reset converter tracking for fresh pass
        converter._applied_overrides = []
        converter._heuristic_replacements = []
        converter._ambiguous_lords = []
        
        pdf_exporter = PDFExporter(args.title, args.version)
        pdf_path = outdir / "restored_names_kjv.pdf"
        events = assembler.assemble(verses, progress_callback=progress_callback)
        pdf_exporter.export(events, pdf_path, progress_callback)
        print(f"Generated: {pdf_path}", file=sys.stderr)
    except ImportError as e:
        print(f"Warning: PDF export unavailable: {e}", file=sys.stderr)
        print("Install reportlab: pip install reportlab", file=sys.stderr)
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    
    # Generate report
    report = assembler.generate_report(args.title, args.version)
    report_path = outdir / "restored_names_kjv.report.json"
    save_report(report_path, report)
    print(f"Generated: {report_path}", file=sys.stderr)
    
    print(f"\nBuild complete! Statistics:", file=sys.stderr)
    print(f"  Total verses: {report['statistics']['total_verses']}", file=sys.stderr)
    print(f"  Books: {report['statistics']['books_processed']}", file=sys.stderr)
    print(f"  Chapters: {report['statistics']['chapters_processed']}", file=sys.stderr)
    print(f"  Applied overrides: {report['statistics']['applied_overrides']}", file=sys.stderr)
    print(f"  Ambiguous Lords: {report['statistics']['ambiguous_lords']}", file=sys.stderr)
    
    return 0


def main(args: Optional[list] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        args: Command-line arguments (for testing)
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        # Handle build-bible command
        if parsed_args.build_bible:
            return handle_build_bible(parsed_args)
        
        # Handle checklist generation
        if parsed_args.make_checklist:
            if not parsed_args.input_file:
                print("Error: --make-checklist requires --in to specify input JSON file", file=sys.stderr)
                return 1
            
            input_path = Path(parsed_args.input_file)
            if not input_path.exists():
                print(f"Error: Input file not found: {input_path}", file=sys.stderr)
                return 1
            
            output_path = Path(parsed_args.make_checklist)
            generator = ChecklistGenerator()
            checklist = generator.generate_checklist(input_path, output_path)
            
            print(f"Generated checklist with {len(checklist)} items: {output_path}", file=sys.stderr)
            return 0
        
        # Prepare paths
        input_path = Path(parsed_args.input_file) if parsed_args.input_file else None
        output_path = Path(parsed_args.output_file) if parsed_args.output_file else None
        report_path = Path(parsed_args.report) if parsed_args.report else None
        overrides_path = Path(parsed_args.overrides) if parsed_args.overrides else Path("overrides.json")
        
        # Validate input file exists if provided
        if input_path and not input_path.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1
        
        # Create configuration
        config = Config.from_args(
            overrides_file=str(overrides_path),
            strict=parsed_args.strict,
            enforce_witnesses=parsed_args.enforce_witnesses,
            verse_aware=not parsed_args.no_verse_aware
        )
        
        # Initialize converter and IO handler
        converter = RestoredNamesConverter(config=config)
        io_handler = ConversionIO(converter)
        
        # Perform conversion
        report = io_handler.convert(
            input_path=input_path,
            output_path=output_path,
            format_type=parsed_args.format,
            strict=parsed_args.strict
        )
        
        # Add metadata to report
        report['config'] = {
            'strict_mode': config.strict_mode,
            'enforce_witnesses': config.enforce_witnesses,
            'verse_aware': config.verse_aware,
            'format': parsed_args.format
        }
        
        # Save report if requested
        if report_path:
            save_report(report_path, report)
        
        return 0
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

