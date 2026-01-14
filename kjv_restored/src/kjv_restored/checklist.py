"""Checklist generation for manual override review."""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

from kjv_restored.io import FormatHandler


class ChecklistGenerator:
    """Generates checklist of verses needing manual review."""
    
    def __init__(self):
        """Initialize checklist generator."""
        self.format_handler = FormatHandler()
    
    def scan_verse(self, text: str, book: str, chapter: int, verse: int) -> List[Dict[str, Any]]:
        """
        Scan a verse for sensitive tokens that need manual review.
        
        Args:
            text: Verse text
            book: Book name
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            List of checklist items for this verse
        """
        items = []
        verse_ref = f"{book} {chapter}:{verse}"
        
        # Check for "Lord" (not all caps) - NT ambiguous
        if re.search(r'\bLord\b', text) and not re.search(r'\bLORD\b', text):
            items.append({
                'ref': verse_ref,
                'needs': 'Lord decision',
                'suggested': 'YAHUAH (if OT quote) or ADON (if NT reference)',
                'witnesses_required': ['cepher', 'dabar_yahuah']
            })
        
        # Check for "Praise ye the LORD" - hallelujah heuristic candidate
        if re.search(r'Praise ye the LORD', text, re.IGNORECASE):
            items.append({
                'ref': verse_ref,
                'needs': 'Hallelujah heuristic decision',
                'suggested': 'Hallelu-YAH (if appropriate)',
                'witnesses_required': []
            })
        
        # Check for "JAH" token - may need override
        if re.search(r'\bJAH\b', text):
            items.append({
                'ref': verse_ref,
                'needs': 'JAH token review',
                'suggested': 'YAH (KJV contains JAH)',
                'witnesses_required': ['kjv_token']
            })
        
        # Check for other sensitive patterns
        # "God" vs "GOD" distinction
        # Only flag if it's ambiguous (not already handled by default rules)
        # This is less critical, so we'll skip it for now
        
        return items
    
    def generate_checklist(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path]
    ) -> List[Dict[str, Any]]:
        """
        Generate checklist from JSON input file.
        
        Args:
            input_path: Path to input JSON file (list of verse objects)
            output_path: Path to output checklist JSON file
            
        Returns:
            List of checklist items
        """
        # Read verses from JSON
        verses = self.format_handler.read_json(input_path)
        
        # Scan all verses
        checklist = []
        for verse in verses:
            text = verse.get('text', '')
            book = verse.get('book', '')
            chapter = verse.get('chapter', 0)
            verse_num = verse.get('verse', 0)
            
            items = self.scan_verse(text, book, chapter, verse_num)
            checklist.extend(items)
        
        # Remove duplicates (same verse ref with same need)
        seen = set()
        unique_checklist = []
        for item in checklist:
            key = (item['ref'], item['needs'])
            if key not in seen:
                seen.add(key)
                unique_checklist.append(item)
        
        # Sort by reference
        unique_checklist.sort(key=lambda x: x['ref'])
        
        # Write to output file
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(unique_checklist, f, indent=2, ensure_ascii=False)
        else:
            # Write to stdout
            json.dump(unique_checklist, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write('\n')
        
        return unique_checklist

