"""
In-memory session cache for Auto Fill results.

Cache keys = (word, source_lang, target_lang).
Cache is NOT persisted across Anki sessions — intentional, so data stays fresh.

Cached value: the complete _fetch_all() result tuple:
    (LanguageData | None, audio_tag | None, image_html | None)
"""

from typing import Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Module-level dict — persists for the lifetime of the Anki process
_cache: dict = {}


def _key(word: str, source_lang: str, target_lang: str) -> str:
    """Normalised, case-insensitive cache key."""
    return f"{word.strip().lower()}|{source_lang}|{target_lang}"


def get(word: str, source_lang: str, target_lang: str) -> Optional[tuple]:
    """Return cached result tuple, or None if not in cache."""
    result = _cache.get(_key(word, source_lang, target_lang))
    if result is not None:
        logger.info(f"Cache HIT  '{word}' ({source_lang} → {target_lang})")
    return result


def put(word: str, source_lang: str, target_lang: str, data: tuple) -> None:
    """Store a fetch result in the cache."""
    _cache[_key(word, source_lang, target_lang)] = data
    logger.info(
        f"Cache STORE  '{word}' ({source_lang} → {target_lang})  "
        f"[total: {len(_cache)}]"
    )


def clear() -> int:
    """Clear all entries. Returns the count of removed entries."""
    count = len(_cache)
    _cache.clear()
    logger.info(f"Cache cleared — {count} entries removed")
    return count


def size() -> int:
    """Return the number of currently cached entries."""
    return len(_cache)
