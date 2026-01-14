"""Tests for checklist generation."""

import pytest
import tempfile
import json
from pathlib import Path

from kjv_restored.checklist import ChecklistGenerator


class TestChecklistGenerator:
    """Test checklist generation functionality."""
    
    def test_scan_verse_lord_ambiguous(self):
        """Test scanning for ambiguous 'Lord' token."""
        generator = ChecklistGenerator()
        
        items = generator.scan_verse(
            "For whosoever shall call upon the name of the Lord shall be saved.",
            "Romans", 10, 13
        )
        
        assert len(items) > 0
        lord_item = next((item for item in items if item['needs'] == 'Lord decision'), None)
        assert lord_item is not None
        assert lord_item['ref'] == "Romans 10:13"
        assert 'YAHUAH' in lord_item['suggested']
        assert 'cepher' in lord_item['witnesses_required']
        assert 'dabar_yahuah' in lord_item['witnesses_required']
    
    def test_scan_verse_hallelujah_candidate(self):
        """Test scanning for hallelujah heuristic candidate."""
        generator = ChecklistGenerator()
        
        items = generator.scan_verse(
            "Praise ye the LORD.",
            "Psalms", 150, 1
        )
        
        assert len(items) > 0
        hallelujah_item = next((item for item in items if 'Hallelujah' in item['needs']), None)
        assert hallelujah_item is not None
        assert 'Hallelu-YAH' in hallelujah_item['suggested']
    
    def test_scan_verse_jah_token(self):
        """Test scanning for JAH token."""
        generator = ChecklistGenerator()
        
        items = generator.scan_verse(
            "Sing unto JAH, sing praises to JAH.",
            "Psalm", 68, 4
        )
        
        assert len(items) > 0
        jah_item = next((item for item in items if 'JAH token' in item['needs']), None)
        assert jah_item is not None
        assert jah_item['ref'] == "Psalm 68:4"
        assert 'kjv_token' in jah_item['witnesses_required']
    
    def test_scan_verse_multiple_issues(self):
        """Test scanning verse with multiple issues."""
        generator = ChecklistGenerator()
        
        items = generator.scan_verse(
            "Praise ye the LORD, O my soul. The Lord is good.",
            "Psalms", 103, 1
        )
        
        # Should find both hallelujah candidate and Lord decision
        assert len(items) >= 2
        needs = [item['needs'] for item in items]
        assert any('Hallelujah' in need for need in needs)
        assert any('Lord decision' in need for need in needs)
    
    def test_generate_checklist_from_json(self):
        """Test generating checklist from JSON input."""
        generator = ChecklistGenerator()
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            verses = [
                {
                    "book": "Romans",
                    "chapter": 10,
                    "verse": 13,
                    "text": "For whosoever shall call upon the name of the Lord shall be saved."
                },
                {
                    "book": "Psalm",
                    "chapter": 68,
                    "verse": 4,
                    "text": "Sing unto JAH, sing praises to JAH."
                }
            ]
            json.dump(verses, input_file)
            input_path = Path(input_file.name)
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)
        
        try:
            checklist = generator.generate_checklist(input_path, output_path)
            
            # Should have items
            assert len(checklist) > 0
            
            # Verify output file was created
            assert output_path.exists()
            
            # Verify output content
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_checklist = json.load(f)
            
            assert len(saved_checklist) == len(checklist)
            
            # Check that items are sorted by reference
            refs = [item['ref'] for item in saved_checklist]
            assert refs == sorted(refs)
            
        finally:
            input_path.unlink()
            output_path.unlink()
    
    def test_checklist_no_duplicates(self):
        """Test that checklist removes duplicates."""
        generator = ChecklistGenerator()
        
        # Create input with same verse appearing multiple times
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            verses = [
                {
                    "book": "Romans",
                    "chapter": 10,
                    "verse": 13,
                    "text": "For whosoever shall call upon the name of the Lord shall be saved."
                },
                {
                    "book": "Romans",
                    "chapter": 10,
                    "verse": 13,
                    "text": "For whosoever shall call upon the name of the Lord shall be saved."
                }
            ]
            json.dump(verses, input_file)
            input_path = Path(input_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)
        
        try:
            checklist = generator.generate_checklist(input_path, output_path)
            
            # Should have only one item for Romans 10:13
            romans_items = [item for item in checklist if item['ref'] == "Romans 10:13"]
            assert len(romans_items) == 1
            
        finally:
            input_path.unlink()
            output_path.unlink()
    
    def test_checklist_no_verse_text_in_output(self):
        """Test that checklist does not include verse text from external Bibles."""
        generator = ChecklistGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            verses = [
                {
                    "book": "Romans",
                    "chapter": 10,
                    "verse": 13,
                    "text": "For whosoever shall call upon the name of the Lord shall be saved."
                }
            ]
            json.dump(verses, input_file)
            input_path = Path(input_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = Path(output_file.name)
        
        try:
            checklist = generator.generate_checklist(input_path, output_path)
            
            # Verify checklist items don't contain full verse text
            for item in checklist:
                # Should only have ref, needs, suggested, witnesses_required
                assert 'text' not in item
                assert 'verse_text' not in item
                assert 'cepher_text' not in item
                assert 'dabar_yahuah_text' not in item
                
        finally:
            input_path.unlink()
            output_path.unlink()

