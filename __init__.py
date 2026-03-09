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


class Plugin(PluginInstance, IndexQueryHandler):
    """Albert plugin to search and copy Unicode symbols"""

    def __init__(self):
        PluginInstance.__init__(self)
        IndexQueryHandler.__init__(self)

        # Load character table
        self.character_list = self._load_character_table()  # type: List[UnicodeChar]

    def defaultTrigger(self):
        """Default trigger keyword"""
        return "sym "

    def extensions(self):
        """Register itself as extension as well (IndexQueryHandler mix-in class)"""
        return [self]

    def synopsis(self, query: str) -> str:
        """Returns input hint for the query"""
        # todo: check whether to remove when query isn't empty anymore
        return "Search unicode symbols by name, code, or character"

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

    def updateIndexItems(self):
        """Build the search index from character list"""
        index_items = []

        for char in self.character_list:
            if not is_valid_char(char):
                continue

            # Create icon using grapheme (character itself)
            def make_icon_factory(character):
                def make_icon():
                    return Icon.grapheme(character)
                return make_icon

            # Get HTML entity if available
            encoded = htmlentities.encode(char.character)
            has_html_entity = "&" in encoded

            # Build actions
            actions = []

            # Primary action: copy character
            def make_copy_char_action(character):
                def set_clipboard():
                    setClipboardText(character)
                return set_clipboard

            actions.append(
                Action(
                    "copy_char",
                    "Copy symbol to clipboard",
                    make_copy_char_action(char.character)
                )
            )

            # Secondary action: copy HTML entity if available
            if has_html_entity:
                def make_copy_html_action(html):
                    def copy_html():
                        setClipboardText(html)
                    return copy_html

                actions.append(
                    Action(
                        "copy_html",
                        "Copy HTML entity to clipboard",
                        make_copy_html_action(encoded)
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
                icon_factory=make_icon_factory(char.character),
                actions=actions,
            )

            # Add to index with searchable string
            index_items.append(
                IndexItem(item=item, string=char.get_search_string())
            )

        self.setIndexItems(index_items)