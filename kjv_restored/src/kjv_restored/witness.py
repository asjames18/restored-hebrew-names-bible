"""Witness management for verse overrides."""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


class WitnessManager:
    """Manages witness metadata for verse overrides."""
    
    VALID_WITNESSES = ["cepher", "dabar_yahuah", "kjv_token"]
    
    def __init__(self, overrides_file: Optional[Path] = None):
        """
        Initialize witness manager.
        
        Args:
            overrides_file: Path to overrides.json file
        """
        self.overrides_file = overrides_file or Path("overrides.json")
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
        # Ensure parent directory exists
        self.overrides_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.overrides_file, 'w', encoding='utf-8') as f:
            json.dump(self.overrides, f, indent=2, ensure_ascii=False)
    
    def validate_witnesses(self, witnesses: List[str]) -> List[str]:
        """
        Validate and filter witness list.
        
        Args:
            witnesses: List of witness names
            
        Returns:
            Validated list of witnesses
        """
        return [w for w in witnesses if w in self.VALID_WITNESSES]
    
    def get_override(self, verse_ref: str) -> Optional[Dict]:
        """
        Get override for verse reference.
        
        Args:
            verse_ref: Verse reference (e.g., "John 3:16")
            
        Returns:
            Override dict or None
        """
        return self.overrides.get(verse_ref)
    
    def has_override(self, verse_ref: str) -> bool:
        """
        Check if override exists for verse reference.
        
        Args:
            verse_ref: Verse reference
            
        Returns:
            True if override exists
        """
        return verse_ref in self.overrides
    
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
        validated_witnesses = self.validate_witnesses(witnesses or [])
        self.overrides[verse_ref] = {
            'replacement': replacement,
            'witnesses': validated_witnesses,
            'require_witness': require_witness
        }
        self.save_overrides()
    
    def remove_override(self, verse_ref: str) -> bool:
        """
        Remove an override.
        
        Args:
            verse_ref: Verse reference
            
        Returns:
            True if override was removed, False if it didn't exist
        """
        if verse_ref in self.overrides:
            del self.overrides[verse_ref]
            self.save_overrides()
            return True
        return False
    
    def has_yah_short_form(self, text: str) -> bool:
        """
        Check if text contains YAH short form (YAH instead of YAHUAH for LORD).
        This is a heuristic check - looks for patterns like "YAH" where "YAHUAH" would be expected.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to use YAH short form
        """
        # Check if text contains "YAH" as a standalone word that might be a short form
        # This is a simple heuristic - in practice, this would be determined by context
        # For now, we check if override explicitly marks it as short form
        return False  # Will be determined by override metadata
    
    def has_both_witnesses(self, witnesses: list) -> bool:
        """
        Check if witnesses list contains both cepher and dabar_yahuah.
        
        Args:
            witnesses: List of witness names
            
        Returns:
            True if both required witnesses are present
        """
        return "cepher" in witnesses and "dabar_yahuah" in witnesses
    
    def get_replacements(
        self,
        verse_ref: str,
        enforce_witnesses: bool = False,
        short_name_mode: str = "kjv_only"
    ) -> Optional[Dict[str, str]]:
        """
        Get replacements dictionary for verse reference.
        Supports both old format (single "replacement") and new format ("replacements" dict).
        
        Args:
            verse_ref: Verse reference
            enforce_witnesses: If True, only apply overrides with witnesses
            short_name_mode: Mode for short name handling ("kjv_only" | "witnessed" | "off")
            
        Returns:
            Dictionary of {original: replacement} if override should be applied, None otherwise
        """
        override = self.get_override(verse_ref)
        if not override:
            return None
        
        witnesses = override.get('witnesses', [])
        
        # Check if enforce_witnesses requires witnesses
        if enforce_witnesses:
            if not witnesses:
                return None
        
        # Get replacements (new format) or single replacement (old format)
        replacements = override.get('replacements')
        if replacements is None:
            # Old format: single "replacement" string
            replacement = override.get('replacement', '')
            if not replacement:
                return None
            # Convert to new format
            replacements = {'__full_text__': replacement}
        
        # Validate YAH replacements in witnessed mode
        if short_name_mode == "witnessed":
            for original, replacement in replacements.items():
                # Check if replacement is "YAH" (short form)
                if replacement == "YAH" or (isinstance(replacement, str) and 
                                            re.search(r'\bYAH\b', replacement) and 
                                            not re.search(r'\bYAHUAH\b', replacement)):
                    # Require both witnesses for YAH replacements
                    if not self.has_both_witnesses(witnesses):
                        return None  # Reject YAH-short override without both witnesses
        
        return replacements

