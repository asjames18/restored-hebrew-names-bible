"""PDF export for full Bible."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Iterator, Tuple, List
import sys

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class PDFExporter:
    """Exports Bible to PDF format."""
    
    def __init__(self, title: str, version: str):
        """
        Initialize PDF exporter.
        
        Args:
            title: Document title
            version: Version string
        """
        if not PDF_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
        
        self.title = title
        self.version = version
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.story = []
        self.books_seen = []
    
    def _setup_styles(self):
        """Set up custom paragraph styles."""
        # Book heading style
        self.book_style = ParagraphStyle(
            'BookHeading',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor='black',
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Chapter heading style
        self.chapter_style = ParagraphStyle(
            'ChapterHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor='black',
            spaceAfter=6,
            spaceBefore=6
        )
        
        # Verse style
        self.verse_style = ParagraphStyle(
            'Verse',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=3,
            leftIndent=0
        )
        
        # Title style
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Title'],
            fontSize=24,
            textColor='black',
            alignment=TA_CENTER,
            spaceAfter=12
        )
    
    def _add_page_number(self, canvas_obj, doc):
        """Add page number to footer."""
        page_num = canvas_obj.getPageNumber()
        text = f"{page_num}"
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.drawCentredString(letter[0] / 2.0, 0.75 * inch, text)
        canvas_obj.restoreState()
    
    def add_title_page(self):
        """Add title page content."""
        self.story.append(Spacer(1, 2 * inch))
        
        # Title
        title_para = Paragraph(self.title, self.title_style)
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.5 * inch))
        
        # Version
        version_para = Paragraph(self.version, self.styles['Heading2'])
        version_para.alignment = TA_CENTER
        self.story.append(version_para)
        self.story.append(Spacer(1, 0.3 * inch))
        
        # Date
        date_text = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        date_para = Paragraph(date_text, self.styles['Normal'])
        date_para.alignment = TA_CENTER
        self.story.append(date_para)
        self.story.append(Spacer(1, 0.5 * inch))
        
        # Disclaimer
        disclaimer_text = (
            "Generated from user-supplied KJV text using restored-name rules. "
            "This document does not include or redistribute text from Cepher Bible or Dâbâr Yahuah."
        )
        disclaimer_para = Paragraph(disclaimer_text, self.styles['Normal'])
        disclaimer_para.alignment = TA_CENTER
        self.story.append(disclaimer_para)
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self, books: List[str]):
        """
        Add table of contents.
        
        Args:
            books: List of book names
        """
        toc_heading = Paragraph("Table of Contents", self.styles['Heading1'])
        self.story.append(toc_heading)
        self.story.append(Spacer(1, 0.3 * inch))
        
        for book in books:
            book_para = Paragraph(f"• {book}", self.styles['Normal'])
            self.story.append(book_para)
        
        self.story.append(PageBreak())
    
    def add_book_heading(self, book_name: str):
        """
        Add book heading.
        
        Args:
            book_name: Name of the book
        """
        if book_name not in self.books_seen:
            self.books_seen.append(book_name)
        
        heading = Paragraph(book_name, self.book_style)
        self.story.append(heading)
    
    def add_chapter_heading(self, chapter_num: int):
        """
        Add chapter heading.
        
        Args:
            chapter_num: Chapter number
        """
        heading = Paragraph(f"Chapter {chapter_num}", self.chapter_style)
        self.story.append(heading)
    
    def add_verse(self, verse_num: int, text: str):
        """
        Add verse text.
        
        Args:
            verse_num: Verse number
            text: Verse text
        """
        # Format: "1 In the beginning..." with verse number in smaller font
        verse_text = f"<font size='9'><sup>{verse_num}</sup></font> {text}"
        para = Paragraph(verse_text, self.verse_style)
        self.story.append(para)
    
    def export(self, events: Iterator[Tuple[str, Dict[str, Any]]], output_path: Path, progress_callback: Optional[callable] = None):
        """
        Export Bible from event stream.
        
        Args:
            events: Iterator of (event_type, event_data) tuples
            output_path: Output file path
            progress_callback: Optional progress callback
        """
        current_book = None
        current_chapter = None
        
        # Add title page
        self.add_title_page()
        
        # Process events
        for event_type, event_data in events:
            if event_type == "book":
                book_name = event_data["name"]
                if book_name not in self.books_seen:
                    self.books_seen.append(book_name)
                current_book = book_name
                self.add_book_heading(book_name)
                if progress_callback:
                    progress_callback(book_name, None, None)
            
            elif event_type == "chapter":
                chapter_num = event_data["number"]
                current_chapter = chapter_num
                self.add_chapter_heading(chapter_num)
            
            elif event_type == "verse":
                verse_num = event_data["verse"]
                text = event_data["text"]
                self.add_verse(verse_num, text)
                if progress_callback:
                    progress_callback(current_book, current_chapter, verse_num)
            
            elif event_type == "end":
                break
        
        # Add TOC (simplified - just list of books)
        # Note: In a full implementation, we'd need to track page numbers
        # For now, we'll add a simple TOC after title page
        
        # Build PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=1 * inch,
            leftMargin=1 * inch,
            topMargin=1 * inch,
            bottomMargin=1 * inch
        )
        
        # Add page number callback
        def on_first_page(canvas_obj, doc):
            self._add_page_number(canvas_obj, doc)
        
        def on_later_pages(canvas_obj, doc):
            self._add_page_number(canvas_obj, doc)
        
        doc.build(self.story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    
    @staticmethod
    def is_available() -> bool:
        """Check if PDF export is available."""
        return PDF_AVAILABLE

