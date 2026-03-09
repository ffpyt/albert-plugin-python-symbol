# -*- coding: utf-8 -*-

"""
Albert plugin for searching Unicode and ASCII characters.
Search for characters using their name, description, block names, or the characters themselves.
Enter to copy the symbol, Alt+Enter to copy HTML entity if available.
"""
from pathlib import Path
from typing import List
import htmlentities

from albert import *

md_iid = "5.0"
md_version = "1.0.0"
md_name = "Unicode Symbols"
md_description = "Search and copy Unicode symbols and characters"
md_license = "GPL-3.0"
md_url = "https://github.com/ffpyt/albert-plugin-python-symbol"
md_readme_url = "https://github.com/ffpyt/albert-plugin-python-symbol/blob/master/README.md"
md_authors = ["@ffpyt"]
md_maintainers = ["@ffpyt"]
md_credits = ["@rootwork"]
md_platforms = ["Linux"]


class UnicodeChar:
    """Container class for unicode characters"""

    def __init__(self, name: str, comment: str, code: str, block: str):
        self.name = name if name != '<control>' else comment
        self.comment = comment
        self.block = block
        self.code = code
        try:
            self.character = chr(int(code, 16))
        except (ValueError, OverflowError):
            warning(f"Invalid unicode code point: {code}")
            self.character = "?"

    def get_search_string(self) -> str:
        """Get the string that should be used in searches"""
        return ' '.join([self.character, self.code, self.name, self.comment])


def is_valid_char(char: UnicodeChar) -> bool:
    """Check if the character is valid"""
    # Skip surrogate pairs and other invalid/problematic characters
    code_int = int(char.code, 16)
    if 0xD800 <= code_int <= 0xDFFF:  # Surrogate pairs
        return False
    if code_int > 0x10FFFF:  # Beyond valid Unicode range
        return False

    # Skip characters that can't be properly displayed
    try:
        # Test if the character can be encoded/decoded properly
        _ = char.character.encode('utf-8').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        debug(f"Skipping invalid character U+{char.code}")
        return False

    return True


class SymbolQueryHandler(IndexQueryHandler):
    """Handles searching for Unicode symbols"""

    def __init__(self, character_list: List[UnicodeChar]):
        IndexQueryHandler.__init__(self)
        self.character_list = character_list

    def id(self) -> str:
        return md_name

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def defaultTrigger(self) -> str:
        """Default trigger keyword"""
        return "sym "

    def updateIndexItems(self):
        """Build the search index from character list"""
        index_items = []

        for char in self.character_list:
            if not is_valid_char(char):
                continue

            # Get HTML entity if available
            encoded = htmlentities.encode(char.character)
            has_html_entity = "&" in encoded

            # Build actions
            actions = []

            # Primary action: copy character
            actions.append(
                Action(
                    "copy_char",
                    "Copy symbol to clipboard",
                    lambda c=char.character: setClipboardText(c)
                )
            )

            # Secondary action: copy HTML entity if available
            if has_html_entity:
                actions.append(
                    Action(
                        "copy_html",
                        "Copy HTML entity to clipboard",
                        lambda html=encoded: setClipboardText(html)
                    )
                )

            # Build subtext
            subtext_parts = [char.block]
            if has_html_entity:
                subtext_parts.append(f"HTML: {encoded}")
            subtext_parts.append(f"Code: U+{char.code}")
            subtext = " • ".join(subtext_parts)

            # Create item
            item = StandardItem(
                id=f"unicode_{char.code}",
                text=f"{char.name.capitalize()} – {char.character}",
                subtext=subtext,
                icon_factory=lambda ch=char.character: Icon.grapheme(ch),
                actions=actions,
            )

            # Add to index with searchable string
            index_items.append(
                IndexItem(item=item, string=char.get_search_string())
            )

        self.setIndexItems(index_items)
        info(f"Indexed {len(index_items)} valid unicode characters")


class Plugin(PluginInstance):
    """Albert plugin to search and copy Unicode symbols"""

    def __init__(self):
        PluginInstance.__init__(self)

        # Load character table
        character_list = self._load_character_table()

        # Create the query handler with the loaded character list
        self.handler = SymbolQueryHandler(character_list)

    def _load_character_table(self) -> List[UnicodeChar]:
        """Read the data file and load to memory"""
        data_file = Path(__file__).parent / "unicode_list.txt"
        character_list = []

        if not data_file.exists():
            critical(f"Unicode data file not found: {data_file}")
            return character_list

        try:
            text = data_file.read_text(encoding="utf-8")

            for line in text.splitlines():
                line = line.strip()
                if line == "":
                    continue

                parts = line.split("\t")
                if len(parts) != 4:
                    continue

                name, comment, code, block = parts
                character = UnicodeChar(name, comment, code, block)
                character_list.append(character)

            info(f"Loaded {len(character_list)} unicode characters")
        except Exception as e:
            critical(f"Failed to load unicode data: {e}")

        return character_list

    def extensions(self):
        """Register the query handler as an extension"""
        return [self.handler]
