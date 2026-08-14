"""
FlashFill — Settings dialog.

Modern, styled PyQt6 dialog with:
  - Dark/glass-morphism QSS styling
  - Provider selector (Mock / Gemini / OpenRouter)
  - API key input with show/hide
  - Model selector for OpenRouter
  - Test connection with live feedback
  - Language pickers (any language → any language)
  - Audio, Image, and Field Mapping configuration
  - Session Cache management
"""

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QDialogButtonBox, QGroupBox, QTabWidget, QWidget,
    QScrollArea, Qt, QFrame, QSizePolicy, QCheckBox,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

_ADDON_PACKAGE = __name__.split(".")[0]

PROVIDERS = ["mock", "gemini", "openrouter"]

AUDIO_PROVIDERS = ["mock", "gtts"]

AUDIO_PROVIDER_INFO = {
    "mock": "No network needed. Returns a silent audio file for testing.",
    "gtts": (
        "Uses Google Translate's public TTS endpoint.\n"
        "No API key required. Supports all Google Translate languages.\n"
        "May be rate-limited for heavy use."
    ),
}

IMAGE_PROVIDERS = ["mock", "unsplash", "pexels"]

IMAGE_PROVIDER_INFO = {
    "mock": "No network needed. Returns a blue placeholder PNG for testing.",
    "unsplash": (
        "Requires a free Unsplash Access Key.\n"
        "Get one at: https://unsplash.com/developers\n"
        "Free plan: 50 requests / hour."
    ),
    "pexels": (
        "Requires a free Pexels API Key.\n"
        "Get one at: https://www.pexels.com/api/\n"
        "Free plan: 200 requests / hour."
    ),
}

PROVIDER_INFO = {
    "mock": "No API key needed. Returns sample data for testing.",
    "gemini": (
        "Requires a Google AI Studio API key.\n"
        "Get one free at: https://aistudio.google.com/app/apikey"
    ),
    "openrouter": (
        "Access hundreds of models (including free ones) with one key.\n"
        "Get a key at: https://openrouter.ai/keys"
    ),
}

LANGUAGES = [
    "Spanish", "French", "German", "Italian", "Portuguese",
    "Japanese", "Korean", "Chinese", "Arabic", "Turkish",
    "Persian", "English", "Russian", "Dutch", "Polish",
]

DATA_FIELDS = [
    "translation", "english", "pronunciation", "part_of_speech",
    "gender", "example", "example_translation", "cefr", "notes",
]

OPENROUTER_MODELS = [
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "openai/gpt-4o-mini",
    "anthropic/claude-3-haiku",
]

# ── QSS stylesheet ─────────────────────────────────────────────────────────────
STYLE = """
QDialog {
    background-color: #1a1d2e;
    color: #e0e4f0;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #2e3250;
    border-radius: 8px;
    background: #1e2235;
    top: -1px;
}

QTabBar::tab {
    background: #252840;
    color: #8890b0;
    border: 1px solid #2e3250;
    border-bottom: none;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    min-width: 100px;
}
QTabBar::tab:selected {
    background: #1e2235;
    color: #7c6af7;
    border-bottom: 2px solid #7c6af7;
}
QTabBar::tab:hover:!selected {
    background: #2a2d45;
    color: #c0c8e0;
}

QGroupBox {
    background: #232640;
    border: 1px solid #2e3255;
    border-radius: 10px;
    margin-top: 12px;
    padding: 16px 14px 12px 14px;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.8px;
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

QLabel {
    color: #c0c8e0;
    font-size: 12px;
}

QLineEdit {
    background: #2a2d45;
    border: 1px solid #3a3e60;
    border-radius: 7px;
    color: #e0e4f0;
    padding: 7px 11px;
    font-size: 13px;
    selection-background-color: #7c6af7;
}
QLineEdit:focus {
    border: 1.5px solid #7c6af7;
    background: #2f3252;
}
QLineEdit:disabled {
    background: #1e2030;
    color: #505570;
    border-color: #282b40;
}
QLineEdit::placeholder {
    color: #505570;
}

QComboBox {
    background: #2a2d45;
    border: 1px solid #3a3e60;
    border-radius: 7px;
    color: #e0e4f0;
    padding: 7px 11px;
    font-size: 13px;
    min-width: 160px;
}
QComboBox:focus {
    border: 1.5px solid #7c6af7;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background: #252840;
    border: 1px solid #3a3e60;
    border-radius: 6px;
    color: #e0e4f0;
    selection-background-color: #7c6af7;
    selection-color: #ffffff;
    padding: 4px;
}

QPushButton {
    background: #7c6af7;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
QPushButton:hover {
    background: #9280ff;
}
QPushButton:pressed {
    background: #6655e0;
}
QPushButton:disabled {
    background: #383b58;
    color: #606380;
}
QPushButton#secondaryBtn {
    background: #2a2d45;
    border: 1px solid #3a3e60;
    color: #c0c8e0;
}
QPushButton#secondaryBtn:hover {
    background: #323560;
    border-color: #7c6af7;
    color: #e0e4f0;
}

QDialogButtonBox QPushButton {
    min-width: 90px;
    padding: 9px 22px;
}

QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: #1e2235;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3a3e60;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #7c6af7;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QFrame#separator {
    background: #2e3255;
    max-height: 1px;
}

QCheckBox {
    color: #c0c8e0;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1.5px solid #3a3e60;
    background: #2a2d45;
}
QCheckBox::indicator:checked {
    background: #7c6af7;
    border-color: #7c6af7;
}
QCheckBox::indicator:hover {
    border-color: #7c6af7;
}
QCheckBox::indicator:disabled {
    background: #1e2030;
    border-color: #282b40;
}

/* Info / warning banner */
QLabel#infoLabel {
    background: #1e2d4a;
    border: 1px solid #2a4a7a;
    border-radius: 7px;
    color: #7ab8f5;
    padding: 8px 12px;
    font-size: 12px;
}
QLabel#warningLabel {
    background: #2d2010;
    border: 1px solid #5a3a10;
    border-radius: 7px;
    color: #f5c060;
    padding: 8px 12px;
    font-size: 12px;
}
QLabel#successLabel {
    background: #102d1a;
    border: 1px solid #1a5a30;
    border-radius: 7px;
    color: #60c080;
    padding: 8px 12px;
    font-size: 12px;
}
QLabel#errorLabel {
    background: #2d1010;
    border: 1px solid #5a1a1a;
    border-radius: 7px;
    color: #f07070;
    padding: 8px 12px;
    font-size: 12px;
}
"""


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FlashFill  ·  Settings")
        self.setMinimumWidth(580)
        self.setMinimumHeight(520)
        self.setStyleSheet(STYLE)
        self._config = mw.addonManager.getConfig(_ADDON_PACKAGE) or {}
        self._build_ui()
        self._load_config()

    # ──────────────────────────────────────────────────────── UI builder ──────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("⚡  FlashFill")
        header.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #7c6af7; "
            "padding-bottom: 4px; letter-spacing: 0.5px;"
        )
        root.addWidget(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        tabs = QTabWidget()
        tabs.addTab(self._build_general_tab(), "  General  ")
        tabs.addTab(self._build_provider_tab(), "  Provider  ")
        tabs.addTab(self._build_audio_tab(), "  Audio  ")
        tabs.addTab(self._build_image_tab(), "  Image  ")
        tabs.addTab(self._build_fields_tab(), "  Field Mapping  ")
        root.addWidget(tabs)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save_and_close)
        btns.rejected.connect(self.reject)
        # Style Cancel as secondary
        cancel_btn = btns.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setObjectName("secondaryBtn")
        root.addWidget(btns)

    # ── General tab ───────────────────────────────────────────────────────────
    def _build_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 16, 12, 12)

        # Note type warning
        warning = QLabel(
            "⚠  Make sure you are using a Basic note type (not 'Basic and reversed').\n"
            "The 'reversed' type creates two cards per note automatically."
        )
        warning.setObjectName("warningLabel")
        warning.setWordWrap(True)
        layout.addWidget(warning)

        lang_box = QGroupBox("Languages")
        lang_form = QFormLayout(lang_box)
        lang_form.setSpacing(10)
        lang_form.setContentsMargins(8, 20, 8, 8)

        self._src_lang = QComboBox()
        self._src_lang.addItems(LANGUAGES)
        lang_form.addRow("Source (language you are learning):", self._src_lang)

        self._tgt_lang = QComboBox()
        self._tgt_lang.addItems(LANGUAGES)
        lang_form.addRow("Target (translation language):", self._tgt_lang)

        layout.addWidget(lang_box)

        input_box = QGroupBox("Note Editor")
        input_form = QFormLayout(input_box)
        input_form.setSpacing(10)
        input_form.setContentsMargins(8, 20, 8, 8)

        self._trigger_field = QLineEdit()
        self._trigger_field.setPlaceholderText("e.g.  Front  or  Word")
        input_form.addRow("Word / phrase input field:", self._trigger_field)

        layout.addWidget(input_box)

        # ── Behavior
        behavior_box = QGroupBox("Behavior")
        behavior_form = QFormLayout(behavior_box)
        behavior_form.setSpacing(10)
        behavior_form.setContentsMargins(8, 20, 8, 8)

        self._preview_enabled = QCheckBox(
            "Show preview before applying (recommended)"
        )
        behavior_form.addRow(self._preview_enabled)

        layout.addWidget(behavior_box)

        # ── Cache
        cache_box = QGroupBox("Session Cache")
        cache_row = QHBoxLayout(cache_box)
        cache_row.setContentsMargins(8, 22, 8, 8)
        cache_row.setSpacing(12)

        self._cache_size_label = QLabel("0 entries cached")
        self._cache_size_label.setStyleSheet("color: #7080a0; font-size: 12px;")

        self._clear_cache_btn = QPushButton("🗑  Clear Cache")
        self._clear_cache_btn.setObjectName("secondaryBtn")
        self._clear_cache_btn.setFixedWidth(130)
        self._clear_cache_btn.clicked.connect(self._on_clear_cache)

        cache_row.addWidget(self._cache_size_label)
        cache_row.addStretch()
        cache_row.addWidget(self._clear_cache_btn)

        layout.addWidget(cache_box)

        layout.addStretch()
        return tab

    # ── Provider tab ──────────────────────────────────────────────────────────
    def _build_provider_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 16, 12, 12)

        prov_box = QGroupBox("Provider")
        prov_form = QFormLayout(prov_box)
        prov_form.setSpacing(12)
        prov_form.setContentsMargins(8, 20, 8, 8)

        self._provider = QComboBox()
        self._provider.addItems(PROVIDERS)
        self._provider.currentTextChanged.connect(self._on_provider_changed)
        prov_form.addRow("Data provider:", self._provider)

        # API key
        api_row = QHBoxLayout()
        api_row.setSpacing(6)
        self._api_key = QLineEdit()
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key.setPlaceholderText("Paste your API key here")
        api_row.addWidget(self._api_key)
        self._show_key_btn = QPushButton("Show")
        self._show_key_btn.setObjectName("secondaryBtn")
        self._show_key_btn.setFixedWidth(60)
        self._show_key_btn.setCheckable(True)
        self._show_key_btn.toggled.connect(self._toggle_key_visibility)
        api_row.addWidget(self._show_key_btn)
        prov_form.addRow("API Key:", api_row)

        # OpenRouter model
        self._model_label = QLabel("Model:")
        self._model_combo = QComboBox()
        self._model_combo.setEditable(True)
        self._model_combo.addItems(OPENROUTER_MODELS)
        prov_form.addRow(self._model_label, self._model_combo)

        # Provider info
        self._prov_info = QLabel()
        self._prov_info.setObjectName("infoLabel")
        self._prov_info.setWordWrap(True)
        self._prov_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        prov_form.addRow(self._prov_info)

        layout.addWidget(prov_box)

        # Test connection
        test_box = QGroupBox("Connection Test")
        test_layout = QVBoxLayout(test_box)
        test_layout.setSpacing(10)
        test_layout.setContentsMargins(8, 20, 8, 12)

        self._test_btn = QPushButton("🔌  Test Connection")
        self._test_btn.setFixedHeight(38)
        self._test_btn.clicked.connect(self._test_connection)

        self._test_result = QLabel("")
        self._test_result.setWordWrap(True)
        self._test_result.setVisible(False)

        test_layout.addWidget(self._test_btn)
        test_layout.addWidget(self._test_result)
        layout.addWidget(test_box)
        layout.addStretch()
        return tab

    # ── Audio tab ─────────────────────────────────────────────────────────────
    def _build_audio_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 16, 12, 12)

        # Enable toggle
        enable_box = QGroupBox("Audio Pronunciation")
        enable_form = QFormLayout(enable_box)
        enable_form.setSpacing(10)
        enable_form.setContentsMargins(8, 20, 8, 8)

        self._audio_enabled = QCheckBox("Enable automatic audio pronunciation")
        enable_form.addRow(self._audio_enabled)

        self._audio_field = QLineEdit()
        self._audio_field.setPlaceholderText("e.g.  Audio")
        enable_form.addRow("Audio field name in note:", self._audio_field)

        layout.addWidget(enable_box)

        # Provider
        prov_box = QGroupBox("Audio Provider")
        prov_form = QFormLayout(prov_box)
        prov_form.setSpacing(12)
        prov_form.setContentsMargins(8, 20, 8, 8)

        self._audio_provider = QComboBox()
        self._audio_provider.addItems(AUDIO_PROVIDERS)
        self._audio_provider.currentTextChanged.connect(self._on_audio_provider_changed)
        prov_form.addRow("TTS provider:", self._audio_provider)

        self._audio_prov_info = QLabel()
        self._audio_prov_info.setObjectName("infoLabel")
        self._audio_prov_info.setWordWrap(True)
        self._audio_prov_info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        prov_form.addRow(self._audio_prov_info)

        layout.addWidget(prov_box)

        # How-to hint
        hint = QLabel(
            "ℹ  Make sure your note type has a field named exactly as specified above.\n"
            "The audio tag will look like:  [sound:autofill_es_mucho_gusto.mp3]"
        )
        hint.setObjectName("infoLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()
        return tab

    # ── Image tab ─────────────────────────────────────────────────────────────
    def _build_image_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 16, 12, 12)

        # Enable / field
        enable_box = QGroupBox("Image Search")
        enable_form = QFormLayout(enable_box)
        enable_form.setSpacing(10)
        enable_form.setContentsMargins(8, 20, 8, 8)

        self._image_enabled = QCheckBox("Enable automatic image search")
        enable_form.addRow(self._image_enabled)

        self._image_field = QLineEdit()
        self._image_field.setPlaceholderText("e.g.  Image")
        enable_form.addRow("Image field name in note:", self._image_field)

        layout.addWidget(enable_box)

        # Provider + API key
        prov_box = QGroupBox("Image Provider")
        prov_form = QFormLayout(prov_box)
        prov_form.setSpacing(12)
        prov_form.setContentsMargins(8, 20, 8, 8)

        self._image_provider = QComboBox()
        self._image_provider.addItems(IMAGE_PROVIDERS)
        self._image_provider.currentTextChanged.connect(self._on_image_provider_changed)
        prov_form.addRow("Image provider:", self._image_provider)

        # API key row (shown only for unsplash / pexels)
        img_key_row = QHBoxLayout()
        img_key_row.setSpacing(6)
        self._image_api_key = QLineEdit()
        self._image_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._image_api_key.setPlaceholderText("Paste your image provider API key here")
        img_key_row.addWidget(self._image_api_key)
        self._show_img_key_btn = QPushButton("Show")
        self._show_img_key_btn.setObjectName("secondaryBtn")
        self._show_img_key_btn.setFixedWidth(60)
        self._show_img_key_btn.setCheckable(True)
        self._show_img_key_btn.toggled.connect(self._toggle_img_key_visibility)
        img_key_row.addWidget(self._show_img_key_btn)
        self._image_key_label = QLabel("API Key:")
        prov_form.addRow(self._image_key_label, img_key_row)

        self._image_prov_info = QLabel()
        self._image_prov_info.setObjectName("infoLabel")
        self._image_prov_info.setWordWrap(True)
        self._image_prov_info.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        prov_form.addRow(self._image_prov_info)

        layout.addWidget(prov_box)

        # Hint
        hint = QLabel(
            "ℹ  Make sure your note type has a field named exactly as specified above.\n"
            "The image tag will look like:  <img src=\"autofill_img_dog.jpg\">"
        )
        hint.setObjectName("infoLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()
        return tab

    # ── Field mapping tab ─────────────────────────────────────────────────────
    def _build_fields_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 16, 12, 12)

        info = QLabel(
            "ℹ  Enter the exact field name from your Anki note type for each data point.\n"
            "Leave a row blank to skip that field entirely."
        )
        info.setObjectName("infoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        form = QFormLayout(container)
        form.setSpacing(10)
        form.setContentsMargins(4, 12, 4, 12)

        FIELD_LABELS = {
            "translation": "Translation (target lang)",
            "english": "English",
            "pronunciation": "Pronunciation / IPA",
            "part_of_speech": "Part of Speech",
            "gender": "Gender",
            "example": "Example sentence",
            "example_translation": "Example translation",
            "cefr": "CEFR level",
            "notes": "Notes / grammar tips",
        }

        self._field_inputs = {}
        for key in DATA_FIELDS:
            inp = QLineEdit()
            inp.setPlaceholderText(f"Anki field name")
            form.addRow(FIELD_LABELS.get(key, key) + ":", inp)
            self._field_inputs[key] = inp

        scroll.setWidget(container)
        layout.addWidget(scroll)
        return tab

    # ──────────────────────────────────────────────────── Config load/save ────
    def _load_config(self):
        cfg = self._config
        self._set_combo(self._src_lang, cfg.get("source_language", "Spanish"))
        self._set_combo(self._tgt_lang, cfg.get("target_language", "Persian"))
        self._trigger_field.setText(cfg.get("trigger_field", "Front"))
        self._set_combo(self._provider, cfg.get("provider", "mock"))
        self._api_key.setText(cfg.get("api_key", ""))
        saved_model = cfg.get("openrouter_model", OPENROUTER_MODELS[0])
        self._set_combo(self._model_combo, saved_model)
        self._on_provider_changed(self._provider.currentText())
        mapping = cfg.get("field_mapping", {})
        for key, inp in self._field_inputs.items():
            inp.setText(mapping.get(key, ""))
        # Audio settings
        self._audio_enabled.setChecked(cfg.get("audio_enabled", True))
        self._audio_field.setText(cfg.get("audio_field", "Audio"))
        self._set_combo(self._audio_provider, cfg.get("audio_provider", "mock"))
        self._on_audio_provider_changed(self._audio_provider.currentText())
        # Image settings
        self._image_enabled.setChecked(cfg.get("image_enabled", True))
        self._image_field.setText(cfg.get("image_field", "Image"))
        self._image_api_key.setText(cfg.get("image_api_key", ""))
        self._set_combo(self._image_provider, cfg.get("image_provider", "mock"))
        self._on_image_provider_changed(self._image_provider.currentText())
        # Behavior + Cache
        self._preview_enabled.setChecked(cfg.get("preview_enabled", True))
        self._update_cache_label()

    def _save_and_close(self):
        cfg = self._config.copy()
        cfg["source_language"] = self._src_lang.currentText()
        cfg["target_language"] = self._tgt_lang.currentText()
        cfg["trigger_field"] = self._trigger_field.text().strip()
        cfg["provider"] = self._provider.currentText()
        cfg["api_key"] = self._api_key.text().strip()
        cfg["openrouter_model"] = self._model_combo.currentText().strip()
        cfg["field_mapping"] = {
            key: inp.text().strip()
            for key, inp in self._field_inputs.items()
            if inp.text().strip()
        }
        # Audio settings
        cfg["audio_enabled"] = self._audio_enabled.isChecked()
        cfg["audio_provider"] = self._audio_provider.currentText()
        cfg["audio_field"] = self._audio_field.text().strip()
        # Image settings
        cfg["image_enabled"] = self._image_enabled.isChecked()
        cfg["image_provider"] = self._image_provider.currentText()
        cfg["image_api_key"] = self._image_api_key.text().strip()
        cfg["image_field"] = self._image_field.text().strip()
        # Behavior
        cfg["preview_enabled"] = self._preview_enabled.isChecked()
        mw.addonManager.writeConfig(_ADDON_PACKAGE, cfg)
        self.accept()

    # ───────────────────────────────────────────────────── Event handlers ─────
    def _on_provider_changed(self, provider: str):
        is_mock = provider == "mock"
        is_openrouter = provider == "openrouter"
        self._api_key.setEnabled(not is_mock)
        self._show_key_btn.setEnabled(not is_mock)
        self._model_label.setVisible(is_openrouter)
        self._model_combo.setVisible(is_openrouter)
        self._prov_info.setText(PROVIDER_INFO.get(provider, ""))
        self._test_result.setVisible(False)

    def _on_audio_provider_changed(self, provider: str):
        self._audio_prov_info.setText(AUDIO_PROVIDER_INFO.get(provider, ""))

    def _on_image_provider_changed(self, provider: str):
        is_mock = provider == "mock"
        self._image_api_key.setEnabled(not is_mock)
        self._show_img_key_btn.setEnabled(not is_mock)
        self._image_key_label.setVisible(not is_mock)
        self._image_prov_info.setText(IMAGE_PROVIDER_INFO.get(provider, ""))

    def _toggle_img_key_visibility(self, checked: bool):
        if checked:
            self._image_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self._show_img_key_btn.setText("Hide")
        else:
            self._image_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self._show_img_key_btn.setText("Show")

    def _update_cache_label(self):
        from ..core.cache import size as cache_size
        n = cache_size()
        self._cache_size_label.setText(
            f"{n} {'entry' if n == 1 else 'entries'} cached this session"
        )

    def _on_clear_cache(self):
        from ..core.cache import clear as cache_clear
        count = cache_clear()
        self._update_cache_label()
        from aqt.utils import tooltip
        tooltip(f"Cache cleared — {count} {'entry' if count == 1 else 'entries'} removed.")

    def _toggle_key_visibility(self, checked: bool):
        if checked:
            self._api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self._show_key_btn.setText("Hide")
        else:
            self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self._show_key_btn.setText("Show")

    def _test_connection(self):
        provider_name = self._provider.currentText()
        api_key = self._api_key.text().strip()

        self._set_test_result("⏳  Testing connection…", "info")
        self._test_btn.setEnabled(False)

        from aqt.qt import QApplication
        QApplication.processEvents()

        try:
            if provider_name == "mock":
                from ..providers.mock import MockProvider
                provider = MockProvider()
            elif provider_name == "gemini":
                if not api_key:
                    raise ValueError("Please enter a Gemini API key first.")
                from ..providers.gemini_provider import GeminiProvider
                provider = GeminiProvider(api_key=api_key)
            elif provider_name == "openrouter":
                if not api_key:
                    raise ValueError("Please enter an OpenRouter API key first.")
                model = self._model_combo.currentText().strip()
                from ..providers.openrouter_provider import OpenRouterProvider
                provider = OpenRouterProvider(api_key=api_key, model=model)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")

            result = provider.fetch_data("hello", "English", "Persian")
            if result and result.translation:
                self._set_test_result(
                    f"✅  Connected!  Translation of 'hello': {result.translation}",
                    "success"
                )
            else:
                self._set_test_result("⚠️  Provider returned no data.", "warning")

        except Exception as e:
            self._set_test_result(f"❌  {e}", "error")
        finally:
            self._test_btn.setEnabled(True)

    def _set_test_result(self, text: str, kind: str = "info"):
        style_map = {
            "info":    "infoLabel",
            "success": "successLabel",
            "warning": "warningLabel",
            "error":   "errorLabel",
        }
        self._test_result.setObjectName(style_map.get(kind, "infoLabel"))
        self._test_result.setText(text)
        self._test_result.setVisible(True)
        # Force QSS re-evaluation after objectName change
        self._test_result.style().unpolish(self._test_result)
        self._test_result.style().polish(self._test_result)

    # ──────────────────────────────────────────────────────── Helpers ─────────
    @staticmethod
    def _set_combo(combo: QComboBox, value: str):
        idx = combo.findText(value, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.insertItem(0, value)
            combo.setCurrentIndex(0)


def open_settings():
    dlg = SettingsDialog(parent=mw)
    dlg.exec()
