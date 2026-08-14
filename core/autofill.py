"""
FlashFill — Core Auto Fill logic.

Stage 1 (language data) + Stage 2 (image) + Stage 3 (audio) + Cache + Preview.

Background thread flow:
    perform_autofill()
        └─ QueryOp.run_in_background()
               └─ _fetch_all()              ← background thread
                    ├─ cache check          Stage 0: return cached result if available
                    ├─ fetch_data()         Stage 1: language data (required)
                    ├─ audio_fill()         Stage 3: TTS audio  (non-fatal)
                    └─ image_fill()         Stage 2: image      (non-fatal, uses Stage 1)
               └─ on_autofill_success()     ← main thread
                    └─ if preview_enabled → PreviewDialog.exec()
                                └─ _apply_to_note() on Apply
                    └─ else → _apply_to_note() directly
"""

import re
from typing import Optional, Tuple

from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import showWarning, tooltip

from ..providers.mock import MockProvider
from ..providers.gemini_provider import GeminiProvider
from ..providers.openrouter_provider import OpenRouterProvider
from .models import LanguageData
from .audio_fill import perform_audio_fill
from .image_fill import perform_image_fill
from ..utils.logger import get_logger

logger = get_logger(__name__)

_ADDON_PACKAGE = __name__.split(".")[0]


# ── Config helper ──────────────────────────────────────────────────────────────

def _get_config() -> dict:
    cfg = mw.addonManager.getConfig(_ADDON_PACKAGE)
    if cfg is None:
        logger.warning("Config not found – using defaults.")
        cfg = {}
    return cfg


# ── Language provider factory ──────────────────────────────────────────────────

def get_provider(config: Optional[dict] = None):
    if config is None:
        config = _get_config()
    provider_type = config.get("provider", "mock").lower()
    api_key       = config.get("api_key", "")
    logger.info(f"Using language provider: '{provider_type}'")

    if provider_type == "gemini":
        return GeminiProvider(api_key=api_key)
    if provider_type == "openrouter":
        return OpenRouterProvider(api_key=api_key, model=config.get("openrouter_model", ""))
    return MockProvider()


# ── Utility ────────────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    """Remove HTML tags that Anki stores inside field values."""
    return re.sub(r"<[^>]+>", "", text).strip()


# ── Background worker ──────────────────────────────────────────────────────────

def _fetch_all(
    _col,
    word: str,
    source_lang: str,
    target_lang: str,
    config: dict,
) -> Tuple[Optional[LanguageData], Optional[str], Optional[str]]:
    """
    Runs entirely in a background thread (via QueryOp).

    Returns:
        (LanguageData | None, audio_sound_tag | None, image_html | None)

    Stage 2 and Stage 3 failures are non-fatal — logged and skipped.
    Results are cached to avoid repeat API calls for the same word.
    Image runs after Stage 1 to use the English translation as a better query.
    """
    from .cache import get as cache_get, put as cache_put

    # ── Stage 0: Cache ──────────────────────────────────────────────────────
    cached = cache_get(word, source_lang, target_lang)
    if cached is not None:
        return cached

    # ── Stage 1: Language data (required) ───────────────────────────────────
    provider = get_provider(config)
    lang_data: Optional[LanguageData] = provider.fetch_data(
        word, source_lang, target_lang
    )

    # ── Stage 3: Audio (optional, non-fatal) ────────────────────────────────
    audio_tag: Optional[str] = None
    try:
        audio_tag = perform_audio_fill(word, source_lang, config)
    except Exception as exc:
        logger.warning(
            f"Audio fetch failed (non-fatal) for '{word}': "
            f"{type(exc).__name__}: {exc}"
        )

    # ── Stage 2: Image (optional, non-fatal, uses Stage 1 data) ─────────────
    image_html: Optional[str] = None
    try:
        image_html = perform_image_fill(word, lang_data, config)
    except Exception as exc:
        logger.warning(
            f"Image fetch failed (non-fatal) for '{word}': "
            f"{type(exc).__name__}: {exc}"
        )

    result = (lang_data, audio_tag, image_html)

    # Cache only when language data was successfully retrieved
    if lang_data is not None:
        cache_put(word, source_lang, target_lang, result)

    return result


# ── Apply to note ──────────────────────────────────────────────────────────────

def _apply_to_note(
    editor,
    lang_data: Optional[LanguageData],
    audio_tag: Optional[str],
    image_html: Optional[str],
    config: dict,
) -> None:
    """
    Writes all fetched data to the current note.
    Only fills EMPTY fields — never overwrites existing content.

    Called from:
      • PreviewDialog.Apply button (with preview enabled)
      • on_autofill_success() directly (with preview disabled)
    """
    if lang_data is None:
        return

    note = editor.note
    field_mapping = config.get("field_mapping", {})
    updated: list[str] = []

    # Stage 1 — language data fields
    for data_key, note_field in field_mapping.items():
        if not note_field or note_field not in note:
            continue
        value = getattr(lang_data, data_key, None)
        if not value:
            continue
        if not _strip_html(note[note_field]):
            note[note_field] = value
            updated.append(note_field)

    # Stage 3 — audio
    if audio_tag:
        audio_field = config.get("audio_field", "Audio")
        if audio_field and audio_field in note:
            if not _strip_html(note[audio_field]):
                note[audio_field] = audio_tag
                updated.append(audio_field)

    # Stage 2 — image
    if image_html:
        image_field = config.get("image_field", "Image")
        if image_field and image_field in note:
            if not _strip_html(note[image_field]):
                note[image_field] = image_html
                updated.append(image_field)

    if updated:
        editor.loadNote(focusTo=editor.currentField)
        tooltip(f"✅  Applied!  Filled: {', '.join(updated)}")
        logger.info(f"_apply_to_note: filled fields: {updated}")
    else:
        tooltip(
            "No fields were updated.\n"
            "(All target fields were already filled, or data was empty.)"
        )


# ── Main entry point ───────────────────────────────────────────────────────────

def perform_autofill(editor):
    """Entry point — called when the user clicks ✨ Auto Fill in the Editor."""
    note   = editor.note
    config = _get_config()

    trigger_field = config.get("trigger_field", "Front")
    if trigger_field not in note:
        showWarning(
            f"Trigger field '{trigger_field}' was not found in this note type.\n"
            f"Please check 'trigger_field' in the add-on configuration."
        )
        return

    word = _strip_html(note[trigger_field])
    if not word:
        showWarning(
            f"The '{trigger_field}' field is empty.\n"
            f"Please type a word or phrase first, then click Auto Fill."
        )
        return

    source_lang = config.get("source_language", "Spanish")
    target_lang = config.get("target_language", "Persian")

    logger.info(f"Auto Fill triggered: '{word}'  ({source_lang} → {target_lang})")

    op = QueryOp(
        parent=editor.widget,
        op=lambda col: _fetch_all(col, word, source_lang, target_lang, config),
        success=lambda result: on_autofill_success(editor, result, config, word),
    )
    op.failure(
        lambda err: showWarning(
            f"FlashFill: Auto Fill failed.\n\n"
            f"Error: {type(err).__name__}: {err}\n\n"
            f"If you are using 'gemini' or 'openrouter', check your API key in:\n"
            f"Tools → FlashFill: Settings…"
        )
    )
    op.with_progress(f"Fetching data for '{word}'…").run_in_background()


# ── Success handler (main thread) ──────────────────────────────────────────────

def on_autofill_success(
    editor,
    result: tuple,
    config: dict,
    word: str = "",
) -> None:
    """
    Called on the main thread after _fetch_all() completes.

    • preview_enabled = True  → shows PreviewDialog for user review
    • preview_enabled = False → applies data directly (no dialog)
    """
    lang_data, audio_tag, image_html = result

    if lang_data is None:
        showWarning(
            "The provider returned no language data.\n"
            "Make sure:\n"
            "  • Provider is set to 'mock' for testing, OR\n"
            "  • The API key is correct for 'gemini' / 'openrouter'"
        )
        return

    if config.get("preview_enabled", True):
        # ── Show Preview Dialog ─────────────────────────────────────────────
        from ..ui.preview_dialog import PreviewDialog

        dlg = PreviewDialog(
            word=word,
            lang_data=lang_data,
            audio_tag=audio_tag,
            image_html=image_html,
            config=config,
            editor=editor,
            parent=editor.widget,
        )
        dlg.exec()
    else:
        # ── Apply directly (preview disabled by user preference) ────────────
        _apply_to_note(editor, lang_data, audio_tag, image_html, config)
