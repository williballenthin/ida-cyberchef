"""Parse various input formats into bytes."""

import base64
from enum import Enum
from typing import Optional


class InputFormat(Enum):
    """Supported input format types."""

    TEXT_UTF8 = "text_utf8"
    HEX_STRING = "hex_string"
    BASE64 = "base64"


class InputParser:
    """Parse text input into bytes based on format."""

    def parse(self, text: str, format: InputFormat) -> Optional[bytes]:
        """Parse text input into bytes.

        Args:
            text: Input text
            format: Format type

        Returns: Parsed bytes, or None if parsing fails
        """
        try:
            if format == InputFormat.TEXT_UTF8:
                return text.encode("utf-8")

            elif format == InputFormat.HEX_STRING:
                hex_str = text.replace(" ", "").replace(":", "").replace("-", "")
                return bytes.fromhex(hex_str)

            elif format == InputFormat.BASE64:
                return base64.b64decode(text)

        except Exception:
            return None
