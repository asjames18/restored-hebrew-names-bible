# KJV Restored Names Converter

A Python 3.11+ tool to convert King James Version (KJV) Bible text (public domain) to use restored Hebrew names:
- **YAHUAH** (or **YAH** for short form contexts)
- **YAHUSHA**
- **HA'MASHIACH**
- **RUACH HAQODESH**

## Features

- **Default name mappings**: Automatically converts common KJV names to restored Hebrew names
- **Verse-aware mode**: Supports verse-specific overrides
- **Witnessed overrides**: Track which witnesses (Cepher, Dâbâr Yahuah) were consulted for specific verse decisions
- **Witness enforcement**: Option to only apply overrides that have been witnessed
- **Multiple formats**: Support for plain text, JSON, and pipe-delimited formats
- **Conversion reports**: Generate detailed reports of conversions

## Important Constraints

### Source Text

- **KJV Input Only**: This tool uses the King James Version (KJV) as input text, which is in the public domain.
- **No Redistribution**: We do **NOT** download, scrape, embed, or redistribute verse text from Cepher Bible or Dâbâr Yahuah (Yahuah Bible).

### Witnessing

- **Witnessing** means user-verified placement notes only. When you mark a verse as "witnessed" by Cepher or Dâbâr Yahuah, you are recording that you manually verified the placement/context in those sources.
- Witness metadata in `overrides.json` is a record of your verification work, not a copy of their text.
- The tool never accesses, downloads, or stores any text from these external Bible sources.

### Overrides as Source of Truth

- **Overrides are the source of truth** for ambiguous cases. When a verse has an override in `overrides.json`, that override takes precedence over default conversion rules.
- Overrides allow you to specify exact replacements for ambiguous tokens (like "Lord" vs "LORD") based on your manual research and verification.
- The `--make-checklist` command helps identify verses that may need overrides, but the final decisions are recorded in `overrides.json`.

## Installation

### Prerequisites

- **Python 3.11 or higher** - [Download here](https://www.python.org/downloads/)
- **pip** (usually comes with Python)

**Windows Users:** During Python installation, make sure to check "Add Python to PATH"

### Quick Setup

```powershell
# Navigate to the kjv_restored directory
cd kjv_restored

# Install in development mode (recommended)
python -m pip install -e .

# Or install with dev dependencies (for testing)
python -m pip install -e .[dev]
```

### Verify Installation

```powershell
# Test the import
python -c "from kjv_restored import RestoredNamesConverter; print('Success!')"

# Or run the CLI
python -m kjv_restored --help
```

### Setup Script

A PowerShell setup script is provided to check your environment:

```powershell
.\setup.ps1
```

This will verify Python installation, check versions, and test imports.

### Requirements

- Python 3.11 or higher
- No external dependencies (uses only Python standard library)

For more detailed installation instructions, see [INSTALL.md](INSTALL.md).

## Usage

### Command Line Interface

```bash
# Basic usage with plain text
python -m kjv_restored --in data/sample_input.txt --out output.txt

# JSON format (verse objects)
python -m kjv_restored --in data/sample_verses.json --format json --out output.json

# Pipe format (one verse per line)
python -m kjv_restored --in input.txt --format pipe --out output.txt

# With strict mode and report
python -m kjv_restored --in input.txt --out output.txt --strict --report report.json

# Enforce witnesses only
python -m kjv_restored --in input.txt --out output.txt --enforce-witnesses

# Disable verse-aware mode
python -m kjv_restored --in input.txt --out output.txt --no-verse-aware

# Generate override checklist
python -m kjv_restored --make-checklist checklist.json --in data/sample_verses.json

# Automated witness checking (requires local Bible files)
python -m kjv_restored --auto-check --in data/kjv_verses.json --cepher-file data/cepher.json --dabar-yahuah-file data/dabar_yahuah.json --auto-overrides-output overrides.json

# Build full Bible document
python -m kjv_restored --build-bible --kjv data/kjv_verses.json --outdir out/ --title "The Restored Names KJV (RRG Standard v1.0)" --strict
```

### Command-Line Options

- `--in FILE`: Input file path (if not provided, reads from stdin)
- `--out FILE`: Output file path (if not provided, writes to stdout)
- `--format FORMAT`: Input/output format: `plain` (default), `json`, or `pipe`
- `--strict`: Enable strict mode (validates conversions)
- `--report FILE`: Generate conversion report JSON file
- `--overrides FILE`: Path to overrides.json file (default: overrides.json)
- `--enforce-witnesses`: Only apply overrides that have witnesses
- `--no-verse-aware`: Disable verse-aware mode (ignore overrides)
- `--make-checklist OUTPUT_FILE`: Generate override checklist from JSON input (requires `--in`)

### Formats

#### Plain Format
Simple text file with KJV text.

#### JSON Format
Array of verse objects:
```json
[
  {
    "book": "John",
    "chapter": 3,
    "verse": 16,
    "text": "For God so loved the world..."
  }
]
```

#### Pipe Format
One verse per line:
```
For God so loved the world...
In the beginning was the Word...
```

## Override Checklist

The `--make-checklist` command generates a checklist of verses that need manual review for overrides. This helps identify verses with ambiguous tokens that require decisions after checking Cepher/Yahuah Bible placements manually.

### Generate Checklist

```bash
python -m kjv_restored --make-checklist checklist.json --in data/sample_verses.json
```

The checklist identifies:
- **"Lord" (NT ambiguous)**: Verses with "Lord" (not all caps) that need a decision (YAHUAH if OT quote, ADON if NT reference)
- **"Praise ye the LORD"**: Hallelujah heuristic candidates
- **"JAH" token**: Verses containing the JAH token that may need overrides

### Checklist Format

```json
[
  {
    "ref": "Romans 10:13",
    "needs": "Lord decision",
    "suggested": "YAHUAH (if OT quote) or ADON (if NT reference)",
    "witnesses_required": ["cepher", "dabar_yahuah"]
  },
  {
    "ref": "Psalm 68:4",
    "needs": "JAH token review",
    "suggested": "YAH (KJV contains JAH)",
    "witnesses_required": ["kjv_token"]
  }
]
```

**Important**: The checklist never includes or stores any verse text from Cepher Bible or Dâbâr Yahuah. It only contains verse references and suggestions for manual review. Users fill out the checklist AFTER manually checking Cepher/Yahuah Bible placements.

## Automated Witness Checking

The `--auto-check` command automates the process of checking verses against local copies of Cepher Bible and Dâbâr Yahuah Bible files.

### Prerequisites

You must have local files containing the witness Bible texts. Supported formats:

**JSON Format** (same format as KJV input):
```json
[
  {
    "book": "Genesis",
    "chapter": 1,
    "verse": 1,
    "text": "In the beginning ELOHIYM created..."
  },
  ...
]
```

**DOCX Format** (Word document):
- Book names as headings (Heading 1 style or all caps)
- Chapter headings (Heading 2 style or "Chapter X")
- Verses with verse numbers (superscript or inline) followed by text
- Example: "1 In the beginning ELOHIYM created..."

**Important**: 
- You must provide your own local copies of these Bible files
- The tool does NOT download or scrape these files from the internet
- The tool does NOT redistribute these files
- You are responsible for obtaining these files legally
- DOCX parsing attempts to extract verse structure automatically

### Running Automated Checks

```powershell
# Using JSON files
python -m kjv_restored --auto-check `
  --in data/kjv_verses.json `
  --cepher-file data/cepher.json `
  --dabar-yahuah-file data/dabar_yahuah.json `
  --auto-overrides-output overrides.json `
  --min-witnesses 2 `
  --out check_report.json

# Using DOCX files
python -m kjv_restored --auto-check `
  --in data/kjv_verses.json `
  --cepher-file data/cepher_bible.docx `
  --dabar-yahuah-file data/dabar_yahuah_bible.docx `
  --auto-overrides-output overrides.json `
  --min-witnesses 2
```

### Options

- `--cepher-file`: Path to Cepher Bible JSON file (at least one witness file required)
- `--dabar-yahuah-file`: Path to Dâbâr Yahuah Bible JSON file (at least one witness file required)
- `--min-witnesses`: Minimum number of witnesses required (1 or 2)
  - `1`: Create overrides if found in either witness
  - `2`: Only create overrides if found in both witnesses (more conservative)
- `--auto-overrides-output`: File to save auto-generated overrides (will merge with existing overrides)
- `--out`: Optional file to save detailed check report

### How It Works

1. **Loads witness files**: Reads your local Cepher and Dâbâr Yahuah Bible files
2. **Compares verses**: For each KJV verse, checks if it exists in witness files
3. **Analyzes names**: Detects which restored names (YAHUAH, YAHUSHA, etc.) appear in witness texts
4. **Suggests replacements**: Automatically suggests replacements based on witness usage
5. **Generates overrides**: Creates `overrides.json` entries with witness metadata

### Example Output

```
Loading witness files...
Checking 31102 verses against witnesses...

Check Results:
  Total verses checked: 31102
  Found in Cepher: 31098
  Found in Dâbâr Yahuah: 31095
  With suggested replacements: 2847

Generating overrides (min_witnesses=2)...
Generated 2847 override entries: overrides.json
```

### Generated Overrides Format

The auto-generated overrides follow the standard format:

```json
{
  "Genesis 1:1": {
    "replacements": {
      "God": "ELOHIYM"
    },
    "witnesses": ["cepher", "dabar_yahuah"],
    "note": "Auto-generated from witness check (min_witnesses=2)"
  }
}
```

### Reviewing Auto-Generated Overrides

**Always review** auto-generated overrides before using them:
- Check a sample of generated overrides manually
- Verify the suggestions make sense in context
- Adjust `--min-witnesses` if too many/few overrides are generated
- Manually edit `overrides.json` to refine decisions

## Overrides File

The `overrides.json` file stores verse-specific overrides. **Overrides are the source of truth** for ambiguous cases and take precedence over default conversion rules.

### New Format (Recommended)

```json
{
  "Romans 10:13": {
    "replacements": {
      "Lord": "YAHUAH"
    },
    "witnesses": ["cepher", "dabar_yahuah"],
    "note": "OT quote placement"
  },
  "Psalm 68:4": {
    "replacements": {
      "JAH": "YAH"
    },
    "witnesses": ["kjv_token"],
    "note": "KJV contains JAH"
  }
}
```

### Legacy Format (Still Supported)

```json
{
  "John 3:16": {
    "replacement": "For YAHUAH so loved the world...",
    "witnesses": ["cepher", "dabar_yahuah"],
    "require_witness": true
  }
}
```

### Override Fields

- `replacements` (new format): Dictionary mapping original tokens to replacement text
- `replacement` (legacy format): Full verse replacement text
- `witnesses`: Array of witness sources consulted (e.g., `["cepher", "dabar_yahuah"]`)
  - **Note**: "Witnessing" means user-verified placement notes only. This records that you manually checked the verse in those sources, not that their text was copied.
- `require_witness`: Boolean indicating if witnesses are required for this override to apply
- `note`: Optional note about the override decision

## Python API

```python
from kjv_restored import RestoredNamesConverter, Config

# Initialize converter
config = Config(verse_aware=True, enforce_witnesses=False)
converter = RestoredNamesConverter(config=config)

# Basic conversion
text = "For God so loved the world..."
converted = converter.convert_text(text)
print(converted)

# Verse-aware conversion
converted = converter.convert_verse(
    text="For God so loved the world...",
    book="John",
    chapter=3,
    verse=16
)

# Batch convert multiple verses
verses = [
    {'text': '...', 'book': 'John', 'chapter': 3, 'verse': 16},
    {'text': '...', 'book': 'John', 'chapter': 3, 'verse': 17}
]
results = converter.batch_convert(verses)
```

## Default Mappings

The converter automatically replaces:

- `LORD`, `Lord`, `God` → `YAHUAH`
- `Jesus` → `YAHUSHA`
- `Christ`, `Messiah` → `HA'MASHIACH`
- `Holy Spirit`, `Holy Ghost` → `RUACH HAQODESH`
- `Jesus Christ` → `YAHUSHA HA'MASHIACH`
- `Christ Jesus` → `HA'MASHIACH YAHUSHA`
- `Hallelujah` → `HalleluYAH`

## Building Full Bible Documents

The `--build-bible` command generates complete Bible documents in both DOCX and PDF formats.

### Prerequisites

Install required dependencies:

```bash
pip install python-docx reportlab
```

### Input Format

The KJV verses must be provided as a JSON file with the following structure:

```json
[
  {
    "ref": "Genesis 1:1",
    "book": "Genesis",
    "chapter": 1,
    "verse": 1,
    "text": "In the beginning God created the heaven and the earth."
  },
  ...
]
```

**Important**: 
- The tool does NOT download or scrape Bible text from the internet
- You must provide your own KJV text file (public domain KJV is acceptable)
- The tool does NOT include or redistribute text from Cepher Bible or Dâbâr Yahuah
- Verses will be automatically sorted by canonical book order if not already sorted

### Where to Place KJV Data

Create a JSON file (e.g., `data/kjv_verses.json`) with all verses in the format shown above. The file should contain all 66 books of the Bible in verse-by-verse format.

### Building the Bible

**Bash/Linux/Mac:**
```bash
python -m kjv_restored --build-bible \
  --kjv data/kjv_verses.json \
  --outdir out/ \
  --title "The Restored Names KJV (RRG Standard v1.0)" \
  --version "v1.0" \
  --strict
```

**PowerShell (Windows):**
```powershell
python -m kjv_restored --build-bible `
  --kjv data/kjv_verses.json `
  --outdir out/ `
  --title "The Restored Names KJV (RRG Standard v1.0)" `
  --version "v1.0" `
  --strict
```

**Or on a single line:**
```powershell
python -m kjv_restored --build-bible --kjv data/kjv_verses.json --outdir out/ --title "The Restored Names KJV (RRG Standard v1.0)" --version "v1.0" --strict
```

This command generates:
- `out/restored_names_kjv.docx` - Word document
- `out/restored_names_kjv.pdf` - PDF document
- `out/restored_names_kjv.report.json` - Conversion report with statistics

### Output Features

**DOCX Output:**
- Title page with document title, version, and generation date
- Table of Contents listing all books
- Book headings (Heading 1 style)
- Chapter headings (Heading 2 style)
- Verses with superscript verse numbers
- Footer with document title

**PDF Output:**
- Title page with document title, version, and generation date
- Table of Contents listing all books
- Book headings styled distinctly
- Chapter headings styled distinctly
- Verses with inline verse numbers
- Page numbers in footer

### Strict Mode

When `--strict` is enabled:
- Ambiguous "Lord" tokens (NT, not all caps) are left unchanged unless an override exists
- All ambiguous cases are recorded in the report file
- The build still completes, but warnings are included in the report

### Report File

The report file (`restored_names_kjv.report.json`) includes:
- Statistics (total verses, books, chapters processed)
- Applied overrides list
- Ambiguous "Lord" occurrences
- Heuristic replacements applied
- Replacement counts

### Performance

The build process:
- Processes verses iteratively to minimize memory usage
- Logs progress every 1000 verses
- Handles large Bibles efficiently

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Test with mini Bible sample:

```bash
python -m kjv_restored --build-bible --kjv data/mini_kjv.json --outdir test_out/
```

## Project Structure

```
kjv_restored/
├── src/
│   └── kjv_restored/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── rules.py            # Name mapping rules
│       ├── converter.py        # Core converter
│       ├── io.py               # Input/output handling
│       ├── cli.py              # Command-line interface
│       └── witness.py          # Witness management
├── data/
│   ├── sample_input.txt
│   ├── sample_verses.json
│   └── overrides.example.json
├── tests/
│   ├── test_rules.py
│   ├── test_converter.py
│   └── test_witness.py
├── pyproject.toml
└── README.md
```

## License

MIT License

