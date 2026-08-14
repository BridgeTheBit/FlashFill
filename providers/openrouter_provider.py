"""
OpenRouter provider — compatible with the OpenAI Chat Completions format.

Docs: https://openrouter.ai/docs/api-reference/overview
Endpoint: POST https://openrouter.ai/api/v1/chat/completions
Auth: Bearer token via Authorization header
"""

import json
import urllib.request
import urllib.error
from typing import Optional

from ..core.models import LanguageData
from .base import BaseLanguageProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Default model — user can override in config
DEFAULT_MODEL = "google/gemma-3-27b-it:free"

PROMPT_TEMPLATE = """\
You are a language learning assistant.
Provide the following information for the {source_lang} word or phrase '{word}'.
The translation should be in {target_lang}.

Respond ONLY with a valid JSON object using exactly these keys (use null if not applicable):
{{
  "translation": "Translation in {target_lang}",
  "english": "English translation",
  "pronunciation": "IPA pronunciation",
  "part_of_speech": "e.g. Noun, Verb, Phrase, Adjective",
  "gender": "Masculine / Feminine / Neuter, or null",
  "example": "A short example sentence in {source_lang}",
  "example_translation": "Translation of the example in {target_lang}",
  "cefr": "CEFR level A1–C2, or null",
  "notes": "Brief grammar or usage notes, or null"
}}
"""


class OpenRouterProvider(BaseLanguageProvider):
    def __init__(self, api_key: str = "", model: str = DEFAULT_MODEL):
        super().__init__(api_key=api_key)
        self.model = model or DEFAULT_MODEL

    def fetch_data(self, word: str, source_lang: str, target_lang: str) -> Optional[LanguageData]:
        if not self.api_key:
            raise ValueError("OpenRouter API key is missing in the configuration.")

        prompt = PROMPT_TEMPLATE.format(
            source_lang=source_lang,
            target_lang=target_lang,
            word=word,
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/anki-flashfill",
                "X-Title": "Anki FlashFill",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = json.loads(response.read().decode("utf-8"))

            text = raw["choices"][0]["message"]["content"]
            data = json.loads(text)

            return LanguageData(
                translation=data.get("translation"),
                english=data.get("english"),
                pronunciation=data.get("pronunciation"),
                part_of_speech=data.get("part_of_speech"),
                gender=data.get("gender"),
                example=data.get("example"),
                example_translation=data.get("example_translation"),
                cefr=data.get("cefr"),
                notes=data.get("notes"),
            )

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error(f"OpenRouter HTTP {e.code}: {body}")
            raise ConnectionError(f"OpenRouter API error {e.code}: {e.reason}\n{body}")

        except urllib.error.URLError as e:
            logger.error(f"OpenRouter network error: {e}")
            raise ConnectionError(f"Network error: {e}")

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"OpenRouter parse error: {e}")
            raise ValueError(f"Could not parse response from OpenRouter: {e}")
