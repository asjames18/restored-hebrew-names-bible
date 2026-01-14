"""Canonical Bible book ordering and utilities."""

# Canonical order of Bible books (KJV standard)
CANONICAL_BOOKS = [
    # Old Testament
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    # New Testament
    "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
    "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]

# Alternative book name mappings (common variations)
BOOK_NAME_MAPPINGS = {
    "1st Samuel": "1 Samuel",
    "2nd Samuel": "2 Samuel",
    "1st Kings": "1 Kings",
    "2nd Kings": "2 Kings",
    "1st Chronicles": "1 Chronicles",
    "2nd Chronicles": "2 Chronicles",
    "1st Corinthians": "1 Corinthians",
    "2nd Corinthians": "2 Corinthians",
    "1st Thessalonians": "1 Thessalonians",
    "2nd Thessalonians": "2 Thessalonians",
    "1st Timothy": "1 Timothy",
    "2nd Timothy": "2 Timothy",
    "1st Peter": "1 Peter",
    "2nd Peter": "2 Peter",
    "1st John": "1 John",
    "2nd John": "2 John",
    "3rd John": "3 John",
    "Song of Songs": "Song of Solomon",
    "Ecclesiastes": "Ecclesiastes",  # Already correct
    "Psalm": "Psalms",
    "Ps": "Psalms",
}


def normalize_book_name(book: str) -> str:
    """
    Normalize book name to canonical form.
    
    Args:
        book: Book name (may have variations)
        
    Returns:
        Canonical book name
    """
    book = book.strip()
    # Check mappings first
    if book in BOOK_NAME_MAPPINGS:
        return BOOK_NAME_MAPPINGS[book]
    # Check if it's already canonical
    if book in CANONICAL_BOOKS:
        return book
    # Try case-insensitive match
    for canonical in CANONICAL_BOOKS:
        if canonical.lower() == book.lower():
            return canonical
    # Return as-is if no match found
    return book


def get_book_order(book: str) -> int:
    """
    Get canonical order index for a book.
    
    Args:
        book: Book name
        
    Returns:
        Order index (0-based), or 999 if not found
    """
    normalized = normalize_book_name(book)
    try:
        return CANONICAL_BOOKS.index(normalized)
    except ValueError:
        return 999  # Unknown books go to end


def sort_verses(verses: list) -> list:
    """
    Sort verses by canonical book order, then chapter, then verse.
    
    Args:
        verses: List of verse dicts with 'book', 'chapter', 'verse' keys
        
    Returns:
        Sorted list of verses
    """
    def sort_key(verse):
        book = verse.get('book', '')
        chapter = verse.get('chapter', 0)
        verse_num = verse.get('verse', 0)
        return (get_book_order(book), chapter, verse_num)
    
    return sorted(verses, key=sort_key)


def is_old_testament(book: str) -> bool:
    """
    Check if book is in Old Testament.
    
    Args:
        book: Book name
        
    Returns:
        True if OT, False if NT or unknown
    """
    normalized = normalize_book_name(book)
    try:
        index = CANONICAL_BOOKS.index(normalized)
        return index < 39  # First 39 books are OT
    except ValueError:
        return False

