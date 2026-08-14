"""
Google Translate TTS Provider (unofficial public endpoint).

No API key is required.
Endpoint: https://translate.google.com/translate_tts
Returns:  MP3 audio data.

Note: This endpoint is unofficial and not guaranteed by Google.
      It is rate-limited per IP; for heavy use consider a paid TTS API.
"""

import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

from .base import BaseAudioProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

# Google Translate TTS endpoint
_TTS_URL = "https://translate.google.com/translate_tts"

# Realistic browser User-Agent to avoid 403 blocks
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class GTTSProvider(BaseAudioProvider):
    """
    Uses Google Translate's public TTS endpoint.

    Supports all languages covered by Google Translate.
    No registration or API key needed.
    """

    def fetch_audio(self, word: str, lang_code: str) -> Optional[bytes]:
        """
        Downloads MP3 pronunciation from Google Translate TTS.

        Args:
            word:      The word or phrase to pronounce.
            lang_code: BCP-47 language code, e.g. 'es', 'fr', 'ja'.

        Returns:
            Raw MP3 bytes, or None if the response is empty.

        Raises:
            ConnectionError: On HTTP or network error.
        """
        params = urllib.parse.urlencode({
            "ie":     "UTF-8",
            "q":      word,
            "tl":     lang_code,
            "client": "tw-ob",   # public client id used by Google Translate web
            "ttsspeed": "1",     # normal speed (0.5 = slow)
        })
        url = f"{_TTS_URL}?{params}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _USER_AGENT,
                "Referer":    "https://translate.google.com/",
                "Accept":     "audio/mpeg, audio/*;q=0.9",
            },
        )

        logger.info(f"GTTSProvider: fetching audio for '{word}' ({lang_code})")

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                data = response.read()

            if not data:
                logger.warning(f"GTTSProvider: empty response for '{word}'")
                return None

            logger.info(
                f"GTTSProvider: received {len(data)} bytes for '{word}' ({lang_code})"
            )
            return data

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"GTTSProvider HTTP {e.code}: {body[:200]}")
            raise ConnectionError(
                f"Google TTS returned HTTP {e.code}: {e.reason}\n"
                f"This may be a temporary rate-limit. Try again later."
            )

        except urllib.error.URLError as e:
            logger.error(f"GTTSProvider network error: {e}")
            raise ConnectionError(f"Network error while fetching audio: {e}")
