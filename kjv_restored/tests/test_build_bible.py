"""Tests for full Bible build functionality."""

import pytest
import tempfile
import json
from pathlib import Path

from kjv_restored.books import sort_verses, normalize_book_name, get_book_order, CANONICAL_BOOKS
from kjv_restored.assembler import BibleAssembler
from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config


class TestBookOrdering:
    """Test canonical book ordering."""
    
    def test_canonical_order(self):
        """Test that books are in canonical order."""
        assert CANONICAL_BOOKS[0] == "Genesis"
        assert CANONICAL_BOOKS[-1] == "Revelation"
        assert "Matthew" in CANONICAL_BOOKS
        assert CANONICAL_BOOKS.index("Matthew") > CANONICAL_BOOKS.index("Malachi")
    
    def test_normalize_book_name(self):
        """Test book name normalization."""
        assert normalize_book_name("Genesis") == "Genesis"
        assert normalize_book_name("genesis") == "Genesis"
        assert normalize_book_name("1 Samuel") == "1 Samuel"
        assert normalize_book_name("1st Samuel") == "1 Samuel"
        assert normalize_book_name("Psalm") == "Psalms"
    
    def test_get_book_order(self):
        """Test getting book order index."""
        assert get_book_order("Genesis") == 0
        assert get_book_order("Revelation") == 65
        assert get_book_order("Unknown Book") == 999
    
    def test_sort_verses(self):
        """Test verse sorting by canonical order."""
        verses = [
            {"book": "John", "chapter": 1, "verse": 1, "text": "..."},
            {"book": "Genesis", "chapter": 1, "verse": 1, "text": "..."},
            {"book": "Exodus", "chapter": 1, "verse": 1, "text": "..."}
        ]
        
        sorted_verses = sort_verses(verses)
        
        assert sorted_verses[0]["book"] == "Genesis"
        assert sorted_verses[1]["book"] == "Exodus"
        assert sorted_verses[2]["book"] == "John"


class TestBibleAssembler:
    """Test Bible assembly."""
    
    def test_load_verses(self):
        """Test loading and sorting verses."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            verses = [
                {"book": "John", "chapter": 1, "verse": 1, "text": "In the beginning..."},
                {"book": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning..."}
            ]
            json.dump(verses, f)
            input_path = Path(f.name)
        
        try:
            config = Config()
            converter = RestoredNamesConverter(config=config)
            assembler = BibleAssembler(converter)
            
            loaded = assembler.load_verses(input_path)
            
            # Should be sorted
            assert loaded[0]["book"] == "Genesis"
            assert loaded[1]["book"] == "John"
        finally:
            input_path.unlink()
    
    def test_assemble_events(self):
        """Test that assembler yields correct events."""
        verses = [
            {"book": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning God created..."},
            {"book": "Genesis", "chapter": 1, "verse": 2, "text": "And the earth was without form..."}
        ]
        
        config = Config()
        converter = RestoredNamesConverter(config=config)
        assembler = BibleAssembler(converter)
        
        events = list(assembler.assemble(verses))
        
        # Should have book, chapter, verses, end
        event_types = [e[0] for e in events]
        assert "book" in event_types
        assert "chapter" in event_types
        assert "verse" in event_types
        assert "end" in event_types
        
        # Check book event
        book_events = [e for e in events if e[0] == "book"]
        assert len(book_events) == 1
        assert book_events[0][1]["name"] == "Genesis"
        
        # Check verse events
        verse_events = [e for e in events if e[0] == "verse"]
        assert len(verse_events) == 2
        assert verse_events[0][1]["verse"] == 1
        assert verse_events[1][1]["verse"] == 2
    
    def test_generate_report(self):
        """Test report generation."""
        verses = [
            {"book": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning God created..."}
        ]
        
        config = Config()
        converter = RestoredNamesConverter(config=config)
        assembler = BibleAssembler(converter)
        
        # Process verses
        list(assembler.assemble(verses))
        
        # Generate report
        report = assembler.generate_report("Test Title", "v1.0")
        
        assert report['title'] == "Test Title"
        assert report['version'] == "v1.0"
        assert 'statistics' in report
        assert report['statistics']['total_verses'] == 1
        assert report['statistics']['books_processed'] == 1


class TestBuildBibleIntegration:
    """Integration tests for full Bible build."""
    
    def test_mini_bible_build(self):
        """Test building a mini Bible from sample data."""
        # This test will verify the build process works end-to-end
        # Actual file generation will be tested separately
        mini_kjv_path = Path("data/mini_kjv.json")
        
        if not mini_kjv_path.exists():
            pytest.skip("mini_kjv.json not found")
        
        config = Config()
        converter = RestoredNamesConverter(config=config)
        assembler = BibleAssembler(converter)
        
        verses = assembler.load_verses(mini_kjv_path)
        
        # Verify verses loaded
        assert len(verses) > 0
        
        # Verify conversion works
        events = list(assembler.assemble(verses))
        verse_events = [e for e in events if e[0] == "verse"]
        
        # Check that conversions were applied
        for event_type, event_data in verse_events:
            text = event_data["text"]
            # Should have some conversions
            assert "God" not in text or "YAHUAH" in text or "ELOHIYM" in text

