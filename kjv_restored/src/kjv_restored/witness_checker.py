"""Automated witness checking against local Bible files."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

from kjv_restored.books import normalize_book_name

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class WitnessChecker:
    """Checks verses against local witness Bible files."""
    
    def __init__(self, cepher_file: Optional[Path] = None, dabar_yahuah_file: Optional[Path] = None):
        """
        Initialize witness checker.
        
        Args:
            cepher_file: Path to local Cepher Bible JSON file
            dabar_yahuah_file: Path to local Dâbâr Yahuah Bible JSON file
        """
        self.cepher_file = cepher_file
        self.dabar_yahuah_file = dabar_yahuah_file
        self.cepher_verses: Dict[str, str] = {}
        self.dabar_yahuah_verses: Dict[str, str] = {}
        self._load_witnesses()
    
    def _load_witnesses(self):
        """Load witness Bible files into memory."""
        if self.cepher_file and self.cepher_file.exists():
            self.cepher_verses = self._load_bible_file(self.cepher_file)
        
        if self.dabar_yahuah_file and self.dabar_yahuah_file.exists():
            self.dabar_yahuah_verses = self._load_bible_file(self.dabar_yahuah_file)
    
    def _load_bible_file(self, file_path: Path) -> Dict[str, str]:
        """
        Load Bible file into verse dictionary.
        
        Supports:
        - JSON files: Array of verse objects or dict keyed by verse reference
        - DOCX files: Word document with verse text (attempts to parse structure)
        
        Returns:
            Dictionary mapping verse keys to text
        """
        if file_path.suffix.lower() == '.json':
            return self._load_json_file(file_path)
        elif file_path.suffix.lower() == '.docx':
            return self._load_docx_file(file_path)
        else:
            # Try JSON first, then DOCX
            try:
                return self._load_json_file(file_path)
            except:
                if DOCX_AVAILABLE:
                    return self._load_docx_file(file_path)
                else:
                    print(f"Warning: Could not determine file type for {file_path}", file=__import__('sys').stderr)
                    return {}
    
    def _load_json_file(self, file_path: Path) -> Dict[str, str]:
        """Load JSON Bible file."""
        verses = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for verse_obj in data:
                    verse_key = self._get_verse_key_from_obj(verse_obj)
                    if verse_key and 'text' in verse_obj:
                        verses[verse_key] = verse_obj['text']
            elif isinstance(data, dict):
                # Assume it's already keyed by verse reference
                verses = data
            
        except Exception as e:
            print(f"Warning: Could not load JSON file {file_path}: {e}", file=__import__('sys').stderr)
        
        return verses
    
    def _load_docx_file(self, file_path: Path) -> Dict[str, str]:
        """
        Load DOCX Bible file.
        
        Attempts to parse DOCX structure to extract verses.
        Looks for patterns like:
        - Verse numbers (superscript or inline)
        - Book/chapter headings
        - Verse text
        
        Returns:
            Dictionary mapping verse keys to text
        """
        if not DOCX_AVAILABLE:
            print(f"Warning: python-docx not available, cannot load DOCX file {file_path}", file=__import__('sys').stderr)
            return {}
        
        verses = {}
        try:
            doc = Document(str(file_path))
            current_book = None
            current_chapter = None
            current_verse = None
            verse_text_parts = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                # Check if this is a book heading (Heading 1 style or all caps)
                if para.style.name.startswith('Heading 1') or (text.isupper() and len(text) < 50):
                    # Might be a book name
                    normalized = normalize_book_name(text)
                    if normalized:  # If it matches a known book
                        current_book = normalized
                        current_chapter = None
                        current_verse = None
                        verse_text_parts = []
                    continue
                
                # Check if this is a chapter heading (Heading 2 style or "Chapter X")
                chapter_match = re.search(r'Chapter\s+(\d+)', text, re.IGNORECASE)
                if chapter_match or para.style.name.startswith('Heading 2'):
                    if chapter_match:
                        current_chapter = int(chapter_match.group(1))
                    current_verse = None
                    verse_text_parts = []
                    continue
                
                # Try to extract verse number and text
                # Pattern: verse number (superscript or inline) followed by text
                verse_match = re.match(r'^(\d+)\s+(.+)$', text)
                if verse_match:
                    verse_num = int(verse_match.group(1))
                    verse_text = verse_match.group(2)
                    
                    if current_book and current_chapter:
                        verse_key = f"{current_book} {current_chapter}:{verse_num}"
                        verses[verse_key] = verse_text
                        current_verse = verse_num
                else:
                    # Might be continuation of previous verse or verse with superscript
                    # Look for superscript numbers in runs
                    verse_num = None
                    verse_text = ""
                    
                    for run in para.runs:
                        run_text = run.text
                        # Check if this run has superscript (verse number)
                        if run.font.superscript and run_text.strip().isdigit():
                            verse_num = int(run_text.strip())
                        else:
                            verse_text += run_text
                    
                    if verse_num and current_book and current_chapter:
                        verse_key = f"{current_book} {current_chapter}:{verse_num}"
                        verses[verse_key] = verse_text.strip()
                        current_verse = verse_num
                    elif current_verse and current_book and current_chapter:
                        # Continuation of previous verse
                        verse_key = f"{current_book} {current_chapter}:{current_verse}"
                        if verse_key in verses:
                            verses[verse_key] += " " + text
                        else:
                            verses[verse_key] = text
            
        except Exception as e:
            print(f"Warning: Could not load DOCX file {file_path}: {e}", file=__import__('sys').stderr)
            import traceback
            traceback.print_exc()
        
        return verses
    
    def _get_verse_key_from_obj(self, verse_obj: Dict) -> Optional[str]:
        """Extract verse key from verse object."""
        if 'ref' in verse_obj:
            return verse_obj['ref']
        elif 'book' in verse_obj and 'chapter' in verse_obj and 'verse' in verse_obj:
            book = normalize_book_name(verse_obj['book'])
            return f"{book} {verse_obj['chapter']}:{verse_obj['verse']}"
        return None
    
    def check_verse(self, verse_key: str, kjv_text: str) -> Dict[str, any]:
        """
        Check a verse against witness files.
        
        Args:
            verse_key: Verse reference (e.g., "Genesis 1:1")
            kjv_text: KJV verse text
            
        Returns:
            Dictionary with check results:
            {
                'cepher_found': bool,
                'dabar_yahuah_found': bool,
                'cepher_text': str or None,
                'dabar_yahuah_text': str or None,
                'name_matches': {
                    'YAHUAH': {'cepher': bool, 'dabar_yahuah': bool},
                    'YAHUSHA': {'cepher': bool, 'dabar_yahuah': bool},
                    ...
                },
                'suggested_replacements': Dict[str, str],
                'witnesses': List[str]
            }
        """
        result = {
            'verse_key': verse_key,
            'cepher_found': False,
            'dabar_yahuah_found': False,
            'cepher_text': None,
            'dabar_yahuah_text': None,
            'name_matches': {},
            'suggested_replacements': {},
            'witnesses': []
        }
        
        # Check Cepher
        if verse_key in self.cepher_verses:
            result['cepher_found'] = True
            result['cepher_text'] = self.cepher_verses[verse_key]
            result['witnesses'].append('cepher')
        
        # Check Dâbâr Yahuah
        if verse_key in self.dabar_yahuah_verses:
            result['dabar_yahuah_found'] = True
            result['dabar_yahuah_text'] = self.dabar_yahuah_verses[verse_key]
            result['witnesses'].append('dabar_yahuah')
        
        # Analyze name usage
        if result['cepher_found'] or result['dabar_yahuah_found']:
            result['name_matches'] = self._analyze_names(
                kjv_text,
                result['cepher_text'],
                result['dabar_yahuah_text']
            )
            result['suggested_replacements'] = self._suggest_replacements(
                kjv_text,
                result['name_matches'],
                result['witnesses']
            )
        
        return result
    
    def _analyze_names(self, kjv_text: str, cepher_text: Optional[str], dabar_yahuah_text: Optional[str]) -> Dict[str, Dict[str, bool]]:
        """
        Analyze which restored names appear in witness texts.
        
        Returns:
            Dictionary mapping name to witness presence:
            {
                'YAHUAH': {'cepher': True, 'dabar_yahuah': True},
                'YAHUSHA': {'cepher': False, 'dabar_yahuah': True},
                ...
            }
        """
        names_to_check = ['YAHUAH', 'YAH', 'YAHUSHA', "HA'MASHIACH", 'RUACH HAQODESH', 'ELOHIYM', 'ADON']
        matches = {}
        
        for name in names_to_check:
            matches[name] = {
                'cepher': bool(cepher_text and name in cepher_text),
                'dabar_yahuah': bool(dabar_yahuah_text and name in dabar_yahuah_text)
            }
        
        return matches
    
    def _suggest_replacements(self, kjv_text: str, name_matches: Dict, witnesses: List[str]) -> Dict[str, str]:
        """
        Suggest replacements based on witness analysis.
        
        Args:
            kjv_text: Original KJV text
            name_matches: Name analysis results
            witnesses: List of available witnesses
            
        Returns:
            Dictionary of suggested replacements: {original_token: replacement}
        """
        suggestions = {}
        
        # Check for LORD -> YAHUAH or YAH
        if re.search(r'\bLORD\b', kjv_text):
            # If both witnesses have YAHUAH, suggest YAHUAH
            if name_matches.get('YAHUAH', {}).get('cepher') and name_matches.get('YAHUAH', {}).get('dabar_yahuah'):
                suggestions['LORD'] = 'YAHUAH'
            # If both have YAH (short form), suggest YAH
            elif name_matches.get('YAH', {}).get('cepher') and name_matches.get('YAH', {}).get('dabar_yahuah'):
                suggestions['LORD'] = 'YAH'
            # If only one witness, be conservative
            elif len(witnesses) == 1 and name_matches.get('YAHUAH', {}).get(witnesses[0]):
                suggestions['LORD'] = 'YAHUAH'
        
        # Check for God -> YAHUAH or ELOHIYM
        if re.search(r'\bGod\b', kjv_text, re.IGNORECASE):
            # If both witnesses have YAHUAH, suggest YAHUAH
            if name_matches.get('YAHUAH', {}).get('cepher') and name_matches.get('YAHUAH', {}).get('dabar_yahuah'):
                suggestions['God'] = 'YAHUAH'
            # If both have ELOHIYM, suggest ELOHIYM
            elif name_matches.get('ELOHIYM', {}).get('cepher') and name_matches.get('ELOHIYM', {}).get('dabar_yahuah'):
                suggestions['God'] = 'ELOHIYM'
        
        # Check for Jesus -> YAHUSHA
        if re.search(r'\bJesus\b', kjv_text):
            if name_matches.get('YAHUSHA', {}).get('cepher') or name_matches.get('YAHUSHA', {}).get('dabar_yahuah'):
                suggestions['Jesus'] = 'YAHUSHA'
        
        # Check for Christ -> HA'MASHIACH
        if re.search(r'\bChrist\b', kjv_text):
            if name_matches.get("HA'MASHIACH", {}).get('cepher') or name_matches.get("HA'MASHIACH", {}).get('dabar_yahuah'):
                suggestions['Christ'] = "HA'MASHIACH"
        
        # Check for Holy Spirit/Ghost -> RUACH HAQODESH
        if re.search(r'\bHoly\s+(?:Spirit|Ghost)\b', kjv_text):
            if name_matches.get('RUACH HAQODESH', {}).get('cepher') or name_matches.get('RUACH HAQODESH', {}).get('dabar_yahuah'):
                suggestions['Holy Spirit'] = 'RUACH HAQODESH'
                suggestions['Holy Ghost'] = 'RUACH HAQODESH'
        
        return suggestions
    
    def check_batch(self, verses: List[Dict]) -> List[Dict]:
        """
        Check multiple verses against witnesses.
        
        Args:
            verses: List of verse dicts with 'book', 'chapter', 'verse', 'text'
            
        Returns:
            List of check results
        """
        results = []
        for verse in verses:
            book = normalize_book_name(verse.get('book', ''))
            chapter = verse.get('chapter', 0)
            verse_num = verse.get('verse', 0)
            verse_key = f"{book} {chapter}:{verse_num}"
            kjv_text = verse.get('text', '')
            
            check_result = self.check_verse(verse_key, kjv_text)
            results.append(check_result)
        
        return results
    
    def generate_overrides(self, check_results: List[Dict], min_witnesses: int = 1) -> Dict[str, Dict]:
        """
        Generate overrides.json entries from check results.
        
        Args:
            check_results: List of check results from check_batch()
            min_witnesses: Minimum number of witnesses required (1 or 2)
            
        Returns:
            Dictionary suitable for overrides.json
        """
        overrides = {}
        
        for result in check_results:
            verse_key = result['verse_key']
            witnesses = result['witnesses']
            suggestions = result['suggested_replacements']
            
            # Only create override if we have enough witnesses
            if len(witnesses) >= min_witnesses and suggestions:
                overrides[verse_key] = {
                    'replacements': suggestions,
                    'witnesses': witnesses,
                    'note': f'Auto-generated from witness check (min_witnesses={min_witnesses})'
                }
        
        return overrides

