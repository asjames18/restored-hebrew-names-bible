"""Tests for witness management."""

import pytest
from pathlib import Path
import tempfile
import json

from kjv_restored.witness import WitnessManager


class TestWitnessManager:
    """Test cases for WitnessManager."""
    
    def test_load_overrides_nonexistent(self):
        """Test loading overrides from non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            overrides_path = Path(tmpdir) / "nonexistent.json"
            manager = WitnessManager(overrides_path)
            assert manager.overrides == {}
    
    def test_load_and_save_overrides(self):
        """Test loading and saving overrides."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "Test replacement",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            assert "John 3:16" in manager.overrides
            assert manager.overrides["John 3:16"]["replacement"] == "Test replacement"
        finally:
            overrides_path.unlink()
    
    def test_validate_witnesses(self):
        """Test witness validation."""
        manager = WitnessManager()
        
        # Valid witnesses
        valid = manager.validate_witnesses(["cepher", "dabar_yahuah"])
        assert valid == ["cepher", "dabar_yahuah"]
        
        # Invalid witnesses filtered out
        mixed = manager.validate_witnesses(["cepher", "invalid", "dabar_yahuah"])
        assert mixed == ["cepher", "dabar_yahuah"]
        assert "invalid" not in mixed
    
    def test_add_override(self):
        """Test adding an override."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            manager.add_override(
                "John 3:16",
                "Test replacement",
                witnesses=["cepher", "dabar_yahuah"],
                require_witness=True
            )
            
            assert "John 3:16" in manager.overrides
            override = manager.overrides["John 3:16"]
            assert override["replacement"] == "Test replacement"
            assert override["witnesses"] == ["cepher", "dabar_yahuah"]
            assert override["require_witness"] is True
            
            # Verify it was saved
            manager2 = WitnessManager(overrides_path)
            assert "John 3:16" in manager2.overrides
        finally:
            overrides_path.unlink()
    
    def test_get_override(self):
        """Test getting an override."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "Test",
                    "witnesses": ["cepher"],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            override = manager.get_override("John 3:16")
            assert override is not None
            assert override["replacement"] == "Test"
            
            # Non-existent override
            assert manager.get_override("John 1:1") is None
        finally:
            overrides_path.unlink()
    
    def test_has_override(self):
        """Test checking if override exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {"John 3:16": {"replacement": "Test", "witnesses": [], "require_witness": False}}
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            assert manager.has_override("John 3:16") is True
            assert manager.has_override("John 1:1") is False
        finally:
            overrides_path.unlink()
    
    def test_remove_override(self):
        """Test removing an override."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {"replacement": "Test", "witnesses": [], "require_witness": False}
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            assert manager.has_override("John 3:16") is True
            
            removed = manager.remove_override("John 3:16")
            assert removed is True
            assert manager.has_override("John 3:16") is False
            
            # Try removing non-existent
            removed2 = manager.remove_override("John 1:1")
            assert removed2 is False
        finally:
            overrides_path.unlink()
    
    def test_should_apply_override(self):
        """Test should_apply_override logic."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            overrides = {
                "John 3:16": {
                    "replacement": "With witness",
                    "witnesses": ["cepher"],
                    "require_witness": False
                },
                "John 1:1": {
                    "replacement": "Without witness",
                    "witnesses": [],
                    "require_witness": False
                }
            }
            json.dump(overrides, f)
            overrides_path = Path(f.name)
        
        try:
            manager = WitnessManager(overrides_path)
            
            # Without enforcement, both should apply
            result1 = manager.should_apply_override("John 3:16", enforce_witnesses=False)
            assert result1 == "With witness"
            
            result2 = manager.should_apply_override("John 1:1", enforce_witnesses=False)
            assert result2 == "Without witness"
            
            # With enforcement, only override with witness should apply
            result3 = manager.should_apply_override("John 3:16", enforce_witnesses=True)
            assert result3 == "With witness"
            
            result4 = manager.should_apply_override("John 1:1", enforce_witnesses=True)
            assert result4 is None  # Should not apply
        finally:
            overrides_path.unlink()

