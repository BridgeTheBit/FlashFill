import json
import urllib.request
import urllib.error
from typing import Optional
from ..core.models import LanguageData
from .base import BaseLanguageProvider
from ..utils.logger import get_logger

logger = get_logger(__name__)

class GeminiProvider(BaseLanguageProvider):
    def fetch_data(self, word: str, source_lang: str, target_lang: str) -> Optional[LanguageData]:
        if not self.api_key:
            raise ValueError("Gemini API key is missing in the configuration.")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        prompt = f"""
        You are a language learning assistant. Provide the following information for the {source_lang} word or phrase '{word}'.
        The translation should be in {target_lang}.
        Respond ONLY with a valid JSON object matching this structure (use null if a field is not applicable):
        {{
            "translation": "Translation in {target_lang}",
            "english": "English translation",
            "pronunciation": "IPA pronunciation",
            "part_of_speech": "Part of speech (e.g. Noun, Verb, Phrase)",
            "gender": "Gender (if applicable, e.g. Masculine, Feminine)",
            "example": "A short example sentence in {source_lang}",
            "example_translation": "Translation of the example in {target_lang}",
            "cefr": "CEFR level (A1-C2)",
            "notes": "Any brief grammar or usage notes"
        }}
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                try:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    parsed_json = json.loads(text_response)
                    
                    return LanguageData(
                        translation=parsed_json.get("translation"),
                        english=parsed_json.get("english"),
                        pronunciation=parsed_json.get("pronunciation"),
                        part_of_speech=parsed_json.get("part_of_speech"),
                        gender=parsed_json.get("gender"),
                        example=parsed_json.get("example"),
                        example_translation=parsed_json.get("example_translation"),
                        cefr=parsed_json.get("cefr"),
                        notes=parsed_json.get("notes")
                    )
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    logger.error(f"Failed to parse Gemini response: {e}\nResponse: {result}")
                    raise ValueError(f"Failed to parse response from Gemini: {e}")
                    
        except urllib.error.URLError as e:
            logger.error(f"Network error when calling Gemini API: {e}")
            raise ConnectionError(f"Network or Proxy error: {e}")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"HTTP error {e.code}: {error_body}")
            raise ConnectionError(f"API Error {e.code}: {e.reason}")
