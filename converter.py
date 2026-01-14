"""
KJV Restored Names Converter

Converts KJV Bible text to use restored Hebrew names:
- YAHUAH (or YAH for short form)
- YAHUSHA
- HA'MASHIACH
- RUACH HAQODESH

Supports verse-aware mode and witnessed overrides.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class RestoredNamesConverter:
    """Converts KJV text to restored Hebrew names."""
    
    # Default name mappings
    # Note: Patterns are applied with case-insensitive flag
    DEFAULT_MAPPINGS = [
        # Compound forms first (longer patterns)
        (r'\bLord\s+God\b', 'YAHUAH'),
        (r'\bJesus\s+Christ\b', "YAHUSHA HA'MASHIACH"),
        (r'\bChrist\s+Jesus\b', "HA'MASHIACH YAHUSHA"),
        (r'\bHoly\s+Spirit\b', 'RUACH HAQODESH'),
        (r'\bHoly\s+Ghost\b', 'RUACH HAQODESH'),
        
        # Primary names
        (r'\bLORD\b', 'YAHUAH'),
        (r'\bGod\b', 'YAHUAH'),
        (r'\bJesus\b', 'YAHUSHA'),
        (r'\bChrist\b', "HA'MASHIACH"),
        (r'\bMessiah\b', "HA'MASHIACH"),
    ]
    
    # Short form contexts (where YAH is used instead of YAHUAH)
    SHORT_FORM_PATTERNS = [
        r'\bHallelu\s*YAH\b',  # Hallelujah -> HalleluYAH
        r'\bYAH\s+weh\b',      # Yahweh contexts
    ]
    
    def __init__(self, overrides_file: Optional[str] = None):
        """
        Initialize converter.
        
        Args:
            overrides_file: Path to overrides.json file (optional)
        """
        self.overrides_file = Path(overrides_file) if overrides_file else Path('overrides.json')
        self.overrides: Dict[str, Dict] = {}
        self.load_overrides()
    
    def load_overrides(self) -> None:
        """Load overrides from JSON file if it exists."""
        if self.overrides_file.exists():
            try:
                with open(self.overrides_file, 'r', encoding='utf-8') as f:
                    self.overrides = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load overrides: {e}")
                self.overrides = {}
        else:
            self.overrides = {}
    
    def save_overrides(self) -> None:
        """Save overrides to JSON file."""
        with open(self.overrides_file, 'w', encoding='utf-8') as f:
            json.dump(self.overrides, f, indent=2, ensure_ascii=False)
    
    def parse_verse_reference(self, text: str) -> Optional[Tuple[str, int, int]]:
        """
        Parse verse reference from text.
        
        Expected formats:
        - "Genesis 1:1"
        - "1 John 3:16"
        - "John 3:16"
        - "John 3:16-17" (returns first verse)
        
        Returns:
            Tuple of (book, chapter, verse) or None
        """
        # Pattern for book chapter:verse (handles numbered books like "1 John")
        # Matches: optional number, space, book name, space, chapter:verse
        pattern = r'(\d*\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+):(\d+)'
        match = re.search(pattern, text)
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            return (book, chapter, verse)
        return None
    
    def get_verse_key(self, book: str, chapter: int, verse: int) -> str:
        """Generate verse key for overrides lookup."""
        return f"{book} {chapter}:{verse}"
    
    def has_override(self, verse_ref: str) -> bool:
        """Check if override exists for verse reference."""
        return verse_ref in self.overrides
    
    def get_override(self, verse_ref: str) -> Optional[Dict]:
        """Get override for verse reference."""
        return self.overrides.get(verse_ref)
    
    def add_override(
        self,
        verse_ref: str,
        replacement: str,
        witnesses: Optional[List[str]] = None,
        require_witness: bool = False
    ) -> None:
        """
        Add or update an override.
        
        Args:
            verse_ref: Verse reference (e.g., "John 3:16")
            replacement: The replacement text for this verse
            witnesses: List of witnesses checked (e.g., ["cepher", "dabar_yahuah"])
            require_witness: If True, override only applies if witnesses are present
        """
        self.overrides[verse_ref] = {
            'replacement': replacement,
            'witnesses': witnesses or [],
            'require_witness': require_witness
        }
        self.save_overrides()
    
    def apply_short_form(self, text: str) -> str:
        """Apply short form YAH where appropriate."""
        # Check for Hallelujah patterns
        text = re.sub(r'\bHallelu\s*jah\b', 'HalleluYAH', text, flags=re.IGNORECASE)
        text = re.sub(r'\bHallelu\s*YAH\b', 'HalleluYAH', text, flags=re.IGNORECASE)
        
        # In certain contexts, YAHUAH might be shortened to YAH
        # This is context-dependent and can be overridden per verse
        return text
    
    def convert_text(
        self,
        text: str,
        verse_ref: Optional[str] = None,
        verse_aware: bool = False,
        enforce_witnesses: bool = False
    ) -> str:
        """
        Convert KJV text to restored names.
        
        Args:
            text: Input KJV text
            verse_ref: Optional verse reference (e.g., "John 3:16")
            verse_aware: If True, check for verse-specific overrides
            enforce_witnesses: If True, only apply overrides with witnesses
        
        Returns:
            Converted text with restored names
        """
        result = text
        
        # Parse verse reference if not provided but verse_aware is True
        if verse_aware and not verse_ref:
            parsed_ref = self.parse_verse_reference(text)
            if parsed_ref:
                verse_ref = self.get_verse_key(*parsed_ref)
        
        # Check for verse-specific override
        if verse_aware and verse_ref:
            override = self.get_override(verse_ref)
            if override:
                # Check if we should apply this override
                should_apply = True
                
                # If enforce_witnesses is True, only apply overrides with witnesses
                if enforce_witnesses:
                    witnesses = override.get('witnesses', [])
                    if not witnesses:
                        # Skip override if no witnesses when enforcement is enabled
                        should_apply = False
                
                if should_apply:
                    return override['replacement']
        
        # Apply default mappings in order (already sorted by length, longer patterns first)
        for pattern, replacement in self.DEFAULT_MAPPINGS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Apply short form conversions
        result = self.apply_short_form(result)
        
        return result
    
    def convert_verse(
        self,
        text: str,
        book: str,
        chapter: int,
        verse: int,
        enforce_witnesses: bool = False
    ) -> str:
        """
        Convert a specific verse with verse-aware mode enabled.
        
        Args:
            text: Verse text
            book: Book name
            chapter: Chapter number
            verse: Verse number
            enforce_witnesses: If True, only apply overrides with witnesses
        
        Returns:
            Converted text
        """
        verse_ref = self.get_verse_key(book, chapter, verse)
        return self.convert_text(text, verse_ref=verse_ref, verse_aware=True, enforce_witnesses=enforce_witnesses)
    
    def batch_convert(
        self,
        verses: List[Dict[str, any]],
        enforce_witnesses: bool = False
    ) -> List[Dict[str, any]]:
        """
        Convert multiple verses.
        
        Args:
            verses: List of dicts with keys: 'text', 'book', 'chapter', 'verse'
            enforce_witnesses: If True, only apply overrides with witnesses
        
        Returns:
            List of converted verses with 'original' and 'converted' keys
        """
        results = []
        for verse in verses:
            original = verse.get('text', '')
            converted = self.convert_verse(
                original,
                verse['book'],
                verse['chapter'],
                verse['verse'],
                enforce_witnesses=enforce_witnesses
            )
            results.append({
                'book': verse['book'],
                'chapter': verse['chapter'],
                'verse': verse['verse'],
                'original': original,
                'converted': converted
            })
        return results

