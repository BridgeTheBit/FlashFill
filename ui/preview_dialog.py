"""
Preview Dialog — Stage 4.

Displays fetched language data, image, and audio BEFORE writing to the note.

Actions available to the user:
  • Review all fetched fields side by side
  • Regenerate the image (calls perform_image_fill in background again)
  • Apply  → writes data to the note and closes
  • Cancel → discards everything and closes (note unchanged)
"""

import os
import re
from typing import Optional

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QGroupBox, QScrollArea, QWidget,
    QFrame, Qt, QPixmap, QSize, QSizePolicy,
)
from aqt.operations import QueryOp
from aqt.utils import tooltip

from ..core.models import LanguageData
from ..utils.logger import get_logger

logger = get_logger(__name__)


# ── Stylesheet ─────────────────────────────────────────────────────────────────
STYLE = """
QDialog {
    background-color: #1a1d2e;
    color: #e0e4f0;
    font-family: "Segoe UI", "SF Pro Display", Arial, sans-serif;
    font-size: 13px;
}
QGroupBox {
    background: #232640;
    border: 1px solid #2e3255;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 14px 12px 14px;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 1px;
    color: #7c6af7;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background: #232640;
}
QLabel { color: #c0c8e0; font-size: 12px; }
QLabel#headerLabel {
    font-size: 18px;
    font-weight: 700;
    color: #7c6af7;
    letter-spacing: 0.3px;
}
QLabel#fieldKey {
    color: #8890b8;
    font-size: 12px;
    font-weight: 600;
    min-width: 140px;
}
QLabel#fieldValue {
    color: #e8ecf8;
    font-size: 13px;
}
QLabel#audioLabel {
    color: #7ab8f5;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 12px;
    background: #1b2c4a;
    border: 1px solid #243a60;
    border-radius: 6px;
    padding: 8px 12px;
}
QLabel#emptyLabel {
    color: #484c6e;
    font-style: italic;
    font-size: 12px;
}
QPushButton {
    background: #7c6af7;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover   { background: #9280ff; }
QPushButton:pressed { background: #5e4fd8; }
QPushButton:disabled { background: #2e3255; color: #505580; }
QPushButton#cancelBtn {
    background: #252840;
    border: 1px solid #383b5e;
    color: #9098c0;
}
QPushButton#cancelBtn:hover {
    background: #2e1818;
    border-color: #c04040;
    color: #e07070;
}
QPushButton#regenBtn {
    background: #1e2235;
    border: 1px solid #3a3e62;
    color: #9098c0;
    padding: 7px 18px;
    font-size: 12px;
}
QPushButton#regenBtn:hover {
    background: #282c4a;
    border-color: #7c6af7;
    color: #c0b8ff;
}
QPushButton#regenBtn:disabled { background: #1a1d2e; color: #404460; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #1e2235;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #363a58;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #7c6af7; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QFrame#sep { background: #2a2e4a; max-height: 1px; }
"""

# Ordered list of language fields and their display labels
_FIELD_LABELS = [
    ("translation",         "Translation"),
    ("english",             "English"),
    ("pronunciation",       "Pronunciation"),
    ("part_of_speech",      "Part of Speech"),
    ("gender",              "Gender"),
    ("example",             "Example"),
    ("example_translation", "Example Translation"),
    ("cefr",                "CEFR"),
    ("notes",               "Notes"),
]


class PreviewDialog(QDialog):
    """
    Preview + confirm dialog for Auto Fill.

    Args:
        word:       The source word or phrase.
        lang_data:  Stage 1 result.
        audio_tag:  Stage 3 result ("[sound:…]") or None.
        image_html: Stage 2 result ('<img src="…">') or None.
        config:     Add-on config dict.
        editor:     Anki Editor — used when applying to the note.
    """

    def __init__(
        self,
        word: str,
        lang_data: LanguageData,
        audio_tag: Optional[str],
        image_html: Optional[str],
        config: dict,
        editor,
        parent=None,
    ):
        super().__init__(parent)
        self._word       = word
        self._lang_data  = lang_data
        self._audio_tag  = audio_tag
        self._image_html = image_html
        self._config     = config
        self._editor     = editor

        self.setWindowTitle(f"Auto Fill Preview — {word}")
        self.setMinimumWidth(580)
        self.setMinimumHeight(580)
        self.setStyleSheet(STYLE)
        self._build_ui()

    # ──────────────────────────────────────────────────────── UI builder ──────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 14)

        # Header
        header = QLabel(f"👁  Preview — {self._word}")
        header.setObjectName("headerLabel")
        root.addWidget(header)

        sep = QFrame()
        sep.setObjectName("sep")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(10)
        cl.setContentsMargins(0, 0, 6, 0)

        cl.addWidget(self._build_language_section())
        cl.addWidget(self._build_image_section())
        if self._audio_tag:
            cl.addWidget(self._build_audio_section())
        cl.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

        # Bottom separator + buttons
        sep2 = QFrame()
        sep2.setObjectName("sep")
        sep2.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep2)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel = QPushButton("✕  Cancel")
        cancel.setObjectName("cancelBtn")
        cancel.setMinimumWidth(100)
        cancel.clicked.connect(self.reject)

        apply_btn = QPushButton("✓  Apply to Note")
        apply_btn.setMinimumWidth(150)
        apply_btn.clicked.connect(self._on_apply)

        btn_row.addWidget(cancel)
        btn_row.addWidget(apply_btn)
        root.addLayout(btn_row)

    # ──────────────────────────────────────────────── Section builders ──────

    def _build_language_section(self) -> QGroupBox:
        box = QGroupBox("Language Data")
        form = QFormLayout(box)
        form.setSpacing(8)
        form.setContentsMargins(10, 22, 10, 10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        has_data = False
        for field_key, display_label in _FIELD_LABELS:
            value = getattr(self._lang_data, field_key, None)
            if not value:
                continue
            has_data = True

            key_lbl = QLabel(f"{display_label}:")
            key_lbl.setObjectName("fieldKey")

            val_lbl = QLabel(value)
            val_lbl.setObjectName("fieldValue")
            val_lbl.setWordWrap(True)
            val_lbl.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            form.addRow(key_lbl, val_lbl)

        if not has_data:
            lbl = QLabel("No language data available.")
            lbl.setObjectName("emptyLabel")
            form.addRow(lbl)

        return box

    def _build_image_section(self) -> QGroupBox:
        box = QGroupBox("Image")
        layout = QVBoxLayout(box)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 22, 10, 12)

        # Image display
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumHeight(130)
        self._image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._image_label.setStyleSheet(
            "background: #1b1e30; border-radius: 8px; padding: 8px;"
        )

        if self._image_html:
            pixmap = self._pixmap_from_html(self._image_html)
            if pixmap:
                self._image_label.setPixmap(self._scale(pixmap))
            else:
                fname = self._filename_from_html(self._image_html)
                self._image_label.setText(f"🖼  Saved to Media:\n{fname}")
        else:
            self._image_label.setText("No image available")
            self._image_label.setObjectName("emptyLabel")

        layout.addWidget(self._image_label)

        # Regenerate button
        self._regen_btn = QPushButton("🔄  Regenerate Image")
        self._regen_btn.setObjectName("regenBtn")
        self._regen_btn.setFixedWidth(180)
        self._regen_btn.clicked.connect(self._on_regenerate)
        layout.addWidget(self._regen_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return box

    def _build_audio_section(self) -> QGroupBox:
        box = QGroupBox("Audio")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 22, 10, 12)

        lbl = QLabel(self._audio_tag)
        lbl.setObjectName("audioLabel")
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(lbl)

        return box

    # ──────────────────────────────────────────────── Image helpers ──────────

    @staticmethod
    def _filename_from_html(html: str) -> str:
        m = re.search(r'<img\s+src="([^"]+)"', html)
        return m.group(1) if m else ""

    @staticmethod
    def _scale(pixmap: QPixmap, max_px: int = 220) -> QPixmap:
        return pixmap.scaled(
            QSize(max_px, max_px),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _pixmap_from_html(self, html: str) -> Optional[QPixmap]:
        """Load the image from Anki Media folder by extracting the filename."""
        fname = self._filename_from_html(html)
        if not fname:
            return None
        path = os.path.join(mw.col.media.dir(), fname)
        if not os.path.exists(path):
            logger.warning(f"PreviewDialog: image not in media folder: {path}")
            return None
        px = QPixmap(path)
        return None if px.isNull() else px

    # ──────────────────────────────────────────────── Event handlers ─────────

    def _on_regenerate(self):
        """Re-fetch the image in background and update the preview."""
        from ..core.image_fill import perform_image_fill

        self._regen_btn.setEnabled(False)
        self._image_label.setPixmap(QPixmap())   # clear old image
        self._image_label.setText("⏳  Fetching new image…")

        op = QueryOp(
            parent=self,
            op=lambda _: perform_image_fill(
                self._word, self._lang_data, self._config
            ),
            success=self._on_regen_done,
        )
        op.failure(lambda err: self._on_regen_error(str(err)))
        op.with_progress("Regenerating image…").run_in_background()

    def _on_regen_done(self, new_html: Optional[str]):
        self._regen_btn.setEnabled(True)
        if new_html:
            self._image_html = new_html
            pixmap = self._pixmap_from_html(new_html)
            if pixmap:
                self._image_label.setPixmap(self._scale(pixmap))
            else:
                self._image_label.setText(
                    f"🖼  {self._filename_from_html(new_html)}"
                )
            tooltip("✅  Image regenerated!")
        else:
            self._image_label.setText("No image returned")
            tooltip("No image found — try changing the provider in Settings.")

    def _on_regen_error(self, err: str):
        self._regen_btn.setEnabled(True)
        self._image_label.setText("❌  Regeneration failed")
        tooltip(f"Image error: {err}")

    def _on_apply(self):
        """Write all data to the note, then close."""
        from ..core.autofill import _apply_to_note

        _apply_to_note(
            self._editor,
            self._lang_data,
            self._audio_tag,
            self._image_html,
            self._config,
        )
        self.accept()
