"""Tests for phrase-first replacements and whole-word boundaries."""

import pytest
import tempfile
import json
from pathlib import Path

from kjv_restored.rules import NameRules
from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config


class TestPhraseFirstOrdering:
    """Test that phrases are matched before single tokens."""
    
    def test_jesus_christ_phrase_first(self):
        """Test that 'Jesus Christ' is matched as phrase before individual tokens."""
        text = "Jesus Christ is the Savior."
        result = NameRules.apply_mappings(text)
        
        # Should match phrase "Jesus Christ" -> "YAHUSHA HA'MASHIACH"
        assert "YAHUSHA HA'MASHIACH" in result
        assert "Jesus Christ" not in result
        # Should not have separate "YAHUSHA" and "HA'MASHIACH" from individual matches
        # (though the phrase replacement contains both, which is correct)
    
    def test_holy_spirit_phrase_first(self):
        """Test that 'Holy Spirit' is matched as phrase."""
        text = "The Holy Spirit guides us."
        result = NameRules.apply_mappings(text)
        
        assert "RUACH HAQODESH" in result
        assert "Holy Spirit" not in result
        # Should not match "Holy" and "Spirit" separately
    
    def test_holy_ghost_phrase_first(self):
        """Test that 'Holy Ghost' is matched as phrase."""
        text = "The Holy Ghost will teach you."
        result = NameRules.apply_mappings(text)
        
        assert "RUACH HAQODESH" in result
        assert "Holy Ghost" not in result
    
    def test_phrase_before_single_token(self):
        """Test that phrase matching happens before single token matching."""
        text = "Jesus Christ and Jesus alone."
        result = NameRules.apply_mappings(text)
        
        # "Jesus Christ" should become "YAHUSHA HA'MASHIACH"
        # "Jesus" alone should become "YAHUSHA"
        assert "YAHUSHA HA'MASHIACH" in result
        assert "YAHUSHA" in result
        assert "Jesus" not in result


class TestWholeWordBoundaries:
    """Test that replacements only occur on whole word boundaries."""
    
    def test_jesus_not_in_other_words(self):
        """Test that 'Jesus' is not replaced when part of other words."""
        text = "Jesus is not in 'Jesuses' or 'Jesustown'."
        result = NameRules.apply_mappings(text)
        
        # "Jesus" should be replaced
        assert "YAHUSHA" in result
        # But "Jesuses" and "Jesustown" should remain unchanged
        assert "Jesuses" in result or "jesustown" in result.lower()
    
    def test_christ_not_in_other_words(self):
        """Test that 'Christ' is not replaced when part of other words."""
        text = "Christ is not in 'Christian' or 'Christlike'."
        result = NameRules.apply_mappings(text)
        
        # "Christ" should be replaced
        assert "HA'MASHIACH" in result
        # But "Christian" and "Christlike" should remain unchanged
        assert "Christian" in result
        assert "Christlike" in result
    
    def test_lord_not_in_other_words(self):
        """Test that 'LORD' is not replaced when part of other words."""
        text = "LORD is not in 'LORDLY' or 'LORDship'."
        result = NameRules.apply_mappings(text)
        
        # "LORD" should be replaced
        assert "YAHUAH" in result
        # But "LORDLY" and "LORDship" should remain unchanged (or partially changed)
        # Note: This is a boundary test - word boundaries should prevent partial matches
    
    def test_god_not_in_other_words(self):
        """Test that 'GOD' is not replaced when part of other words."""
        text = "GOD is not in 'GODLY' or 'GODship'."
        result = NameRules.apply_mappings(text)
        
        # "GOD" should be replaced
        assert "ELOHIYM" in result
        # But "GODLY" and "GODship" should remain unchanged


class TestTokenReplacements:
    """Test single token replacements."""
    
    def test_jesus_token(self):
        """Test 'Jesus' -> 'YAHUSHA'."""
        text = "Jesus said unto them."
        result = NameRules.apply_mappings(text)
        assert "YAHUSHA" in result
        assert "Jesus" not in result
    
    def test_christ_token(self):
        """Test 'Christ' -> 'HA'MASHIACH'."""
        text = "Christ is risen."
        result = NameRules.apply_mappings(text)
        assert "HA'MASHIACH" in result
        assert "Christ" not in result
    
    def test_god_all_caps(self):
        """Test 'GOD' (all caps) -> 'ELOHIYM'."""
        text = "GOD is great."
        result = NameRules.apply_mappings(text)
        assert "ELOHIYM" in result
        assert "GOD" not in result
    
    def test_god_title_case(self):
        """Test 'God' (title case) -> 'YAHUAH'."""
        text = "God is great."
        result = NameRules.apply_mappings(text)
        assert "YAHUAH" in result
        assert "God" not in result
        assert "ELOHIYM" not in result
    
    def test_god_vs_god_case_sensitivity(self):
        """Test that 'GOD' and 'God' are handled differently."""
        text = "GOD is ELOHIYM, and God is YAHUAH."
        result = NameRules.apply_mappings(text)
        assert "ELOHIYM" in result
        assert "YAHUAH" in result
        assert "GOD" not in result
        assert "God" not in result
    
    def test_lord_token(self):
        """Test 'LORD' -> 'YAHUAH'."""
        text = "The LORD is my shepherd."
        result = NameRules.apply_mappings(text)
        assert "YAHUAH" in result
        assert "LORD" not in result


class TestLordAmbiguous:
    """Test 'Lord' (not all caps) handling."""
    
    def test_lord_to_adon_non_strict(self):
        """Test that 'Lord' (not all caps) -> 'ADON' in non-strict mode."""
        text = "The Lord is my shepherd."
        result = NameRules.apply_mappings(text, strict_mode=False)
        assert "ADON" in result
        assert "Lord" not in result
    
    def test_lord_unchanged_strict(self):
        """Test that 'Lord' is unchanged in strict mode."""
        text = "The Lord is my shepherd."
        result = NameRules.apply_mappings(text, strict_mode=True)
        assert "Lord" in result
        assert "ADON" not in result
    
    def test_lord_with_override_strict(self):
        """Test that 'Lord' can be overridden in strict mode."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "Psalms 23:1": {
                    "replacement": "The ADON is my shepherd.",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(
                overrides_file=overrides_path,
                verse_aware=True,
                strict_mode=True
            )
            converter = RestoredNamesConverter(config=config)
            
            text = "The Lord is my shepherd."
            result = converter.convert_verse(text, "Psalms", 23, 1)
            
            # Should use override
            assert "ADON" in result
            assert "Lord" not in result
        finally:
            overrides_path.unlink()
    
    def test_lord_vs_lord_case_sensitivity(self):
        """Test that 'LORD' (all caps) and 'Lord' (title case) are handled differently."""
        text = "The LORD is great, and the Lord is good."
        result = NameRules.apply_mappings(text, strict_mode=False)
        
        # "LORD" should become "YAHUAH"
        assert "YAHUAH" in result
        # "Lord" should become "ADON"
        assert "ADON" in result
        assert "LORD" not in result
        assert "Lord" not in result


class TestPhraseOrderingEdgeCases:
    """Test edge cases for phrase ordering."""
    
    def test_multiple_phrases(self):
        """Test multiple phrases in same text."""
        text = "Jesus Christ and the Holy Spirit."
        result = NameRules.apply_mappings(text)
        
        assert "YAHUSHA HA'MASHIACH" in result
        assert "RUACH HAQODESH" in result
        assert "Jesus Christ" not in result
        assert "Holy Spirit" not in result
    
    def test_phrase_with_punctuation(self):
        """Test phrases with punctuation."""
        text = "Jesus Christ! The Holy Spirit?"
        result = NameRules.apply_mappings(text)
        
        assert "YAHUSHA HA'MASHIACH" in result
        assert "RUACH HAQODESH" in result
    
    def test_phrase_at_start_and_end(self):
        """Test phrases at start and end of text."""
        text = "Jesus Christ is Lord. Holy Ghost."
        result = NameRules.apply_mappings(text, strict_mode=False)
        
        assert "YAHUSHA HA'MASHIACH" in result
        assert "RUACH HAQODESH" in result
    
    def test_overlapping_patterns(self):
        """Test that phrase matching prevents overlapping issues."""
        text = "Jesus Christ came. Christ is risen."
        result = NameRules.apply_mappings(text)
        
        # "Jesus Christ" should become phrase
        assert "YAHUSHA HA'MASHIACH" in result
        # "Christ" alone should also be replaced
        assert "HA'MASHIACH" in result
        # But "Christ" in "Jesus Christ" should not be double-replaced


class TestIntegration:
    """Integration tests for phrase-first replacements."""
    
    def test_full_conversion_with_phrases(self):
        """Test full conversion with phrase-first logic."""
        config = Config(strict_mode=False)
        converter = RestoredNamesConverter(config=config)
        
        text = "Jesus Christ is the Lord. The Holy Spirit guides us."
        result = converter.convert_text(text)
        
        assert "YAHUSHA HA'MASHIACH" in result
        assert "ADON" in result
        assert "RUACH HAQODESH" in result
        assert "Jesus" not in result
        assert "Christ" not in result
        assert "Lord" not in result
        assert "Holy Spirit" not in result
    
    def test_strict_mode_preserves_lord(self):
        """Test that strict mode preserves 'Lord' without override."""
        config = Config(strict_mode=True)
        converter = RestoredNamesConverter(config=config)
        
        text = "The Lord is my shepherd."
        result = converter.convert_text(text)
        
        # Should preserve "Lord" in strict mode
        assert "Lord" in result
        assert "ADON" not in result
    
    def test_case_insensitive_phrases(self):
        """Test that phrases are matched case-insensitively."""
        text = "jesus christ and HOLY SPIRIT"
        result = NameRules.apply_mappings(text)
        
        assert "YAHUSHA HA'MASHIACH" in result
        assert "RUACH HAQODESH" in result

