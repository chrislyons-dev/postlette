"""Unicode Mathematical style transforms for Postlette."""

# Unicode Mathematical Bold offsets
# A-Z → U+1D400..U+1D419, a-z → U+1D41A..U+1D433, 0-9 → U+1D7CE..U+1D7D7
_BOLD_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _BOLD_MAP[_c] = chr(0x1D400 + _i)
for _i in range(10):
    _BOLD_MAP[str(_i)] = chr(0x1D7CE + _i)


def apply_bold(text: str) -> str:
    """Map A-Z, a-z, 0-9 to Unicode Mathematical Bold. Leave everything else unchanged."""
    return "".join(_BOLD_MAP.get(c, c) for c in text)


# Unicode Mathematical Italic offsets (letters only — no reliable italic digit set)
# A-Z → U+1D434..U+1D44D, a-z → U+1D44E..U+1D467
# Exception: italic 'h' is U+210E (PLANCK CONSTANT), not U+1D455 (unassigned).
_ITALIC_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _ITALIC_MAP[_c] = chr(0x1D434 + _i)
_ITALIC_MAP["h"] = "\u210e"

# Unicode Mathematical Bold-Italic offsets (letters only)
# A-Z → U+1D468..U+1D481, a-z → U+1D482..U+1D49B
_BOLD_ITALIC_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _BOLD_ITALIC_MAP[_c] = chr(0x1D468 + _i)


def apply_italic(text: str) -> str:
    """Map A-Z, a-z to Unicode Mathematical Italic. Leave everything else unchanged."""
    return "".join(_ITALIC_MAP.get(c, c) for c in text)


def apply_bold_italic(text: str) -> str:
    """Map A-Z, a-z to Unicode Mathematical Bold-Italic. Leave everything else unchanged."""
    return "".join(_BOLD_ITALIC_MAP.get(c, c) for c in text)


# Reverse map: styled Unicode char → original ASCII. Built from all style maps
# so unstyle works regardless of which style was applied.
_UNSTYLE_MAP: dict[str, str] = {}
for _style_map in (_BOLD_MAP, _ITALIC_MAP, _BOLD_ITALIC_MAP):
    for _ascii, _styled in _style_map.items():
        _UNSTYLE_MAP[_styled] = _ascii


def apply_unstyle(text: str) -> str:
    """Revert any Postlette-styled characters back to ASCII. Leave everything else unchanged."""
    return "".join(_UNSTYLE_MAP.get(c, c) for c in text)
