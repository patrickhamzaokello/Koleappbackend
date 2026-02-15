from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageConfig:
    id: str
    display_name: str
    native_name: str
    # ElevenLabs Scribe language hint (None = auto-detect)
    eleven_code: str | None


# ─── Supported languages ──────────────────────────────────────────────────────

LANGUAGES: dict[str, LanguageConfig] = {
    "luganda": LanguageConfig(
        id="luganda",
        display_name="Luganda",
        native_name="Luganda",
        eleven_code=None,
    ),
    "swahili": LanguageConfig(
        id="swahili",
        display_name="Swahili",
        native_name="Kiswahili",
        eleven_code="sw",
    ),
    "acholi": LanguageConfig(
        id="acholi",
        display_name="Acholi",
        native_name="Acholi",
        eleven_code=None,
    ),
    "runyankole": LanguageConfig(
        id="runyankole",
        display_name="Runyankole",
        native_name="Runyankole",
        eleven_code=None,
    ),
    "ateso": LanguageConfig(
        id="ateso",
        display_name="Ateso",
        native_name="Ateso",
        eleven_code=None,
    ),
    "english": LanguageConfig(
        id="english",
        display_name="English",
        native_name="English",
        eleven_code="en",
    ),
}


def get_language(language_id: str) -> LanguageConfig | None:
    """Return a LanguageConfig by ID (case-insensitive), or None if unknown."""
    return LANGUAGES.get(language_id.lower())


def get_display_name(language_id: str) -> str:
    """Return the display name for a language ID, falling back to the raw ID."""
    lang = get_language(language_id)
    return lang.display_name if lang else language_id.capitalize()