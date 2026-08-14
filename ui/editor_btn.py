"""
FlashFill — Editor toolbar buttons.

Adds two buttons to the Anki Note Editor toolbar:
  • ✨ Auto Fill  (Ctrl+Shift+A) — fetches and fills language data
  • ⚙ Settings              — opens the FlashFill settings dialog

Hook used: gui_hooks.editor_did_init_buttons
Signature: (buttons: list[str], editor: Editor) -> None
"""

from aqt import gui_hooks
from ..core.autofill import perform_autofill
from .settings_dialog import open_settings


def _add_buttons(buttons: list, editor) -> None:
    """Appends the FlashFill buttons to the editor toolbar button list."""

    autofill_btn = editor.addButton(
        icon=None,
        cmd="flashFillAutoFill",
        func=lambda e=editor: perform_autofill(e),
        tip="FlashFill: Auto Fill Language Information (Ctrl+Shift+A)",
        keys="Ctrl+Shift+A",
        label="✨ Auto Fill",
    )
    buttons.append(autofill_btn)

    settings_btn = editor.addButton(
        icon=None,
        cmd="flashFillSettings",
        func=lambda e=editor: open_settings(),
        tip="FlashFill: Open Settings",
        label="⚙ Settings",
    )
    buttons.append(settings_btn)


def init_ui() -> None:
    """Register the toolbar hook. Called once from __init__.py."""
    gui_hooks.editor_did_init_buttons.append(_add_buttons)
