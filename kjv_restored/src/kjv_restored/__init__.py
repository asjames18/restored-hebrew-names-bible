"""
KJV Restored Names Converter

A tool to convert King James Version (KJV) Bible text to use restored Hebrew names.
"""

__version__ = "1.0.0"

from kjv_restored.converter import RestoredNamesConverter
from kjv_restored.config import Config
from kjv_restored.witness import WitnessManager
from kjv_restored.checklist import ChecklistGenerator
from kjv_restored.assembler import BibleAssembler
from kjv_restored.export_docx import DOCXExporter
from kjv_restored.export_pdf import PDFExporter

__all__ = [
    "RestoredNamesConverter",
    "Config",
    "WitnessManager",
    "ChecklistGenerator",
    "BibleAssembler",
    "DOCXExporter",
    "PDFExporter",
]

