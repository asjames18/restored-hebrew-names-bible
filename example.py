"""
Example usage of the KJV Restored Names Converter
"""

from converter import RestoredNamesConverter

def main():
    # Initialize converter
    converter = RestoredNamesConverter()
    
    # Example 1: Basic conversion
    print("=== Example 1: Basic Conversion ===")
    text1 = "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."
    converted1 = converter.convert_text(text1)
    print(f"Original: {text1}")
    print(f"Converted: {converted1}\n")
    
    # Example 2: Verse-aware conversion
    print("=== Example 2: Verse-Aware Conversion ===")
    text2 = "John 3:16 For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."
    converted2 = converter.convert_text(text2, verse_aware=True)
    print(f"Original: {text2}")
    print(f"Converted: {converted2}\n")
    
    # Example 3: Add an override with witnesses
    print("=== Example 3: Adding Override with Witnesses ===")
    converter.add_override(
        verse_ref="John 3:16",
        replacement="For YAHUAH so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
        witnesses=["cepher", "dabar_yahuah"],
        require_witness=True
    )
    print("Added override for John 3:16 with witnesses: cepher, dabar_yahuah\n")
    
    # Example 4: Convert with override applied
    print("=== Example 4: Conversion with Override ===")
    text4 = "For God so loved the world..."
    converted4 = converter.convert_verse(
        text4,
        book="John",
        chapter=3,
        verse=16,
        enforce_witnesses=False
    )
    print(f"Original: {text4}")
    print(f"Converted (with override): {converted4}\n")
    
    # Example 5: Multiple name conversions
    print("=== Example 5: Multiple Name Conversions ===")
    text5 = "Jesus Christ is the Lord and Messiah. The Holy Spirit guides us."
    converted5 = converter.convert_text(text5)
    print(f"Original: {text5}")
    print(f"Converted: {converted5}\n")
    
    # Example 6: Hallelujah conversion
    print("=== Example 6: Hallelujah Conversion ===")
    text6 = "Hallelujah! Praise the Lord!"
    converted6 = converter.convert_text(text6)
    print(f"Original: {text6}")
    print(f"Converted: {converted6}\n")

if __name__ == '__main__':
    main()

