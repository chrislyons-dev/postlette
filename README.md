# Postlette

A tiny desktop editor that adds Unicode emphasis for social posts.

Postlette uses Unicode characters, not rich text formatting. Type your post, style selected text with bold or italic, insert separators, and copy the result. Platforms may render these characters differently.

Rendering varies by platform.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/chrislyons-dev/postlette.git
cd postlette
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
python main.py
```

1. Type or paste your post into the editor.
2. Select text and apply styling (Bold, Italic, etc.) from the toolbar.
3. Insert em dashes or separators at the cursor.
4. Click **Copy** (or press `Ctrl+Shift+C`) to copy the result to your clipboard.

Use styling sparingly for readability.

## Test

```bash
python tasks.py test
```

## Lint

```bash
python tasks.py lint    # check
python tasks.py fix     # auto-fix
```

## Build

Standalone executables are built with PyInstaller. Each OS requires its own build.

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name postlette main.py
```

The executable will be in `dist/postlette.exe`.

### macOS

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name postlette main.py
```

The app bundle will be in `dist/postlette.app`.

**Note:** Distributing on macOS may require codesigning and notarization.

## License

MIT
