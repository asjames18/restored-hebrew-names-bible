# KJV Restored Names Converter

A tool to convert King James Version (KJV) Bible text to use restored Hebrew names:
- **YAHUAH** (or **YAH** for short form contexts)
- **YAHUSHA**
- **HA'MASHIACH**
- **RUACH HAQODESH**

## Features

- **Default name mappings**: Automatically converts common KJV names to restored Hebrew names
- **Verse-aware mode**: Supports verse-specific overrides
- **Witnessed overrides**: Track which witnesses (Cepher, Dâbâr Yahuah) were consulted for specific verse decisions
- **Witness enforcement**: Option to only apply overrides that have been witnessed

## Important Constraints

⚠️ **This tool does NOT download, scrape, or embed verse text from Cepher Bible or Dâbâr Yahuah (Yahuah Bible).**

These sources may only be referenced as **witnesses** via user-provided, verse-level decisions (metadata) stored in `overrides.json`. The tool never copies their wording.

## Installation

No external dependencies required. Uses only Python standard library.

```bash
# Python 3.6+ required
python --version
```

## Usage

### Basic Conversion

Convert text from command line:

```bash
# From stdin
echo "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life." | python cli.py

# From file
python cli.py input.txt -o output.txt

# Direct text
python cli.py "Jesus Christ is Lord"
```

### Verse-Aware Mode

Enable verse-aware mode to check for verse-specific overrides:

```bash
python cli.py "John 3:16 For God so loved the world..." --verse-aware
```

### Enforce Witnesses

Only apply overrides that have witnesses:

```bash
python cli.py "John 3:16 ..." --verse-aware --enforce-witnesses
```

### Managing Overrides

#### Add an Override

```bash
python cli.py --add-override "John 3:16" "For YAHUAH so loved the world..." "cepher,dabar_yahuah" "true"
```

Parameters:
- `VERSE_REF`: Verse reference (e.g., "John 3:16")
- `REPLACEMENT`: The replacement text for this verse
- `WITNESSES`: Comma-separated list of witnesses (e.g., "cepher,dabar_yahuah")
- `REQUIRE_WITNESS`: "true" or "false" - if true, override only applies when witnesses are present

#### List Overrides

```bash
python cli.py --list-overrides
```

#### Remove an Override

```bash
python cli.py --remove-override "John 3:16"
```

## Overrides File Structure

The `overrides.json` file stores verse-specific overrides:

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

- `replacement`: The converted text for this specific verse
- `witnesses`: Array of witness sources consulted (e.g., `["cepher", "dabar_yahuah"]`)
- `require_witness`: Boolean indicating if witnesses are required for this override to apply

## Python API

```python
from converter import RestoredNamesConverter

# Initialize converter
converter = RestoredNamesConverter(overrides_file='overrides.json')

# Basic conversion
text = "For God so loved the world..."
converted = converter.convert_text(text)
print(converted)

# Verse-aware conversion
converted = converter.convert_verse(
    text="For God so loved the world...",
    book="John",
    chapter=3,
    verse=16,
    enforce_witnesses=False
)

# Add override
converter.add_override(
    verse_ref="John 3:16",
    replacement="For YAHUAH so loved the world...",
    witnesses=["cepher", "dabar_yahuah"],
    require_witness=True
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

## License

[Add your license here]
