"""Core converter for KJV to restored Hebrew names."""

import re
from typing import Dict, List, Optional, Tuple

from kjv_restored.rules import NameRules
from kjv_restored.witness import WitnessManager
from kjv_restored.config import Config


class RestoredNamesConverter:
    """Converts KJV text to restored Hebrew names."""
    
    def __init__(self, config: Optional[Config] = None, witness_manager: Optional[WitnessManager] = None):
        """
        Initialize converter.
        
        Args:
            config: Configuration object
            witness_manager: Witness manager instance
        """
        self.config = config or Config()
        self.witness_manager = witness_manager or WitnessManager(self.config.overrides_file)
        self._applied_overrides = []  # Track applied overrides for reporting
        self._heuristic_replacements = []  # Track heuristic replacements
        self._ambiguous_lords = []  # Track ambiguous Lord occurrences
    
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
    
    def convert_text(
        self,
        text: str,
        verse_ref: Optional[str] = None,
        strict: Optional[bool] = None
    ) -> str:
        """
        Convert KJV text to restored names.
        
        Args:
            text: Input KJV text
            verse_ref: Optional verse reference (e.g., "John 3:16")
            strict: Override config strict_mode (if provided)
        
        Returns:
            Converted text with restored names
        """
        result = text
        strict_mode = strict if strict is not None else self.config.strict_mode
        
        # Parse verse reference if not provided but verse_aware is True
        if self.config.verse_aware and not verse_ref:
            parsed_ref = self.parse_verse_reference(text)
            if parsed_ref:
                verse_ref = self.get_verse_key(*parsed_ref)
        
        # Check for verse-specific override
        if self.config.verse_aware and verse_ref:
            replacements = self.witness_manager.get_replacements(
                verse_ref,
                enforce_witnesses=self.config.enforce_witnesses,
                short_name_mode=self.config.short_name_mode
            )
            if replacements is not None:
                # Apply replacements
                result = self._apply_replacements(result, replacements)
                # Store override info for reporting
                self._applied_overrides.append({
                    'verse_ref': verse_ref,
                    'replacements': replacements,
                    'witnesses': self.witness_manager.get_override(verse_ref).get('witnesses', [])
                })
                return result
        
        # Track ambiguous "Lord" occurrences before conversion
        ambiguous_lords = []
        if re.search(r'\bLord\b', result) and not re.search(r'\bLORD\b', result):
            # Found "Lord" (not all caps) - this is ambiguous
            ambiguous_lords.append({
                'verse_ref': verse_ref or 'unknown',
                'text': result
            })
        
        # Apply JAH -> YAH conversion if short_name_mode is not "off"
        jah_changed = False
        if self.config.short_name_mode != "off":
            result, jah_changed = NameRules.convert_jah_to_yah(result)
        
        # Apply Hallelujah heuristic if enabled (before default mappings to catch "LORD")
        hallelujah_changed = False
        if self.config.hallelujah_heuristic:
            result, hallelujah_changed = NameRules.apply_hallelujah_heuristic(result)
        
        # Store heuristic info for reporting
        if hallelujah_changed:
            self._heuristic_replacements.append({
                'verse_ref': verse_ref or 'unknown',
                'type': 'hallelujah_heuristic'
            })
        
        # Store ambiguous Lord info for reporting
        if ambiguous_lords:
            self._ambiguous_lords.extend(ambiguous_lords)
        
        # Apply default mappings
        result = NameRules.apply_all(result, strict_mode=strict_mode)
        
        # In strict mode, "Lord" (not all caps) is left unchanged unless override exists
        # This is handled in apply_lord_mapping, so no additional validation needed here
        
        return result
    
    def convert_verse(
        self,
        text: str,
        book: str,
        chapter: int,
        verse: int,
        strict: Optional[bool] = None
    ) -> str:
        """
        Convert a specific verse with verse-aware mode enabled.
        
        Args:
            text: Verse text
            book: Book name
            chapter: Chapter number
            verse: Verse number
            strict: Override config strict_mode (if provided)
        
        Returns:
            Converted text
        """
        verse_ref = self.get_verse_key(book, chapter, verse)
        return self.convert_text(text, verse_ref=verse_ref, strict=strict)
    
    def _apply_replacements(self, text: str, replacements: Dict[str, str]) -> str:
        """
        Apply multiple replacements to text.
        
        Args:
            text: Input text
            replacements: Dictionary of {original: replacement}
        
        Returns:
            Text with replacements applied
        """
        result = text
        
        # Handle old format: full text replacement
        if '__full_text__' in replacements:
            return replacements['__full_text__']
        
        # Apply each replacement (use word boundaries for whole-word matching)
        for original, replacement in replacements.items():
            # Escape special regex characters in original
            escaped_original = re.escape(original)
            # Use word boundaries for whole-word matching
            pattern = r'\b' + escaped_original + r'\b'
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def batch_convert(
        self,
        verses: List[Dict[str, any]],
        strict: Optional[bool] = None
    ) -> List[Dict[str, any]]:
        """
        Convert multiple verses.
        
        Args:
            verses: List of dicts with keys: 'text', 'book', 'chapter', 'verse'
            strict: Override config strict_mode (if provided)
        
        Returns:
            List of converted verses with 'original' and 'converted' keys
        """
        # Reset tracking
        self._applied_overrides = []
        self._heuristic_replacements = []
        self._ambiguous_lords = []
        
        results = []
        for verse in verses:
            original = verse.get('text', '')
            converted = self.convert_verse(
                original,
                verse['book'],
                verse['chapter'],
                verse['verse'],
                strict=strict
            )
            results.append({
                'book': verse['book'],
                'chapter': verse['chapter'],
                'verse': verse['verse'],
                'original': original,
                'converted': converted
            })
        return results
    
    def get_applied_overrides(self) -> List[Dict]:
        """Get list of applied overrides for reporting."""
        return getattr(self, '_applied_overrides', [])
    
    def get_heuristic_replacements(self) -> List[Dict]:
        """Get list of heuristic replacements for reporting."""
        return getattr(self, '_heuristic_replacements', [])
    
    def get_ambiguous_lords(self) -> List[Dict]:
        """Get list of ambiguous Lord occurrences for reporting."""
        return getattr(self, '_ambiguous_lords', [])

