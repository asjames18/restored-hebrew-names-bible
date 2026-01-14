"""Tests for name mapping rules."""

import pytest
from kjv_restored.rules import NameRules


class TestNameRules:
    """Test cases for NameRules."""
    
    def test_lord_to_yahuah(self):
        """Test LORD -> YAHUAH conversion."""
        text = "The LORD is my shepherd."
        result = NameRules.apply_all(text)
        assert "YAHUAH" in result
        assert "LORD" not in result
    
    def test_god_to_yahuah(self):
        """Test God -> YAHUAH conversion."""
        text = "For God so loved the world."
        result = NameRules.apply_all(text)
        assert "YAHUAH" in result
        assert "God" not in result
    
    def test_jesus_to_yahusha(self):
        """Test Jesus -> YAHUSHA conversion."""
        text = "Jesus said unto them."
        result = NameRules.apply_all(text)
        assert "YAHUSHA" in result
        assert "Jesus" not in result
    
    def test_christ_to_hamashiach(self):
        """Test Christ -> HA'MASHIACH conversion."""
        text = "Jesus Christ is Lord."
        result = NameRules.apply_all(text)
        assert "HA'MASHIACH" in result
        assert "Christ" not in result
    
    def test_messiah_to_hamashiach(self):
        """Test Messiah -> HA'MASHIACH conversion."""
        text = "He is the Messiah."
        result = NameRules.apply_all(text)
        assert "HA'MASHIACH" in result
        assert "Messiah" not in result
    
    def test_holy_spirit_to_ruach_haqodesh(self):
        """Test Holy Spirit -> RUACH HAQODESH conversion."""
        text = "The Holy Spirit guides us."
        result = NameRules.apply_all(text)
        assert "RUACH HAQODESH" in result
        assert "Holy Spirit" not in result
    
    def test_holy_ghost_to_ruach_haqodesh(self):
        """Test Holy Ghost -> RUACH HAQODESH conversion."""
        text = "The Holy Ghost will teach you."
        result = NameRules.apply_all(text)
        assert "RUACH HAQODESH" in result
        assert "Holy Ghost" not in result
    
    def test_jesus_christ_compound(self):
        """Test Jesus Christ -> YAHUSHA HA'MASHIACH."""
        text = "Jesus Christ is the Son of God."
        result = NameRules.apply_all(text)
        assert "YAHUSHA HA'MASHIACH" in result
    
    def test_christ_jesus_compound(self):
        """Test Christ Jesus -> HA'MASHIACH YAHUSHA."""
        text = "In Christ Jesus we have redemption."
        result = NameRules.apply_all(text)
        assert "HA'MASHIACH YAHUSHA" in result
    
    def test_hallelujah_to_halleluyah(self):
        """Test Hallelujah -> HalleluYAH."""
        text = "Hallelujah! Praise the Lord!"
        result = NameRules.apply_all(text)
        assert "HalleluYAH" in result
        assert "Hallelujah" not in result
    
    def test_case_insensitive(self):
        """Test that conversions are case-insensitive."""
        text = "JESUS christ LORD god"
        result = NameRules.apply_all(text)
        assert "YAHUSHA" in result
        assert "HA'MASHIACH" in result
        assert "YAHUAH" in result
    
    def test_multiple_occurrences(self):
        """Test multiple occurrences in same text."""
        text = "God is good. God is great. God is YAHUAH."
        result = NameRules.apply_all(text)
        # Should convert all instances
        assert result.count("YAHUAH") >= 3
    
    def test_no_changes_when_no_matches(self):
        """Test that text without matches is unchanged."""
        text = "This is a normal sentence with no special names."
        result = NameRules.apply_all(text)
        assert result == text

