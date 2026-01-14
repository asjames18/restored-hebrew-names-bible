"""Bible assembly and structure generation."""

from datetime import datetime
from typing import Dict, List, Iterator, Tuple, Optional, Any
import json
from pathlib import Path

from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config
from kjv_restored.books import sort_verses, normalize_book_name


class BibleAssembler:
    """Assembles Bible structure from verse data."""
    
    def __init__(self, converter: RestoredNamesConverter):
        """
        Initialize assembler.
        
        Args:
            converter: RestoredNamesConverter instance
        """
        self.converter = converter
        self.stats = {
            'total_verses': 0,
            'books_processed': 0,
            'chapters_processed': 0,
            'ambiguous_lords': 0,
            'applied_overrides': 0
        }
    
    def load_verses(self, input_path: Path) -> List[Dict[str, Any]]:
        """
        Load and sort verses from JSON file.
        
        Args:
            input_path: Path to JSON file with verse data
            
        Returns:
            Sorted list of verse dicts
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            verses = json.load(f)
        
        if not isinstance(verses, list):
            raise ValueError("Input JSON must be a list of verse objects")
        
        # Sort by canonical order
        sorted_verses = sort_verses(verses)
        return sorted_verses
    
    def assemble(self, verses: List[Dict[str, Any]], progress_callback: Optional[callable] = None) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """
        Assemble Bible structure, yielding events.
        
        Events are tuples of (type, data):
        - ("title", {"text": "The Restored Names KJV", ...})
        - ("toc", {})
        - ("book", {"name": "Genesis", "number": 1})
        - ("chapter", {"book": "Genesis", "number": 1})
        - ("verse", {"book": "Genesis", "chapter": 1, "verse": 1, "text": "..."})
        - ("end", {})
        
        Args:
            verses: List of verse dicts
            progress_callback: Optional callback(book, chapter, verse) for progress updates
            
        Yields:
            Tuples of (event_type, event_data)
        """
        # Reset stats
        self.stats = {
            'total_verses': 0,
            'books_processed': 0,
            'chapters_processed': 0,
            'ambiguous_lords': 0,
            'applied_overrides': 0
        }
        
        current_book = None
        current_chapter = None
        
        for verse in verses:
            book = normalize_book_name(verse.get('book', ''))
            chapter = verse.get('chapter', 0)
            verse_num = verse.get('verse', 0)
            text = verse.get('text', '')
            
            # New book
            if book != current_book:
                if current_book is not None:
                    # End previous book (could add book end event if needed)
                    pass
                current_book = book
                current_chapter = None
                self.stats['books_processed'] += 1
                yield ("book", {"name": book, "number": self.stats['books_processed']})
            
            # New chapter
            if chapter != current_chapter:
                current_chapter = chapter
                self.stats['chapters_processed'] += 1
                yield ("chapter", {"book": book, "number": chapter})
            
            # Convert verse text
            verse_ref = f"{book} {chapter}:{verse_num}"
            converted_text = self.converter.convert_verse(
                text,
                book,
                chapter,
                verse_num,
                strict=self.converter.config.strict_mode
            )
            
            # Track stats
            self.stats['total_verses'] += 1
            if self.converter.get_applied_overrides():
                self.stats['applied_overrides'] = len(self.converter.get_applied_overrides())
            if self.converter.get_ambiguous_lords():
                self.stats['ambiguous_lords'] = len(self.converter.get_ambiguous_lords())
            
            # Yield verse event
            yield ("verse", {
                "book": book,
                "chapter": chapter,
                "verse": verse_num,
                "text": converted_text,
                "original_text": text
            })
            
            # Progress callback
            if progress_callback:
                progress_callback(book, chapter, verse_num)
        
        yield ("end", {})
    
    def generate_report(self, title: str, version: str) -> Dict[str, Any]:
        """
        Generate conversion report.
        
        Args:
            title: Document title
            version: Version string
            
        Returns:
            Report dictionary
        """
        report = {
            'title': title,
            'version': version,
            'generated_date': datetime.now().isoformat(),
            'statistics': self.stats.copy(),
            'applied_overrides': self.converter.get_applied_overrides(),
            'ambiguous_lord_occurrences': self.converter.get_ambiguous_lords(),
            'heuristic_replacements': self.converter.get_heuristic_replacements()
        }
        
        # Add replacement counts
        replacement_counts = {}
        for override in self.converter.get_applied_overrides():
            replacements = override.get('replacements', {})
            for original, replacement in replacements.items():
                if original != '__full_text__':
                    key = f"{original} -> {replacement}"
                    replacement_counts[key] = replacement_counts.get(key, 0) + 1
        if replacement_counts:
            report['replacement_counts'] = replacement_counts
        
        return report

