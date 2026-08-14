"""
Image Fill — core logic for Stage 2.

Flow (runs entirely in a background thread via QueryOp):
  1. Generate an English image search query from the word + LanguageData.
  2. Select the configured image provider.
  3. Download raw image bytes.
  4. Detect file type (JPEG / PNG) from magic bytes.
  5. Write to a temp file → add_file() into Anki Media Collection.
  6. Return an HTML <img src="filename"> tag to put in the note field.
"""

import os
import re
import struct
import tempfile
from typing import Optional

from aqt import mw
from ..utils.logger import get_logger

logger = get_logger(__name__)


# ── Image search query generation ─────────────────────────────────────────────

def _generate_image_query(word: str, lang_data) -> str:
    """
    Creates a descriptive English search query for the image provider.

    Strategy:
      • Use the English translation of the word as the base.
      • Adjust phrasing based on part of speech for more relevant results.

    Examples:
      perro      (Noun)   english="dog"           → "dog"
      comer      (Verb)   english="to eat"        → "person eating"
      mucho gusto(Phrase) english="Nice to meet"  → "Nice to meet you two people greeting"
    """
    if lang_data is None:
        return word

    english = (lang_data.english or word).strip()
    # Strip "to " prefix that LLMs commonly prepend to Spanish/French verbs
    base = english[3:] if english.lower().startswith("to ") else english

    pos = (lang_data.part_of_speech or "").lower()

    if "verb" in pos:
        # Gerund form is more image-searchable than infinitive
        query = f"person {base}ing"
    elif any(p in pos for p in ("phrase", "expression", "idiom", "interjection")):
        # Phrases: keep full English, add context
        query = f"{english} two people"
    else:
        # Noun, adjective, adverb, etc.
        query = base

    logger.info(f"Image query for '{word}' (pos={pos or 'unknown'}): '{query}'")
    return query


# ── File-type detection ────────────────────────────────────────────────────────

def _detect_extension(data: bytes, fallback_url: str = "") -> str:
    """Detect the image format from magic bytes, falling back to URL hints."""
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:4] == b"GIF8":
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    # Fallback: scan the URL for a recognisable extension
    for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        if ext in fallback_url.lower():
            return ext
    return ".jpg"    # safe default — most images are JPEG


# ── Filename helper ────────────────────────────────────────────────────────────

def _safe_filename(word: str, extension: str) -> str:
    """
    Creates a deterministic, filesystem-safe filename.

    Example: "mucho gusto", ".jpg"  →  "autofill_img_mucho_gusto.jpg"
    """
    safe = re.sub(r"[^a-zA-Z0-9]", "_", word.strip().lower())
    safe = re.sub(r"_+", "_", safe).strip("_")
    return f"autofill_img_{safe}{extension}"


# ── Provider factory ───────────────────────────────────────────────────────────

def get_image_provider(config: dict):
    """
    Instantiates the configured image provider.
    Returns None if image filling is disabled.
    """
    if not config.get("image_enabled", True):
        logger.info("Image fill is disabled in config — skipping.")
        return None

    provider_type = config.get("image_provider", "mock").lower()
    api_key = config.get("image_api_key", "")

    if provider_type == "mock":
        from ..providers.image.mock_image import MockImageProvider
        return MockImageProvider()

    if provider_type == "unsplash":
        from ..providers.image.unsplash import UnsplashProvider
        return UnsplashProvider(api_key=api_key)

    if provider_type == "pexels":
        from ..providers.image.pexels import PexelsProvider
        return PexelsProvider(api_key=api_key)

    logger.warning(
        f"Unknown image provider '{provider_type}' — defaulting to mock."
    )
    from ..providers.image.mock_image import MockImageProvider
    return MockImageProvider()


# ── Main function ──────────────────────────────────────────────────────────────

def perform_image_fill(word: str, lang_data, config: dict) -> Optional[str]:
    """
    Downloads a relevant image, saves it to Anki Media, and returns
    an HTML <img> tag ready to put inside a note field.

    Must be called from a background thread (QueryOp), NOT the UI thread.

    Args:
        word:      The source word or phrase (e.g. "mucho gusto").
        lang_data: LanguageData from Stage 1 — used to build a better query.
                   May be None if Stage 1 failed.
        config:    Add-on config dict.

    Returns:
        HTML string '<img src="autofill_img_mucho_gusto.jpg">' on success,
        or None if image fill is disabled, no image found, or download failed.
    """
    provider = get_image_provider(config)
    if provider is None:
        return None

    query = _generate_image_query(word, lang_data)

    image_data: Optional[bytes] = provider.search_image(query)
    if not image_data:
        logger.warning(
            f"perform_image_fill: provider returned no data for query '{query}'"
        )
        return None

    # ── Determine file type ───────────────────────────────────────────────────
    ext = _detect_extension(image_data)
    filename = _safe_filename(word, ext)

    # ── Write to temp file ────────────────────────────────────────────────────
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(tmp_path, "wb") as fh:
            fh.write(image_data)
        logger.info(
            f"perform_image_fill: wrote {len(image_data):,} bytes to {tmp_path}"
        )
    except OSError as e:
        logger.error(f"perform_image_fill: could not write temp file: {e}")
        return None

    # ── Add to Anki Media Collection ──────────────────────────────────────────
    try:
        final_name = mw.col.media.add_file(tmp_path)
        logger.info(
            f"perform_image_fill: added to Anki Media as '{final_name}'"
        )
    except Exception as e:
        logger.error(f"perform_image_fill: mw.col.media.add_file failed: {e}")
        return None
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return f'<img src="{final_name}">'
