from abc import ABC, abstractmethod
from typing import Optional
from ..core.models import LanguageData

class BaseLanguageProvider(ABC):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        
    @abstractmethod
    def fetch_data(self, word: str, source_lang: str, target_lang: str) -> Optional[LanguageData]:
        """
        Fetches language information for a given word.
        
        Args:
            word: The word or phrase to look up.
            source_lang: The language of the word (e.g. 'Spanish').
            target_lang: The target language for translations (e.g. 'Persian').
            
        Returns:
            LanguageData object containing the parsed information, or None if failed.
        """
        pass
