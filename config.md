# FlashFill — Configuration Reference

All settings are managed through **Tools → FlashFill: Settings…** in Anki.
This file documents the raw `config.json` keys for reference.

## config.json Keys

| Key | Default | Description |
|-----|---------|-------------|
| `source_language` | `"Spanish"` | Language you are **learning** |
| `target_language` | `"Persian"` | Language you **translate into** |
| `provider` | `"mock"` | AI provider: `mock`, `gemini`, or `openrouter` |
| `api_key` | `""` | API key for the provider (empty for mock) |
| `openrouter_model` | `"google/gemma-3-27b-it:free"` | Model ID for OpenRouter |
| `trigger_field` | `"Front"` | Field where you type the word |
| `field_mapping` | see below | Maps data types to Note Type field names |
| `audio_enabled` | `true` | Enable TTS audio download |
| `audio_provider` | `"mock"` | Audio provider: `mock` or `gtts` |
| `audio_field` | `"Audio"` | Note field for the audio tag |
| `image_enabled` | `true` | Enable image search and download |
| `image_provider` | `"mock"` | Image provider: `mock`, `unsplash`, or `pexels` |
| `image_api_key` | `""` | API key for image provider |
| `image_field` | `"Image"` | Note field for the image tag |
| `preview_enabled` | `true` | Show preview dialog before applying |

## field_mapping

```json
"field_mapping": {
    "translation":         "Translation",
    "english":             "English",
    "pronunciation":       "Pronunciation",
    "part_of_speech":      "Part of Speech",
    "gender":              "Gender",
    "example":             "Example",
    "example_translation": "Example Translation",
    "cefr":                "CEFR",
    "notes":               "Notes"
}
```

The key is the internal data name; the value is the **exact field name** in your Anki Note Type.  
Leave the value empty (`""`) to skip that data type.

## Notes

- The "FlashFill" Note Type is created automatically on first run.
- All settings can be changed at any time via the Settings dialog.
- For full setup instructions see `README.md` (English) or `GUIDE_FA.md` (فارسی).
