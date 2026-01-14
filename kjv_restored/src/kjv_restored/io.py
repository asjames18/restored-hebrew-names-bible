"""Input/output handling for different formats."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.rules import NameRules


class FormatHandler:
    """Handles different input/output formats."""
    
    @staticmethod
    def read_plain(input_path: Optional[Path]) -> str:
        """Read plain text from file or stdin."""
        if input_path:
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return sys.stdin.read()
    
    @staticmethod
    def read_json(input_path: Optional[Path]) -> List[Dict[str, Any]]:
        """Read JSON format (list of verse objects)."""
        if input_path:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
        
        if not isinstance(data, list):
            raise ValueError("JSON input must be a list of verse objects")
        
        return data
    
    @staticmethod
    def read_pipe(input_path: Optional[Path]) -> List[str]:
        """Read pipe format (one verse per line)."""
        if input_path:
            with open(input_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = sys.stdin.readlines()
        
        return [line.strip() for line in lines if line.strip()]
    
    @staticmethod
    def write_plain(output_path: Optional[Path], text: str) -> None:
        """Write plain text to file or stdout."""
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            sys.stdout.write(text)
    
    @staticmethod
    def write_json(output_path: Optional[Path], data: List[Dict[str, Any]]) -> None:
        """Write JSON format."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        else:
            sys.stdout.write(json_str)
    
    @staticmethod
    def write_pipe(output_path: Optional[Path], lines: List[str]) -> None:
        """Write pipe format (one verse per line)."""
        text = '\n'.join(lines) + '\n'
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            sys.stdout.write(text)


class ConversionIO:
    """Handles conversion with different formats."""
    
    def __init__(self, converter: RestoredNamesConverter):
        """
        Initialize conversion IO handler.
        
        Args:
            converter: RestoredNamesConverter instance
        """
        self.converter = converter
        self.format_handler = FormatHandler()
    
    def convert_plain(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Convert plain text format.
        
        Returns:
            Report dict with conversion statistics
        """
        # Reset tracking
        self.converter._applied_overrides = []
        self.converter._heuristic_replacements = []
        self.converter._ambiguous_lords = []
        
        text = self.format_handler.read_plain(input_path)
        converted = self.converter.convert_text(text, strict=strict)
        self.format_handler.write_plain(output_path, converted)
        
        # Build comprehensive report
        report = self._build_report('plain', strict=strict)
        report.update({
            'input_length': len(text),
            'output_length': len(converted),
            'changed': text != converted
        })
        
        return report
    
    def convert_json(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Convert JSON format.
        
        Returns:
            Report dict with conversion statistics
        """
        verses = self.format_handler.read_json(input_path)
        results = self.converter.batch_convert(verses, strict=strict)
        self.format_handler.write_json(output_path, results)
        
        changed_count = sum(1 for r in results if r['original'] != r['converted'])
        
        # Build comprehensive report
        report = self._build_report('json', strict=strict)
        report.update({
            'verse_count': len(verses),
            'changed_count': changed_count,
            'unchanged_count': len(verses) - changed_count
        })
        
        return report
    
    def convert_pipe(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Convert pipe format (one verse per line).
        
        Returns:
            Report dict with conversion statistics
        """
        # Reset tracking
        self.converter._applied_overrides = []
        self.converter._heuristic_replacements = []
        self.converter._ambiguous_lords = []
        
        lines = self.format_handler.read_pipe(input_path)
        converted_lines = [self.converter.convert_text(line, strict=strict) for line in lines]
        self.format_handler.write_pipe(output_path, converted_lines)
        
        changed_count = sum(1 for orig, conv in zip(lines, converted_lines) if orig != conv)
        
        # Build comprehensive report
        report = self._build_report('pipe', strict=strict)
        report.update({
            'line_count': len(lines),
            'changed_count': changed_count,
            'unchanged_count': len(lines) - changed_count
        })
        
        return report
    
    def _build_report(self, format_type: str, strict: bool = False) -> Dict[str, Any]:
        """
        Build comprehensive conversion report.
        
        Args:
            format_type: Format type ('plain', 'json', 'pipe')
            strict: Whether strict mode was used
        
        Returns:
            Report dictionary
        """
        report = {
            'format': format_type,
            'strict_mode': strict
        }
        
        # Applied overrides
        applied_overrides = self.converter.get_applied_overrides()
        if applied_overrides:
            report['applied_overrides'] = applied_overrides
            
            # Count replacements by type
            replacement_counts = {}
            for override in applied_overrides:
                replacements = override.get('replacements', {})
                for original, replacement in replacements.items():
                    if original != '__full_text__':
                        key = f"{original} -> {replacement}"
                        replacement_counts[key] = replacement_counts.get(key, 0) + 1
            if replacement_counts:
                report['replacement_counts'] = replacement_counts
        
        # Heuristic replacements
        heuristic_replacements = self.converter.get_heuristic_replacements()
        if heuristic_replacements:
            report['heuristic_replacements'] = heuristic_replacements
            # Count by type
            heuristic_counts = {}
            for hr in heuristic_replacements:
                h_type = hr.get('type', 'unknown')
                heuristic_counts[h_type] = heuristic_counts.get(h_type, 0) + 1
            report['heuristic_counts'] = heuristic_counts
        
        # Ambiguous Lord occurrences
        ambiguous_lords = self.converter.get_ambiguous_lords()
        if ambiguous_lords:
            report['ambiguous_lord_occurrences'] = ambiguous_lords
            report['ambiguous_lord_count'] = len(ambiguous_lords)
            report['ambiguous_lord_behavior'] = 'preserved' if strict else 'converted_to_ADON'
        
        return report
    
    def convert(
        self,
        input_path: Optional[Path],
        output_path: Optional[Path],
        format_type: str = 'plain',
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Convert based on format type.
        
        Args:
            input_path: Input file path (None for stdin)
            output_path: Output file path (None for stdout)
            format_type: Format type ('plain', 'json', 'pipe')
            strict: Enable strict mode
        
        Returns:
            Report dict with conversion statistics
        """
        format_type = format_type.lower()
        
        if format_type == 'plain':
            return self.convert_plain(input_path, output_path, strict=strict)
        elif format_type == 'json':
            return self.convert_json(input_path, output_path, strict=strict)
        elif format_type == 'pipe':
            return self.convert_pipe(input_path, output_path, strict=strict)
        else:
            raise ValueError(f"Unknown format: {format_type}")

