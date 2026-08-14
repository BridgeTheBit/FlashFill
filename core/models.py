from dataclasses import dataclass
from typing import Optional

@dataclass
class LanguageData:
    translation: Optional[str] = None
    english: Optional[str] = None
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None
    gender: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None
    cefr: Optional[str] = None
    notes: Optional[str] = None
