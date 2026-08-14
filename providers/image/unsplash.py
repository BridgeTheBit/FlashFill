"""
Unsplash Image Provider.

API Docs : https://unsplash.com/documentation#search-photos
Endpoint : GET https://api.unsplash.com/search/photos
Auth     : Authorization: Client-ID {access_key}
Free plan: 50 requests / hour.

How to get a free key:
  1. Go to https://unsplash.com/developers
  2. Create a new application
  3. Copy the "Access Key"
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

_SEARCH_URL = "https://api.unsplash.com/search/photos"
_USER_AGENT = "AnkiLanguageAutoFill/1.0 (https://github.com/anki-language-autofill)"


class UnsplashProvider(BaseImageProvider):
    """
    Fetches a contextually relevant photo from Unsplash.

    Two-step process:
      1. Search the Unsplash API → get photo metadata (URL, attribution).
      2. Download the "small" variant (~400 px wide) — ideal for Anki cards.
    """

    def search_image(self, query: str) -> Optional[bytes]:
        if not self.api_key:
            raise ValueError(
                "Unsplash Access Key is missing.\n"
                "Get a free key at: https://unsplash.com/developers\n"
                "Then paste it in Settings → Image → API Key."
            )

        # ── Step 1: Search ──────────────────────────────────────────────────
        params = urllib.parse.urlencode({
            "query":       query,
            "per_page":    1,
            "orientation": "squarish",   # square images look best on cards
        })
        req = urllib.request.Request(
            f"{_SEARCH_URL}?{params}",
            headers={
                "Authorization": f"Client-ID {self.api_key}",
                "Accept-Version": "v1",
                "User-Agent": _USER_AGENT,
            },
        )

        logger.info(f"UnsplashProvider: searching for '{query}'")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Unsplash search HTTP {e.code}: {body[:300]}")
            raise ConnectionError(
                f"Unsplash API error {e.code}: {e.reason}\n"
                f"Check your Access Key in Settings → Image."
            )
        except urllib.error.URLError as e:
            logger.error(f"Unsplash network error: {e}")
            raise ConnectionError(f"Network error searching Unsplash: {e}")

        results = data.get("results", [])
        if not results:
            logger.warning(f"UnsplashProvider: no results for '{query}'")
            return None

        # ── Step 2: Download ────────────────────────────────────────────────
        # "small" = ~400 px wide, good quality for Anki without huge file size
        image_url = results[0]["urls"]["small"]
        logger.info(f"UnsplashProvider: downloading image from {image_url[:70]}…")

        try:
            img_req = urllib.request.Request(
                image_url, headers={"User-Agent": _USER_AGENT}
            )
            with urllib.request.urlopen(img_req, timeout=25) as resp:
                image_bytes = resp.read()
        except urllib.error.URLError as e:
            logger.error(f"Unsplash image download error: {e}")
            raise ConnectionError(f"Failed to download Unsplash image: {e}")

        logger.info(
            f"UnsplashProvider: downloaded {len(image_bytes):,} bytes for '{query}'"
        )
        return image_bytes
