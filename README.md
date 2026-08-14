# FlashFill — Anki Add-on

> **Automatically fills language-learning flashcard fields using AI.**  
> Supports any source and target language. Works with Gemini, OpenRouter (100+ models), and an offline Mock mode.

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [Installation](#installation)
3. [First Run — Note Type Setup](#first-run--note-type-setup)
4. [Configuration](#configuration)
5. [Getting API Keys](#getting-api-keys)
   - [Google Gemini (Free)](#google-gemini-free)
   - [OpenRouter (Free + Paid models)](#openrouter-free--paid-models)
6. [How to Use](#how-to-use)
7. [Audio Feature (Automatic Pronunciation)](#audio-feature-automatic-pronunciation)
8. [Image Feature (Automatic Images)](#image-feature-automatic-images)
   - [Unsplash API Key](#unsplash-api-key)
   - [Pexels API Key](#pexels-api-key)
9. [Preview Dialog](#preview-dialog)
10. [Session Cache](#session-cache)
11. [Field Mapping](#field-mapping)
12. [Troubleshooting](#troubleshooting)

---

## What It Does

You type a word or phrase in the **Front** field of a card (e.g., `bonjour`), click **✨ Auto Fill**, and the add-on automatically fills:

| Field | Example |
|-------|---------|
| Translation | سلام / درود |
| English | Hello / Good morning |
| Pronunciation | /bɔ̃.ʒuʁ/ |
| Part of Speech | Interjection |
| Gender | — |
| Example | Bonjour, comment ça va ? |
| Example Translation | Hello, how are you? |
| CEFR | A1 |
| Notes | Common French greeting used at any time of day |
| Audio | 🔊 (spoken pronunciation MP3) |
| Image | 🖼 (contextual photo) |

Works for **any language pair**: Spanish→English, Japanese→Arabic, German→Persian, etc.

---

## Installation

### Method 1 — Copy the folder (Manual install)

1. Open Anki
2. Go to **Tools → Add-ons → Open Add-ons Folder**
3. Create a new folder inside `addons21/`, for example: `addons21/language_auto_fill/`
4. Copy **all files** from this project into that folder
5. Restart Anki

### Method 2 — From AnkiWeb (if published)

1. In Anki, go to **Tools → Add-ons → Get Add-ons…**
2. Enter the add-on code
3. Click OK and restart Anki

---

## First Run — Note Type Setup

On the **first time** you open Anki after installation, the add-on **automatically creates** a Note Type called **"FlashFill"** with all 12 fields pre-configured and a styled card template.

You will see a confirmation message. After that:

1. Go to **Add** (shortcut: `A`)
2. At the top, click the **Note Type** selector (shows "Basic" by default)
3. Choose **"FlashFill"**
4. You're ready!

> **No manual field setup required.** The Note Type is created automatically on first run.

---

## Configuration

Go to **Tools → FlashFill: Settings…**

### General Tab
| Setting | Description |
|---------|-------------|
| Source Language | The language you are **learning** (e.g., Spanish, Japanese) |
| Target Language | The language you **translate into** (e.g., Persian, English) |
| Word input field | The field where you type the word (default: `Front`) |
| Show preview before applying | Opens a preview dialog to review data before saving |
| Session Cache | Shows how many words are cached; button to clear cache |

### Provider Tab
| Setting | Description |
|---------|-------------|
| Provider | `mock` (offline test), `gemini`, or `openrouter` |
| API Key | Your API key for the selected provider |
| Model (OpenRouter only) | The AI model to use (e.g., `google/gemma-3-27b-it:free`) |

### Audio Tab
| Setting | Description |
|---------|-------------|
| Enable audio | Toggle on/off |
| TTS Provider | `mock` (silent file) or `gtts` (Google Translate TTS, free) |
| Audio field name | Must match the field name in your Note Type |

### Image Tab
| Setting | Description |
|---------|-------------|
| Enable image | Toggle on/off |
| Image Provider | `mock` (blue placeholder), `unsplash`, or `pexels` |
| API Key | Only needed for Unsplash or Pexels |
| Image field name | Must match the field name in your Note Type |

### Field Mapping Tab
Map each data type to the correct field name in your Note Type.  
Leave a field blank to skip it.

---

## Getting API Keys

### Google Gemini (Free)

Google Gemini offers a **generous free tier** (15 requests/minute, 1 million tokens/day).

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)
5. In Anki: **Tools → FlashFill: Settings… → Provider tab**
   - Set Provider to `gemini`
   - Paste your key in the API Key field
   - Click Save

> **Recommended for beginners.** No payment info required.

---

### OpenRouter (Free + Paid models)

OpenRouter gives you access to **100+ AI models** (GPT-4, Claude, Llama, Gemma, etc.) through a single API key. Many models are **free**.

**Step 1 — Create an account:**
1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Click **Sign In** → create an account (GitHub or Google login available)

**Step 2 — Get your API key:**
1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Click **Create Key**
3. Give it a name (e.g., `Anki Auto Fill`)
4. Copy the key (starts with `sk-or-...`)

**Step 3 — Configure in Anki:**
1. **Tools → FlashFill: Settings… → Provider tab**
2. Set Provider to `openrouter`
3. Paste your API key
4. Choose a model (recommendations below)
5. Click Save

**Recommended Free Models:**

| Model | ID to paste | Notes |
|-------|-------------|-------|
| Google Gemma 3 27B | `google/gemma-3-27b-it:free` | ✅ Default, excellent quality |
| Meta Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct:free` | Very capable, free |
| DeepSeek R1 | `deepseek/deepseek-r1-0528:free` | Strong reasoning |
| Mistral 7B | `mistralai/mistral-7b-instruct:free` | Fast and lightweight |

> To browse all models, visit [https://openrouter.ai/models?order=top-weekly](https://openrouter.ai/models?order=top-weekly) and filter by **Free**.

---

## How to Use

1. Open the **Add** window in Anki (`A` key)
2. Select **"FlashFill"** as your Note Type
3. Type a word or phrase in the **Front** field  
   (e.g., `auf Wiedersehen`, `おはよう`, `merci beaucoup`)
4. Click the **✨ Auto Fill** button in the toolbar  
   (or press **Ctrl+Shift+A**)
5. A progress indicator appears while data is fetched
6. The **Preview Dialog** opens — review all fields
7. Click **✓ Apply to Note** to save, or **✕ Cancel** to discard

> **Existing fields are never overwritten.** Auto Fill only fills empty fields.

---

## Audio Feature (Automatic Pronunciation)

The add-on uses **Google Translate TTS** (free, no API key) to download MP3 pronunciation audio.

1. In Settings → **Audio tab**:
   - Check "Enable automatic audio pronunciation"
   - Set TTS Provider to `gtts`
   - Set Audio field name to `Audio`
2. When you click Auto Fill, the pronunciation is downloaded and saved to Anki Media
3. The Audio field is filled with `[sound:autofill_es_bonjour.mp3]`
4. In card review, the audio plays automatically

> **Supported languages**: 28+ languages including Spanish, French, German, Japanese, Arabic, Persian, Turkish, Chinese, Korean, Russian, and more.

---

## Image Feature (Automatic Images)

### Unsplash API Key (50 req/hour — Free)

1. Go to [https://unsplash.com/developers](https://unsplash.com/developers)
2. Click **"Register as a developer"** and create a free account
3. Click **"New Application"**
4. Accept the terms, fill in the app name and description
5. Scroll down to **"Keys"** — copy your **Access Key**
6. In Anki: Settings → **Image tab**
   - Set Image Provider to `unsplash`
   - Paste the Access Key

### Pexels API Key (200 req/hour — Free)

1. Go to [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Click **"Get Started"** and create a free account
3. Go to [https://www.pexels.com/api/new/](https://www.pexels.com/api/new/)
4. Fill in the form and submit
5. Your API key appears on the page — copy it
6. In Anki: Settings → **Image tab**
   - Set Image Provider to `pexels`
   - Paste the API Key

> **Image query generation is smart:** Nouns → direct search ("dog"), Verbs → gerund form ("person eating"), Phrases → full translation query.

---

## Preview Dialog

After fetching data, the Preview Dialog shows everything before saving:

- All language fields with their values
- The downloaded image (live preview)
- The audio file tag

**Actions:**
- **✓ Apply to Note** — write data to the card and close
- **✕ Cancel** — discard everything, note unchanged
- **🔄 Regenerate Image** — fetch a new image without closing the dialog

---

## Session Cache

The add-on caches results for the duration of your Anki session. If you run Auto Fill on the same word again, the cached result is returned instantly (no API call).

- Cache is cleared automatically when Anki restarts
- You can manually clear it: Settings → General → **🗑 Clear Cache**

---

## Field Mapping

If you use a **custom Note Type** (not "FlashFill"), you can configure which data goes into which field:

1. Settings → **Field Mapping tab**
2. For each data type, enter the exact field name from your Note Type
3. Leave blank to skip that data type

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Auto Fill button not visible | Restart Anki completely |
| "Trigger field not found" error | Check the "Word input field" setting — it must match your Note Type's field name exactly |
| No data returned (mock mode) | Switch to `gemini` or `openrouter` with a valid API key |
| API key rejected (401 error) | Double-check the key is correct and has no leading/trailing spaces |
| Image not showing in card | Make sure the `Image` field is included in your card template |
| Audio not playing | Ensure the `Audio` field is in your template and the media folder has the file |
| Rate limit error (429) | You've exceeded the free tier. Wait a minute or upgrade your plan |
| OpenRouter "no credits" error | Add a small credit ($1–5) at [openrouter.ai/credits](https://openrouter.ai/credits) for paid models, or use a free model |

---

## File Structure

```
addons21/language_auto_fill/
├── __init__.py              # Entry point — creates Note Type on first run
├── config.json              # Default settings
├── README.md                # This guide (English)
├── GUIDE_FA.md              # Installation guide (Persian / فارسی)
├── core/
│   ├── autofill.py          # Main Auto Fill logic
│   ├── audio_fill.py        # TTS audio download
│   ├── image_fill.py        # Image search and download
│   ├── cache.py             # Session cache
│   └── models.py            # LanguageData dataclass
├── providers/
│   ├── mock.py              # Offline test provider
│   ├── gemini_provider.py   # Google Gemini AI
│   ├── openrouter_provider.py  # OpenRouter (100+ models)
│   └── audio/               # Audio providers (gtts, mock)
│   └── image/               # Image providers (unsplash, pexels, mock)
├── ui/
│   ├── editor_btn.py        # Toolbar button
│   ├── settings_dialog.py   # Settings window
│   └── preview_dialog.py    # Preview before applying
└── utils/
    └── logger.py            # Logging utility
```

---

*Made with ❤️ for language learners.*
