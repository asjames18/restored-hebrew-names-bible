"""Tests for short name support."""

import pytest
import tempfile
import json
from pathlib import Path

from kjv_restored.rules import NameRules
from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config
from kjv_restored.witness import WitnessManager


class TestJAHConversion:
    """Test JAH -> YAH conversion."""
    
    def test_jah_to_yah_uppercase(self):
        """Test JAH -> YAH conversion (uppercase)."""
        text = "Sing unto JAH, sing praises to JAH."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is True
        assert "YAH" in result
        assert "JAH" not in result
        assert result == "Sing unto YAH, sing praises to YAH."
    
    def test_jah_to_yah_lowercase(self):
        """Test jah -> yah conversion (lowercase)."""
        text = "Sing unto jah, sing praises to jah."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is True
        assert "yah" in result
        assert "jah" not in result
        assert result == "Sing unto yah, sing praises to yah."
    
    def test_jah_to_yah_title_case(self):
        """Test Jah -> Yah conversion (title case)."""
        text = "Sing unto Jah, sing praises to Jah."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is True
        assert "Yah" in result
        assert "Jah" not in result
        assert result == "Sing unto Yah, sing praises to Yah."
    
    def test_jah_preserves_punctuation(self):
        """Test that JAH conversion preserves punctuation."""
        text = "JAH! JAH? JAH, JAH."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is True
        assert result == "YAH! YAH? YAH, YAH."
    
    def test_jah_not_in_other_words(self):
        """Test that JAH is not converted when part of other words."""
        text = "Hallelujah is a word. JAH is separate."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is True
        assert "Hallelujah" in result  # Should remain unchanged
        assert "YAH" in result  # JAH should be converted
        assert "JAH" not in result
    
    def test_no_jah_no_change(self):
        """Test that text without JAH is unchanged."""
        text = "This text has no JAH token."
        result, changed = NameRules.convert_jah_to_yah(text)
        assert changed is False
        assert result == text


class TestHallelujahHeuristic:
    """Test Hallelujah heuristic."""
    
    def test_hallelujah_heuristic_with_period(self):
        """Test Hallelujah heuristic: 'Praise ye the LORD.' -> 'Hallelu-YAH.'"""
        text = "Praise ye the LORD."
        result, changed = NameRules.apply_hallelujah_heuristic(text)
        assert changed is True
        assert result == "Hallelu-YAH."
        assert "Praise ye the LORD" not in result
    
    def test_hallelujah_heuristic_without_period(self):
        """Test Hallelujah heuristic: 'Praise ye the LORD' -> 'Hallelu-YAH'"""
        text = "Praise ye the LORD"
        result, changed = NameRules.apply_hallelujah_heuristic(text)
        assert changed is True
        assert result == "Hallelu-YAH"
    
    def test_hallelujah_heuristic_in_sentence(self):
        """Test Hallelujah heuristic within a sentence."""
        text = "The people said, Praise ye the LORD. And they rejoiced."
        result, changed = NameRules.apply_hallelujah_heuristic(text)
        assert changed is True
        assert "Hallelu-YAH." in result
        assert "Praise ye the LORD" not in result
    
    def test_hallelujah_heuristic_no_match(self):
        """Test that non-matching text is unchanged."""
        text = "Praise the LORD, all ye people."
        result, changed = NameRules.apply_hallelujah_heuristic(text)
        assert changed is False
        assert result == text
    
    def test_hallelujah_heuristic_disabled(self):
        """Test that heuristic is not applied when disabled."""
        config = Config(hallelujah_heuristic=False)
        converter = RestoredNamesConverter(config=config)
        text = "Praise ye the LORD."
        result = converter.convert_text(text)
        # Should convert LORD to YAHUAH but not apply heuristic
        assert "YAHUAH" in result
        assert "Hallelu-YAH" not in result


class TestWitnessedMode:
    """Test witnessed mode for YAH short form."""
    
    def test_witnessed_mode_rejects_yah_without_both_witnesses(self):
        """Test that witnessed mode rejects YAH-short override without both witnesses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalms 68:4": {
                    "replacement": "Sing unto YAH, sing praises to YAH. [OVERRIDE]",
                    "witnesses": ["cepher"],  # Only one witness
                    "require_witness": False
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
            
            # Should NOT use override because it has YAH short form but only one witness
            text = "Sing unto JAH, sing praises to JAH."
            result = converter.convert_verse(text, "Psalms", 68, 4)
            
            # Should use default rules (JAH -> YAH), not the override
            assert "YAH" in result
            assert "[OVERRIDE]" not in result  # Override was rejected
        finally:
            overrides_path.unlink()
    
    def test_witnessed_mode_accepts_yah_with_both_witnesses(self):
        """Test that witnessed mode accepts YAH-short override with both witnesses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalms 68:4": {
                    "replacement": "Sing unto YAH, sing praises to YAH.",
                    "witnesses": ["cepher", "dabar_yahuah"],  # Both witnesses
                    "require_witness": False
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
            
            # Should use override because it has both witnesses
            text = "Sing unto JAH, sing praises to JAH."
            result = converter.convert_verse(text, "Psalms", 68, 4)
            
            # Should use the override
            assert result == "Sing unto YAH, sing praises to YAH."
        finally:
            overrides_path.unlink()
    
    def test_witnessed_mode_accepts_yahuah_override(self):
        """Test that witnessed mode accepts YAHUAH (not short form) override with one witness."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalms 68:4": {
                    "replacement": "Sing unto YAHUAH, sing praises to YAHUAH.",
                    "witnesses": ["cepher"],  # Only one witness, but YAHUAH not YAH
                    "require_witness": False
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
            
            # Should use override because it's YAHUAH, not YAH short form
            text = "Sing unto JAH, sing praises to JAH."
            result = converter.convert_verse(text, "Psalms", 68, 4)
            
            # Should use the override (YAHUAH, not YAH)
            assert result == "Sing unto YAHUAH, sing praises to YAHUAH."
        finally:
            overrides_path.unlink()
    
    def test_kjv_only_mode_allows_jah_conversion(self):
        """Test that kjv_only mode allows JAH -> YAH conversion."""
        config = Config(short_name_mode="kjv_only")
        converter = RestoredNamesConverter(config=config)
        
        text = "Sing unto JAH, sing praises to JAH."
        result = converter.convert_text(text)
        
        # Should convert JAH to YAH
        assert "YAH" in result
        assert "JAH" not in result
    
    def test_off_mode_disables_jah_conversion(self):
        """Test that off mode disables JAH -> YAH conversion."""
        config = Config(short_name_mode="off")
        converter = RestoredNamesConverter(config=config)
        
        text = "Sing unto JAH, sing praises to JAH."
        result = converter.convert_text(text)
        
        # Should NOT convert JAH to YAH
        assert "JAH" in result
        # But other conversions should still work
        assert "YAHUAH" in result or "YAH" in result  # From other conversions


class TestShortNameIntegration:
    """Integration tests for short name features."""
    
    def test_jah_conversion_with_other_conversions(self):
        """Test JAH conversion works with other name conversions."""
        config = Config(short_name_mode="kjv_only")
        converter = RestoredNamesConverter(config=config)
        
        text = "Sing unto JAH, sing praises to JAH. For God so loved the world."
        result = converter.convert_text(text)
        
        assert "YAH" in result  # From JAH conversion
        assert "YAHUAH" in result  # From God conversion
        assert "JAH" not in result
        assert "God" not in result
    
    def test_hallelujah_heuristic_integration(self):
        """Test Hallelujah heuristic integration."""
        config = Config(hallelujah_heuristic=True)
        converter = RestoredNamesConverter(config=config)
        
        text = "Praise ye the LORD."
        result = converter.convert_text(text)
        
        # Should apply heuristic
        assert "Hallelu-YAH" in result or "Hallelu-YAH." in result
    
    def test_witnessed_mode_with_enforce_witnesses(self):
        """Test witnessed mode combined with enforce_witnesses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalms 68:4": {
                    "replacement": "Sing unto YAH, sing praises to YAH.",
                    "witnesses": ["cepher", "dabar_yahuah"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(
                overrides_file=overrides_path,
                verse_aware=True,
                short_name_mode="witnessed",
                enforce_witnesses=True
            )
            converter = RestoredNamesConverter(config=config)
            
            # Should use override because it has both witnesses
            text = "Sing unto JAH, sing praises to JAH."
            result = converter.convert_verse(text, "Psalms", 68, 4)
            
            assert result == "Sing unto YAH, sing praises to YAH."
        finally:
            overrides_path.unlink()

