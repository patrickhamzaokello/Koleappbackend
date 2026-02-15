import logging
from functools import lru_cache

import anthropic
import httpx
from elevenlabs import ElevenLabs
from openai import AsyncOpenAI

from config import get_settings
from languages import get_display_name

logger = logging.getLogger(__name__)


# ─── Lazy client singletons ───────────────────────────────────────────────────

@lru_cache
def get_anthropic_client() -> anthropic.AsyncAnthropic:
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


@lru_cache
def get_elevenlabs_client() -> ElevenLabs:
    settings = get_settings()
    return ElevenLabs(api_key=settings.elevenlabs_api_key)


@lru_cache
def get_openai_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key)


# ─── Translation service ──────────────────────────────────────────────────────

async def translate_with_claude(text: str, source_language: str) -> str:
    """
    Translate `text` from `source_language` into English using Claude.

    Returns the original text unchanged if:
    - `source_language` is English
    - `text` is blank
    """
    if not text or not text.strip():
        return ""

    if source_language.lower() == "english":
        return text

    settings = get_settings()
    lang_name = get_display_name(source_language)

    client = get_anthropic_client()

    logger.info("Translating %d chars from %s via Claude", len(text), lang_name)

    message = await client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.claude_max_tokens,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Translate the following {lang_name} text to English.\n"
                    "Return ONLY the English translation — no explanations, "
                    "no notes, no original text.\n"
                    "If the text is already in English or is unintelligible, "
                    "return it as-is.\n\n"
                    f"Text to translate:\n{text}"
                ),
            }
        ],
    )

    block = message.content[0]
    return block.text.strip() if block.type == "text" else text


async def translate_with_openai(text: str, source_language: str) -> str:
    """
    Translate `text` from `source_language` into English using OpenAI.

    Returns the original text unchanged if:
    - `source_language` is English
    - `text` is blank
    """
    if not text or not text.strip():
        return ""

    if source_language.lower() == "english":
        return text

    settings = get_settings()
    lang_name = get_display_name(source_language)

    client = get_openai_client()

    logger.info("Translating %d chars from %s via OpenAI", len(text), lang_name)

    response = await client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.openai_max_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translation assistant. "
                    "Return ONLY the English translation — no explanations, "
                    "no notes, no original text. "
                    "If the text is already in English or is unintelligible, "
                    "return it as-is."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Translate the following {lang_name} text to English:\n\n{text}"
                ),
            },
        ],
    )

    choice = response.choices[0]
    content = choice.message.content
    return content.strip() if content else text


# ─── ElevenLabs token service ─────────────────────────────────────────────────

def create_scribe_token() -> str:
    """
    Mint a single-use ElevenLabs Scribe Realtime token.
    Tokens expire after 15 minutes.
    Raises RuntimeError if the ElevenLabs key is not configured.
    """
    settings = get_settings()

    if not settings.elevenlabs_configured:
        raise RuntimeError("ElevenLabs API key is not configured.")

    logger.info("Minting ElevenLabs single-use scribe token")

    response = httpx.post(
        "https://api.elevenlabs.io/v1/single-use-token/realtime_scribe",
        headers={"xi-api-key": settings.elevenlabs_api_key},
    )
    response.raise_for_status()
    return response.json()["token"]