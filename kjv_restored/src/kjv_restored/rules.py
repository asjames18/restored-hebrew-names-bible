"""Name mapping rules for KJV to restored Hebrew names."""

import re
from typing import List, Tuple, Dict


class NameRules:
    """Defines the rules for converting KJV names to restored Hebrew names."""
    
    # Phrase mappings (applied first, whole word/phrase only)
    PHRASE_MAPPINGS: List[Tuple[str, str]] = [
        (r'\bJesus\s+Christ\b', "YAHUSHA HA'MASHIACH"),
        (r'\bHoly\s+Ghost\b', 'RUACH HAQODESH'),
        (r'\bHoly\s+Spirit\b', 'RUACH HAQODESH'),
    ]
    
    # Single token mappings (applied after phrases, whole word only)
    TOKEN_MAPPINGS: List[Tuple[str, str]] = [
        (r'\bJesus\b', 'YAHUSHA'),
        (r'\bChrist\b', "HA'MASHIACH"),
        (r'\bGOD\b', 'ELOHIYM'),  # All caps GOD -> ELOHIYM
        (r'\bGod\b', 'YAHUAH'),  # Title case God -> YAHUAH (case-insensitive)
        (r'\bLORD\b', 'YAHUAH'),
        (r'\bMessiah\b', "HA'MASHIACH"),
    ]
    
    @staticmethod
    def apply_phrase_mappings(text: str) -> str:
        """
        Apply phrase mappings first (whole phrase only).
        
        Args:
            text: Input text
            
        Returns:
            Text with phrases replaced
        """
        result = text
        for pattern, replacement in NameRules.PHRASE_MAPPINGS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    @staticmethod
    def apply_token_mappings(text: str) -> str:
        """
        Apply single token mappings (whole word only).
        
        Args:
            text: Input text
            
        Returns:
            Text with tokens replaced
        """
        result = text
        for pattern, replacement in NameRules.TOKEN_MAPPINGS:
            # GOD (all caps) should be case-sensitive, others case-insensitive
            if pattern == r'\bGOD\b':
                result = re.sub(pattern, replacement, result)  # Case-sensitive
            else:
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result
    
    @staticmethod
    def apply_lord_mapping(text: str, strict_mode: bool = False) -> str:
        """
        Apply "Lord" (not all caps) mapping.
        - Non-strict: "Lord" -> "ADON"
        - Strict: Leave "Lord" unchanged (unless override exists)
        
        Args:
            text: Input text
            strict_mode: If True, leave "Lord" unchanged
            
        Returns:
            Text with "Lord" replaced (if not strict)
        """
        if strict_mode:
            return text
        
        # Match "Lord" (not all caps) as whole word
        # This matches "Lord" but not "LORD" (which is handled by token mappings)
        result = re.sub(r'\bLord\b', 'ADON', text)
        return result
    
    @staticmethod
    def apply_mappings(text: str, strict_mode: bool = False) -> str:
        """
        Apply all name mappings in correct order.
        
        Args:
            text: Input text
            strict_mode: If True, leave "Lord" unchanged
            
        Returns:
            Text with names replaced
        """
        # Apply phrases first (longer patterns)
        result = NameRules.apply_phrase_mappings(text)
        
        # Apply single tokens (shorter patterns)
        result = NameRules.apply_token_mappings(result)
        
        # Apply "Lord" mapping (ambiguous case)
        result = NameRules.apply_lord_mapping(result, strict_mode=strict_mode)
        
        return result
    
    @staticmethod
    def convert_jah_to_yah(text: str) -> Tuple[str, bool]:
        """
        Convert JAH token to YAH (KJV has it in Ps 68:4).
        Preserves casing and punctuation.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (converted_text, was_changed)
        """
        # Match JAH as a word boundary token, preserving case
        # Pattern matches: JAH, jah, Jah, etc. but not as part of other words
        original = text
        
        def replace_jah(match):
            matched = match.group(0)
            # Preserve case: if all caps, return YAH; if title case, return Yah; if lowercase, return yah
            if matched.isupper():
                return 'YAH'
            elif matched[0].isupper() and matched[1:].islower():
                return 'Yah'
            else:
                return 'yah'
        
        # Use case-insensitive flag but preserve original case via replacement function
        result = re.sub(r'\bJAH\b', replace_jah, text, flags=re.IGNORECASE)
        was_changed = result != original
        return result, was_changed
    
    @staticmethod
    def apply_hallelujah_heuristic(text: str) -> Tuple[str, bool]:
        """
        Apply Hallelujah heuristic: replace "Praise ye the LORD." with "Hallelu-YAH."
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (converted_text, was_changed)
        """
        original = text
        # Match "Praise ye the LORD." and "Praise ye the LORD" (with or without period)
        patterns = [
            (r'Praise ye the LORD\.', 'Hallelu-YAH.'),
            (r'Praise ye the LORD\b', 'Hallelu-YAH'),
        ]
        
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        was_changed = result != original
        return result, was_changed
    
    @staticmethod
    def apply_short_form(text: str) -> str:
        """
        Apply short form YAH where appropriate.
        
        Args:
            text: Input text
            
        Returns:
            Text with short forms applied
        """
        # Check for Hallelujah patterns
        text = re.sub(r'\bHallelu\s*jah\b', 'HalleluYAH', text, flags=re.IGNORECASE)
        text = re.sub(r'\bHallelu\s*YAH\b', 'HalleluYAH', text, flags=re.IGNORECASE)
        
        # In certain contexts, YAHUAH might be shortened to YAH
        # This is context-dependent and can be overridden per verse
        return text
    
    @staticmethod
    def apply_all(text: str, strict_mode: bool = False) -> str:
        """
        Apply all name mapping rules.
        
        Args:
            text: Input text
            strict_mode: If True, leave "Lord" unchanged
            
        Returns:
            Fully converted text
        """
        result = NameRules.apply_mappings(text, strict_mode=strict_mode)
        result = NameRules.apply_short_form(result)
        return result

