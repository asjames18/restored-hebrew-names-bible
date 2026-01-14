"""Tests for converter module."""

import pytest
from pathlib import Path
import tempfile
import json

from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config
from kjv_restored.witness import WitnessManager


class TestRestoredNamesConverter:
    """Test cases for RestoredNamesConverter."""
    
    def test_basic_conversion(self):
        """Test basic text conversion."""
        converter = RestoredNamesConverter()
        text = "For God so loved the world."
        result = converter.convert_text(text)
        assert "YAHUAH" in result
        assert "God" not in result
    
    def test_parse_verse_reference(self):
        """Test verse reference parsing."""
        converter = RestoredNamesConverter()
        
        # Test simple reference
        ref = converter.parse_verse_reference("John 3:16 For God so loved...")
        assert ref == ("John", 3, 16)
        
        # Test numbered book
        ref = converter.parse_verse_reference("1 John 3:16 Some text")
        assert ref == ("1 John", 3, 16)
        
        # Test Genesis
        ref = converter.parse_verse_reference("Genesis 1:1 In the beginning")
        assert ref == ("Genesis", 1, 1)
        
        # Test no reference
        ref = converter.parse_verse_reference("Just some text")
        assert ref is None
    
    def test_get_verse_key(self):
        """Test verse key generation."""
        converter = RestoredNamesConverter()
        key = converter.get_verse_key("John", 3, 16)
        assert key == "John 3:16"
    
    def test_convert_verse(self):
        """Test verse-specific conversion."""
        converter = RestoredNamesConverter()
        text = "For God so loved the world."
        result = converter.convert_verse(text, "John", 3, 16)
        assert "YAHUAH" in result
    
    def test_convert_with_override(self):
        """Test conversion with verse override."""
        # Create temporary overrides file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "For YAHUAH so loved the world (OVERRIDE).",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            text = "For God so loved the world."
            result = converter.convert_verse(text, "John", 3, 16)
            
            # Should use override
            assert "OVERRIDE" in result
        finally:
            overrides_path.unlink()
    
    def test_convert_without_override(self):
        """Test conversion without override uses default rules."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {}
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=True)
            converter = RestoredNamesConverter(config=config)
            
            text = "For God so loved the world."
            result = converter.convert_verse(text, "John", 3, 16)
            
            # Should use default rules
            assert "YAHUAH" in result
            assert "God" not in result
        finally:
            overrides_path.unlink()
    
    def test_enforce_witnesses(self):
        """Test witness enforcement."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "OVERRIDE WITH WITNESS",
                    "witnesses": ["cepher"],
                    "require_witness": False
                },
                "John 1:1": {
                    "replacement": "OVERRIDE WITHOUT WITNESS",
                    "witnesses": [],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            # Test with enforce_witnesses=True
            config = Config(
                overrides_file=overrides_path,
                verse_aware=True,
                enforce_witnesses=True
            )
            converter = RestoredNamesConverter(config=config)
            
            # Should apply override with witness
            result1 = converter.convert_verse("test", "John", 3, 16)
            assert "OVERRIDE WITH WITNESS" in result1
            
            # Should NOT apply override without witness
            result2 = converter.convert_verse("test", "John", 1, 1)
            assert "OVERRIDE WITHOUT WITNESS" not in result2
        finally:
            overrides_path.unlink()
    
    def test_batch_convert(self):
        """Test batch conversion of multiple verses."""
        converter = RestoredNamesConverter()
        
        verses = [
            {
                'text': 'For God so loved the world.',
                'book': 'John',
                'chapter': 3,
                'verse': 16
            },
            {
                'text': 'Jesus Christ is Lord.',
                'book': 'John',
                'chapter': 1,
                'verse': 1
            }
        ]
        
        results = converter.batch_convert(verses)
        
        assert len(results) == 2
        assert results[0]['book'] == 'John'
        assert results[0]['chapter'] == 3
        assert results[0]['verse'] == 16
        assert "YAHUAH" in results[0]['converted']
        assert "YAHUSHA HA'MASHIACH" in results[1]['converted']
    
    def test_verse_aware_disabled(self):
        """Test that verse-aware mode can be disabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "OVERRIDE TEXT",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            config = Config(overrides_file=overrides_path, verse_aware=False)
            converter = RestoredNamesConverter(config=config)
            
            # Should not use override when verse_aware is False
            text = "For God so loved the world."
            result = converter.convert_verse(text, "John", 3, 16)
            
            assert "OVERRIDE TEXT" not in result
            assert "YAHUAH" in result  # Should use default rules
        finally:
            overrides_path.unlink()

