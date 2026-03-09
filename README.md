# albert-plugin-python-symbol

> An [Albert](https://albertlauncher.github.io/) plugin for searching Unicode and ASCII characters

Search and copy Unicode symbols to your clipboard. Find characters using their name, description, Unicode block names, or the characters themselves.

## Features

- 🔍 **Comprehensive Search** - Search by character name, description, Unicode block, code point, or the character itself
- 📋 **Quick Copy** - Press <kbd>Enter</kbd> to copy the symbol to clipboard
- 🌐 **HTML Entity Support** - Select "Copy HTML entity" action for HTML-compatible entities (e.g., `&copy;`, `&hearts;`)
- ⚡ **Fast Indexing** - Uses Albert's native indexing for instant results
- 🎨 **Visual Icons** - Character displayed as icon for easy identification

## Usage

1. Type the trigger keyword `sym<space>` (or your custom trigger) in Albert
2. Enter your search query (e.g., "arrow", "U+2764", "heart", "©")
3. Press <kbd>Enter</kbd> to copy the symbol to clipboard
4. Or select "Copy HTML entity to clipboard" for the HTML version (when available)

By default the query

### Usage Examples

- `sym heart` - Find heart symbols
- `sym arrow right` - Find right-pointing arrows  
- `sym copyright` - Find copyright symbol
- `sym 263A` - Search by Unicode code point
- `sym ♥` - Search by the character itself

## Installation

### Requirements

This plugin requires the `htmlentities` Python package to provide HTML entity conversion.

### Install Steps

1. **Install the htmlentities package in Albert's virtual environment:**

```bash
# Activate Albert's virtual environment
source ~/.local/share/albert/python/venv/bin/activate

# Install htmlentities in Albert's venv
pip install htmlentities

# Deactivate the venv
deactivate
```

2. Git clone this repository into your Albert plugins directory:

```bash
git clone https://github.com/ffpyt/albert-plugin-python-symbol.git ~/.local/share/albert/python/plugins/symbol
```

3. **Restart Albert**
4. **Enable the plugin:**
    - Open Albert settings
    - Go to **Plugins** → **Python** → **Unicode Symbols**
    - Enable the plugin
    - Review configuration in Query tab:
      - Customize the trigger keyword (default: `sym<default>`)
      - Disable global query handling to prevent symbols from showing in the search results w/o prior trigger keyword
      - Enable fuzzy matching for symbols (not recommended) 

## Technical Details

- **Plugin Type:** IndexQueryHandler (indexed search for fast results)
- **Python API:** Albert v5.0
- **Python package dependencies:** `htmlentities`
- **Data Source:** (included) `unicode_list.txt`

## Credits

- This is a port of the [ulauncher-symbol](https://github.com/rootwork/ulauncher-symbol) extension by [@rootwork](https://github.com/rootwork) adapted to [Albert launcher](https://albertlauncher.github.io/)
- [rootworks's ulauncher-symbol](https://github.com/rootwork/ulauncher-symbol) was forked from [ulauncher-unicode](https://github.com/zensoup/ulauncher-unicode) by [@zensoup](https://github.com/zensoup)

## License
GPL-3.0. See [LICENCE](LICENCE)
