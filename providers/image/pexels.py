"""
Pexels Image Provider.

API Docs : https://www.pexels.com/api/documentation/#photos-search
Endpoint : GET https://api.pexels.com/v1/search
Auth     : Authorization: {api_key}
Free plan: 200 requests / hour, 20 000 requests / month.

How to get a free key:
  1. Go to https://www.pexels.com/api/
  2. Sign up / log in
  3. Request access → copy your API key
  4. Paste it in Anki → Tools → FlashFill Settings → Image tab
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

from .base import BaseImageProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

_SEARCH_URL = "https://api.pexels.com/v1/search"
_USER_AGENT = "AnkiLanguageAutoFill/1.0 (https://github.com/anki-language-autofill)"


class PexelsProvider(BaseImageProvider):
    """
    Fetches a contextually relevant photo from Pexels.

    Two-step process:
      1. Search the Pexels API → get photo metadata.
      2. Download the "medium" size variant (~1200 px wide).
         If you prefer smaller files, change "medium" to "small" (~350 px).
    """

    def search_image(self, query: str) -> Optional[bytes]:
        if not self.api_key:
            raise ValueError(
                "Pexels API Key is missing.\n"
                "Get a free key at: https://www.pexels.com/api/\n"
                "Then paste it in Settings → Image → API Key."
            )

        # ── Step 1: Search ──────────────────────────────────────────────────
        params = urllib.parse.urlencode({
            "query":    query,
            "per_page": 1,
            "size":     "medium",
        })
        req = urllib.request.Request(
            f"{_SEARCH_URL}?{params}",
            headers={
                "Authorization": self.api_key,
                "User-Agent":    _USER_AGENT,
            },
        )

        logger.info(f"PexelsProvider: searching for '{query}'")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Pexels search HTTP {e.code}: {body[:300]}")
            raise ConnectionError(
                f"Pexels API error {e.code}: {e.reason}\n"
                f"Check your API Key in Settings → Image."
            )
        except urllib.error.URLError as e:
            logger.error(f"Pexels network error: {e}")
            raise ConnectionError(f"Network error searching Pexels: {e}")

        photos = data.get("photos", [])
        if not photos:
            logger.warning(f"PexelsProvider: no results for '{query}'")
            return None

        # ── Step 2: Download ────────────────────────────────────────────────
        # "medium" ~1200 px; use "small" (~350 px) if you want smaller files
        image_url = photos[0]["src"]["medium"]
        logger.info(f"PexelsProvider: downloading image from {image_url[:70]}…")

        try:
            img_req = urllib.request.Request(
                image_url, headers={"User-Agent": _USER_AGENT}
            )
            with urllib.request.urlopen(img_req, timeout=25) as resp:
                image_bytes = resp.read()
        except urllib.error.URLError as e:
            logger.error(f"Pexels image download error: {e}")
            raise ConnectionError(f"Failed to download Pexels image: {e}")

        logger.info(
            f"PexelsProvider: downloaded {len(image_bytes):,} bytes for '{query}'"
        )
        return image_bytes
