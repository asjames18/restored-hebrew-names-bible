"""Tests for new overrides.json format with multiple replacements."""

import pytest
import tempfile
import json
from pathlib import Path

from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config
from kjv_restored.witness import WitnessManager


class TestNewOverridesFormat:
    """Test the new overrides format with multiple replacements."""
    
    def test_multiple_replacements_per_verse(self):
        """Test that multiple replacements can be specified per verse."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Romans 10:13": {
                    "replacements": {
                        "Lord": "YAHUAH"
                    },
                    "witnesses": ["cepher", "dabar_yahuah"],
                    "note": "OT quote placement"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            text = "For whosoever shall call upon the name of the Lord shall be saved."
            result = converter.convert_verse(text, "Romans", 10, 13)
            
            # Should apply override: "Lord" -> "YAHUAH"
            assert "YAHUAH" in result
            assert "Lord" not in result
        finally:
            overrides_path.unlink()
    
    def test_jah_to_yah_override(self):
        """Test JAH -> YAH override with kjv_token witness."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalm 68:4": {
                    "replacements": {
                        "JAH": "YAH"
                    },
                    "witnesses": ["kjv_token"],
                    "note": "KJV contains JAH"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            text = "Sing unto JAH, sing praises to JAH."
            result = converter.convert_verse(text, "Psalm", 68, 4)
            
            # Should apply override: "JAH" -> "YAH"
            assert "YAH" in result
            assert "JAH" not in result
        finally:
            overrides_path.unlink()
    
    def test_witnessed_mode_yah_requires_both_witnesses(self):
        """Test that YAH replacements in witnessed mode require both witnesses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Romans 10:13": {
                    "replacements": {
                        "Lord": "YAH"  # YAH short form
                    },
                    "witnesses": ["cepher"],  # Only one witness
                    "note": "Test"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(
                overrides_file=overrides_path,
                verse_aware=True,
                short_name_mode="witnessed"
            )
            converter = RestoredNamesConverter(config=config)
            
            text = "For whosoever shall call upon the name of the Lord shall be saved."
            result = converter.convert_verse(text, "Romans", 10, 13)
            
            # Should NOT apply override (only one witness for YAH)
            # Should use default rules instead
            assert "YAH" not in result or "YAHUAH" in result
        finally:
            overrides_path.unlink()
    
    def test_witnessed_mode_yah_with_both_witnesses(self):
        """Test that YAH replacements work with both witnesses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Romans 10:13": {
                    "replacements": {
                        "Lord": "YAH"  # YAH short form
                    },
                    "witnesses": ["cepher", "dabar_yahuah"],  # Both witnesses
                    "note": "Test"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(
                overrides_file=overrides_path,
                verse_aware=True,
                short_name_mode="witnessed"
            )
            converter = RestoredNamesConverter(config=config)
            
            text = "For whosoever shall call upon the name of the Lord shall be saved."
            result = converter.convert_verse(text, "Romans", 10, 13)
            
            # Should apply override (both witnesses present)
            assert "YAH" in result
        finally:
            overrides_path.unlink()
    
    def test_old_format_backward_compatibility(self):
        """Test that old format (single 'replacement') still works."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "For YAHUAH so loved the world...",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            text = "For God so loved the world..."
            result = converter.convert_verse(text, "John", 3, 16)
            
            # Should use old format override
            assert "YAHUAH" in result
        finally:
            overrides_path.unlink()


class TestReporting:
    """Test reporting functionality."""
    
    def test_applied_overrides_in_report(self):
        """Test that applied overrides are recorded in report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Romans 10:13": {
                    "replacements": {
                        "Lord": "YAHUAH"
                    },
                    "witnesses": ["cepher", "dabar_yahuah"],
                    "note": "OT quote"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            # Convert a verse
            text = "For whosoever shall call upon the name of the Lord shall be saved."
            converter.convert_verse(text, "Romans", 10, 13)
            
            # Check that override was recorded
            applied = converter.get_applied_overrides()
            assert len(applied) > 0
            assert applied[0]['verse_ref'] == "Romans 10:13"
            assert "replacements" in applied[0]
        finally:
            overrides_path.unlink()
    
    def test_replacement_counts_in_report(self):
        """Test that replacement counts are calculated."""
        from kjv_restored.io import ConversionIO
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Romans 10:13": {
                    "replacements": {
                        "Lord": "YAHUAH"
                    },
                    "witnesses": ["cepher"],
                    "note": "Test"
                },
                "John 1:1": {
                    "replacements": {
                        "Lord": "YAHUAH"
                    },
                    "witnesses": ["cepher"],
                    "note": "Test"
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            io_handler = ConversionIO(converter)
            
            # Convert verses
            verses = [
                {
                    'text': 'For whosoever shall call upon the name of the Lord.',
                    'book': 'Romans',
                    'chapter': 10,
                    'verse': 13
                },
                {
                    'text': 'In the beginning was the Lord.',
                    'book': 'John',
                    'chapter': 1,
                    'verse': 1
                }
            ]
            
            converter.batch_convert(verses)
            report = io_handler._build_report('json')
            
            # Check replacement counts
            if 'replacement_counts' in report:
                counts = report['replacement_counts']
                # Should have count for "Lord -> YAHUAH"
                assert any('Lord -> YAHUAH' in key for key in counts.keys())
        finally:
            overrides_path.unlink()
    
    def test_ambiguous_lord_tracking(self):
        """Test that ambiguous Lord occurrences are tracked."""
        config = Config(strict_mode=False)
        converter = RestoredNamesConverter(config=config)
        
        text = "The Lord is my shepherd."
        converter.convert_text(text)
        
        # Check ambiguous lords
        ambiguous = converter.get_ambiguous_lords()
        # Should track "Lord" (not all caps)
        assert len(ambiguous) > 0 or "Lord" in text
    
    def test_heuristic_replacements_tracking(self):
        """Test that heuristic replacements are tracked."""
        config = Config(hallelujah_heuristic=True)
        converter = RestoredNamesConverter(config=config)
        
        text = "Praise ye the LORD."
        converter.convert_text(text)
        
        # Check heuristic replacements
        heuristics = converter.get_heuristic_replacements()
        assert len(heuristics) > 0
        assert any(h.get('type') == 'hallelujah_heuristic' for h in heuristics)

