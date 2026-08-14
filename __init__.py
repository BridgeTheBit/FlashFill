"""
FlashFill — Anki Add-on entry point.

On first run (profile_did_open hook):
  • Creates the "FlashFill" Note Type with all 12 fields and a styled
    card template. Users just pick this note type and start filling cards.

On every Anki start:
  • Registers the ✨ Auto Fill button in the Note Editor toolbar.
  • Adds "FlashFill: Settings…" to the Tools menu.
"""

from aqt import mw, gui_hooks
from aqt.qt import QAction
from aqt.utils import showInfo

from .ui.editor_btn import init_ui
from .ui.settings_dialog import open_settings


# ── Note Type definition ──────────────────────────────────────────────────────

NOTE_TYPE_NAME = "FlashFill"

NOTE_FIELDS = [
    "Front",                # trigger field — user types the word here
    "Translation",          # target-language translation
    "English",              # English translation
    "Pronunciation",        # IPA phonetics
    "Part of Speech",       # Noun / Verb / Phrase / Adjective …
    "Gender",               # Masculine / Feminine / Neuter (if applicable)
    "Example",              # example sentence in source language
    "Example Translation",  # example translated to target language
    "CEFR",                 # A1 – C2 level
    "Notes",                # grammar or usage notes
    "Audio",                # [sound:filename.mp3]
    "Image",                # <img src="filename.jpg">
]

_CARD_FRONT = """\
<div class="card-wrapper">
  <div class="word-header">
    <div class="word-main">{{Front}}</div>
  </div>
</div>
"""

_CARD_BACK = """\
<div class="card-wrapper">

  <div class="word-header">
    <div class="word-main">{{Front}}</div>

    {{#Pronunciation}}
    <div class="word-pronunciation">/ {{Pronunciation}} /</div>
    {{/Pronunciation}}

    <div class="word-meta">
      {{#Part of Speech}}
      <span class="badge badge-pos">{{Part of Speech}}</span>
      {{/Part of Speech}}

      {{#Gender}}
      <span class="badge badge-gender">{{Gender}}</span>
      {{/Gender}}

      {{#CEFR}}
      <span class="badge badge-cefr">{{CEFR}}</span>
      {{/CEFR}}
    </div>
    {{#Audio}}
    	<span><br>{{Audio}}</span>
    {{/Audio}}
  </div>

  <div class="info-grid">

    {{#Translation}}
    <div class="info-card translation full-width">
      <div class="info-label">Translation</div>
      <div class="info-value persian">{{Translation}}</div>
    </div>
    {{/Translation}}

    {{#English}}
    <div class="info-card english">
      <div class="info-label">English</div>
      <div class="info-value">{{English}}</div>
    </div>
    {{/English}}

    {{#Pronunciation}}
    <div class="info-card">
      <div class="info-label">Pronunciation</div>
      <div class="info-value" style="color:#a78bfa;">/ {{Pronunciation}} /</div>
    </div>
    {{/Pronunciation}}

  </div>

  {{#Example}}
  <div class="example-block">
    <div class="info-label">📖  Example</div>
    <div class="example-src">{{Example}}</div>
    {{#Example Translation}}
    <div class="example-tgt">{{Example Translation}}</div>
    {{/Example Translation}}
  </div>
  {{/Example}}

  {{#Image}}
  <div class="Image-block">
    <div class="info-label">📖  Image</div> <br>
    <div class="Image-src">{{Image}}</div>
  </div>
  {{/Image}}

  {{#Notes}}
  <div class="notes-block">
    <div class="info-label">💡  Notes</div>
    {{Notes}}
  </div>
  {{/Notes}}

</div>
"""

_CARD_CSS = """\
/* ── FlashFill card styles ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Naskh+Arabic:wght@400;500;700&display=swap');

  :root {
    --bg: #0f1117;
    --surface: #1a1d2e;
    --surface2: #222540;
    --border: #2e3255;
    --accent: #7c6af7;
    --accent2: #a78bfa;
    --text: #e2e8f0;
    --text-muted: #8892b0;
    --green: #34d399;
    --blue: #60a5fa;
    --rose: #f472b6;
    --amber: #fbbf24;
    --radius: 12px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    font-size: 15px;
    min-height: 100vh;
    padding: 0;
  }

  .card-wrapper {
    max-width: 680px;
    margin: 0 auto;
    padding: 24px 20px 32px;
  }

  /* ── Word header ── */
  .word-header {
    text-align: center;
    padding: 28px 24px 22px;
    background: linear-gradient(135deg, #1e1b4b 0%, #1a1d3a 60%, #0f172a 100%);
    border: 1px solid #3730a3;
    border-radius: var(--radius);
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
  }
  .word-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #7c6af7, #a78bfa, #60a5fa);
  }
  .word-main {
    font-size: 36px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.5px;
    line-height: 1.2;
  }
  .word-pronunciation {
    font-size: 15px;
    color: var(--accent2);
    margin-top: 8px;
    font-weight: 400;
    letter-spacing: 0.5px;
  }
  .word-meta {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 12px;
    flex-wrap: wrap;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .badge-pos {
    background: rgba(124, 106, 247, 0.2);
    border: 1px solid rgba(124, 106, 247, 0.4);
    color: var(--accent2);
  }
  .badge-gender {
    background: rgba(244, 114, 182, 0.15);
    border: 1px solid rgba(244, 114, 182, 0.35);
    color: var(--rose);
  }
  .badge-cefr {
    background: rgba(251, 191, 36, 0.15);
    border: 1px solid rgba(251, 191, 36, 0.35);
    color: var(--amber);
  }

  /* ── Info grid ── */
  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .info-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 16px;
    position: relative;
  }
  .info-card.full-width {
    grid-column: 1 / -1;
  }
  .info-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }
  .info-value {
    font-size: 16px;
    font-weight: 500;
    color: var(--text);
    line-height: 1.5;
  }

  /* color accents per card type */
  .info-card.translation .info-label { color: var(--green); }
  .info-card.translation { border-left: 3px solid var(--green); }
  .info-card.english .info-label { color: var(--blue); }
  .info-card.english { border-left: 3px solid var(--blue); }

  /* ── Example block ── */
  .example-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 12px;
    border-left: 3px solid var(--accent);
  }
  .example-block .info-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--accent2);
    margin-bottom: 8px;
  }
  .example-src {
    font-size: 15px;
    font-style: italic;
    color: #c4b5fd;
    margin-bottom: 6px;
    line-height: 1.6;
  }
  .example-tgt {
    font-size: 14px;
    color: var(--text-muted);
    line-height: 1.6;
    direction: rtl;
    text-align: right;
    font-family: 'Noto Naskh Arabic', 'Vazirmatn', Tahoma, sans-serif;
  }
  /* ── Image block ── */
  .Image-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    margin-bottom: 12px;
    border-left: 3px solid var(--accent);
  }
  .Image-block .info-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--accent2);
    margin-bottom: 8px;
  }
  .Image-src {
    display: block;
		text-align: center;
    margin-left: auto;
    margin-right: auto;
    margin-top: 10px;
    margin-bottom: 6px;
    line-height: 1.6;
  }

  /* ── Notes ── */
  .notes-block {
    background: rgba(251, 191, 36, 0.06);
    border: 1px solid rgba(251, 191, 36, 0.2);
    border-radius: var(--radius);
    padding: 12px 16px;
    font-size: 13px;
    color: #e2c97e;
    line-height: 1.6;
  }
  .notes-block .info-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--amber);
    margin-bottom: 5px;
  }

  /* ── Persian text ── */
  .persian {
    direction: rtl;
    text-align: right;
    font-family: 'Noto Naskh Arabic', 'Vazirmatn', Tahoma, sans-serif;
    font-size: 18px;
  }

  /* hide empty fields */
  .info-card:empty { display: none; }
"""


# ── Note Type creation ────────────────────────────────────────────────────────

def _ensure_note_type() -> None:
    """
    Creates the 'FlashFill' Note Type if it doesn't already exist.
    Called via profile_did_open so the collection is guaranteed to be open.
    Safe to call on every Anki startup — exits immediately if the type exists.
    """
    col = mw.col
    if col is None:
        return

    # Check by name — col.models.by_name() is the correct modern API
    if col.models.by_name(NOTE_TYPE_NAME) is not None:
        return  # already created

    # Build model dict using the standard helper methods
    model = col.models.new(NOTE_TYPE_NAME)

    for field_name in NOTE_FIELDS:
        fld = col.models.new_field(field_name)
        col.models.add_field(model, fld)

    # Add single card template
    tmpl = col.models.new_template("Card 1")
    tmpl["qfmt"] = _CARD_FRONT
    tmpl["afmt"] = _CARD_BACK
    col.models.add_template(model, tmpl)

    model["css"] = _CARD_CSS

    # col.models.add() saves the model and returns OpChangesWithId in modern Anki
    col.models.add(model)

    showInfo(
        "FlashFill\n\n"
        "✅  The 'FlashFill' Note Type has been created!\n\n"
        "It includes all 12 fields (word, translation, pronunciation,\n"
        "example, audio, image, …) and a ready-to-use card template.\n\n"
        "Next steps:\n"
        "  1. Tools → FlashFill: Settings…  (set your languages & API key)\n"
        "  2. Click Add, choose the 'FlashFill' note type\n"
        "  3. Type a word in Front, then click  ✨ Auto Fill"
    )


# ── UI initialisation ─────────────────────────────────────────────────────────

# Add ✨ Auto Fill button to the Note Editor toolbar
init_ui()

# Add "FlashFill: Settings…" entry to the Tools menu
action = QAction("FlashFill: Settings…", mw)
action.triggered.connect(open_settings)
mw.form.menuTools.addAction(action)

# Register Note Type creation — runs after the profile (collection) is loaded
gui_hooks.profile_did_open.append(_ensure_note_type)
