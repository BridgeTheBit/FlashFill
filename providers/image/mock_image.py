"""
Mock Image Provider — for testing without network access.

Generates a small solid-color PNG programmatically using only
Python stdlib (struct + zlib). No external dependencies needed.
The resulting 60×60 cornflower-blue square is easy to recognise
as a placeholder when inspecting Anki cards.
"""

import struct
import time
import zlib
from typing import Optional

from .base import BaseImageProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)


def _make_png(width: int = 60, height: int = 60,
              r: int = 100, g: int = 149, b: int = 237) -> bytes:
    """
    Build a minimal solid-color RGB PNG using only stdlib.

    PNG structure:
        signature  (8 bytes)
        IHDR chunk (25 bytes: 4 len + 4 type + 13 data + 4 CRC)
        IDAT chunk (variable: zlib-compressed scanlines)
        IEND chunk (12 bytes)

    Each scanline: filter_byte(0x00) + R G B × width
    """

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        payload = chunk_type + data
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + payload + struct.pack(">I", crc)

    # ── IHDR ──────────────────────────────────────────────────────────────────
    # width(4), height(4), bit_depth(1), color_type(1)=2(RGB),
    # compression(1)=0, filter(1)=0, interlace(1)=0
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    # ── IDAT ──────────────────────────────────────────────────────────────────
    # Each scanline: filter byte 0 (None) followed by RGB pixels
    scanline = b"\x00" + bytes([r, g, b] * width)
    raw_image = scanline * height
    idat_data = zlib.compress(raw_image, level=1)

    return (
        b"\x89PNG\r\n\x1a\n"          # PNG signature
        + make_chunk(b"IHDR", ihdr_data)
        + make_chunk(b"IDAT", idat_data)
        + make_chunk(b"IEND", b"")
    )


# Pre-generate once at import time to avoid repeated work
_MOCK_PNG: bytes = _make_png(60, 60, r=100, g=149, b=237)  # cornflower blue


class MockImageProvider(BaseImageProvider):
    """
    Returns a 60×60 cornflower-blue PNG placeholder.
    Works completely offline — no network access required.
    """

    def search_image(self, query: str) -> Optional[bytes]:
        logger.info(
            f"MockImageProvider: returning placeholder PNG for query '{query}'"
        )
        time.sleep(0.3)   # simulate slight network latency
        return _MOCK_PNG
