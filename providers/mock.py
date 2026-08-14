"""
Mock Language Provider — for offline testing without any API key.

Returns generic placeholder data that makes the full pipeline testable:
  Auto Fill → Preview → Audio → Image → Apply to Note

The mock is language-agnostic: it uses the actual source_lang and target_lang
from config to build realistic-looking placeholder strings.
"""

import time
from typing import Optional
from ..core.models import LanguageData
from .base import BaseLanguageProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MockProvider(BaseLanguageProvider):
    def fetch_data(
        self, word: str, source_lang: str, target_lang: str
    ) -> Optional[LanguageData]:
        logger.info(
            f"MockProvider: '{word}' ({source_lang} → {target_lang})"
        )
        time.sleep(1.0)  # simulate network latency

        return LanguageData(
            translation=f"[{target_lang} translation of '{word}']",
            english=f"[English meaning of '{word}']",
            pronunciation=f"/mock-ipa-{word.lower().replace(' ', '-')}/",
            part_of_speech="Noun",
            gender=None,
            example=f"This is a mock example sentence with '{word}'.",
            example_translation=f"[{target_lang} translation of the example sentence.]",
            cefr="A1",
            notes=(
                f"Mock data — switch to 'gemini' or 'openrouter' in "
                f"FlashFill Settings for real {source_lang} → {target_lang} results."
            ),
        )
