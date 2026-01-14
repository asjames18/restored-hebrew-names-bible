"""Configuration management for KJV Restored Names Converter."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration settings for the converter."""
    
    overrides_file: Path = Path("overrides.json")
    strict_mode: bool = False
    enforce_witnesses: bool = False
    verse_aware: bool = True
    short_name_mode: str = "kjv_only"  # "kjv_only" | "witnessed" | "off"
    hallelujah_heuristic: bool = False
    
    @classmethod
    def from_args(
        cls,
        overrides_file: Optional[str] = None,
        strict: bool = False,
        enforce_witnesses: bool = False,
        verse_aware: bool = True,
        short_name_mode: str = "kjv_only",
        hallelujah_heuristic: bool = False
    ) -> "Config":
        """Create config from command-line arguments."""
        return cls(
            overrides_file=Path(overrides_file) if overrides_file else Path("overrides.json"),
            strict_mode=strict,
            enforce_witnesses=enforce_witnesses,
            verse_aware=verse_aware,
            short_name_mode=short_name_mode,
            hallelujah_heuristic=hallelujah_heuristic
        )

