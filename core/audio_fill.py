"""
Audio Fill — core logic for Stage 3.

Responsibilities:
  1. Pick the right audio provider from config.
  2. Resolve the source language name → BCP-47 code.
  3. Download MP3 bytes in background (called from autofill.py's QueryOp).
  4. Save the file to Anki's Media Collection.
  5. Return the Anki sound tag: [sound:filename.mp3]
"""

import os
import re
import tempfile
from typing import Optional

from aqt import mw
from ..utils.logger import get_logger

logger = get_logger(__name__)

# ── Language name → BCP-47 code ───────────────────────────────────────────────
LANG_TO_CODE: dict[str, str] = {
    "Spanish":    "es",
    "French":     "fr",
    "German":     "de",
    "Italian":    "it",
    "Portuguese": "pt",
    "Japanese":   "ja",
    "Korean":     "ko",
    "Chinese":    "zh-CN",
    "Arabic":     "ar",
    "Turkish":    "tr",
    "Persian":    "fa",
    "English":    "en",
    "Russian":    "ru",
    "Dutch":      "nl",
    "Polish":     "pl",
    "Hebrew":     "he",
    "Greek":      "el",
    "Swedish":    "sv",
    "Norwegian":  "no",
    "Danish":     "da",
    "Finnish":    "fi",
    "Czech":      "cs",
    "Romanian":   "ro",
    "Hungarian":  "hu",
    "Ukrainian":  "uk",
    "Hindi":      "hi",
    "Thai":       "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
}


def _safe_filename(word: str, lang_code: str) -> str:
    """
    Creates a deterministic, filesystem-safe filename for the audio file.

    Example:
        "mucho gusto", "es"  →  "autofill_es_mucho_gusto.mp3"
    """
    # Keep only alphanumerics, replace everything else with underscore
    safe = re.sub(r"[^a-zA-Z0-9]", "_", word.strip().lower())
    # Collapse multiple underscores and strip leading/trailing ones
    safe = re.sub(r"_+", "_", safe).strip("_")
    return f"autofill_{lang_code}_{safe}.mp3"


def get_audio_provider(config: dict):
    """
    Instantiates and returns the configured audio provider.

    Returns None if audio is disabled in config.
    """
    if not config.get("audio_enabled", True):
        logger.info("Audio is disabled in config — skipping.")
        return None

    provider_type = config.get("audio_provider", "gtts").lower()

    if provider_type == "mock":
        from ..providers.audio.mock_audio import MockAudioProvider
        return MockAudioProvider()

    if provider_type == "gtts":
        from ..providers.audio.gtts_provider import GTTSProvider
        return GTTSProvider()

    logger.warning(f"Unknown audio provider '{provider_type}' — defaulting to gtts.")
    from ..providers.audio.gtts_provider import GTTSProvider
    return GTTSProvider()


def perform_audio_fill(word: str, source_lang: str, config: dict) -> Optional[str]:
    """
    Downloads pronunciation audio, saves it to Anki Media, and returns the
    Anki sound tag to embed in the note field.

    This function is meant to be called from inside a background thread
    (e.g. QueryOp), NOT from the main UI thread.

    Args:
        word:        The word or phrase to pronounce.
        source_lang: Human-readable language name (e.g. 'Spanish').
        config:      The add-on config dict.

    Returns:
        A string like "[sound:autofill_es_mucho_gusto.mp3]" on success,
        or None if audio is disabled, unsupported, or download failed.
    """
    # ── Resolve language code ─────────────────────────────────────────────────
    lang_code = LANG_TO_CODE.get(source_lang)
    if not lang_code:
        logger.warning(
            f"perform_audio_fill: no BCP-47 code for language '{source_lang}'. "
            f"Supported: {list(LANG_TO_CODE.keys())}"
        )
        return None

    # ── Get provider ──────────────────────────────────────────────────────────
    provider = get_audio_provider(config)
    if provider is None:
        return None   # audio disabled

    # ── Fetch audio bytes ─────────────────────────────────────────────────────
    audio_data: Optional[bytes] = provider.fetch_audio(word, lang_code)
    if not audio_data:
        logger.warning(f"perform_audio_fill: provider returned no data for '{word}'")
        return None

    # ── Save to temp file ─────────────────────────────────────────────────────
    filename = _safe_filename(word, lang_code)
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    try:
        with open(tmp_path, "wb") as fh:
            fh.write(audio_data)
        logger.info(f"perform_audio_fill: wrote {len(audio_data)} bytes to {tmp_path}")
    except OSError as e:
        logger.error(f"perform_audio_fill: could not write temp file: {e}")
        return None

    # ── Add to Anki Media Collection ──────────────────────────────────────────
    try:
        final_name = mw.col.media.add_file(tmp_path)
        logger.info(f"perform_audio_fill: added to Anki Media as '{final_name}'")
    except Exception as e:
        logger.error(f"perform_audio_fill: mw.col.media.add_file failed: {e}")
        return None
    finally:
        # Always clean up the temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return f"[sound:{final_name}]"
