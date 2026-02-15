import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status

from config import get_settings
from languages import LANGUAGES
from schemas import (
    ErrorResponse,
    HealthResponse,
    LanguageInfo,
    LanguagesResponse,
    ScribeTokenResponse,
    TranslateRequest,
    TranslateResponse,
)
from services import create_scribe_token, translate_with_claude, translate_with_openai

logger = logging.getLogger(__name__)

# ─── Health router ────────────────────────────────────────────────────────────

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse.ok(
        anthropic_ok=settings.anthropic_configured,
        elevenlabs_ok=settings.elevenlabs_configured,
    )


# ─── API router ───────────────────────────────────────────────────────────────

api_router = APIRouter(prefix="/api", tags=["API"])


@api_router.get(
    "/languages",
    response_model=LanguagesResponse,
    summary="List supported languages",
)
async def list_languages() -> LanguagesResponse:
    """Return all languages the app supports, with ElevenLabs availability flag."""
    return LanguagesResponse(
        languages=[
            LanguageInfo(
                id=lang.id,
                display_name=lang.display_name,
                native_name=lang.native_name,
                eleven_labs_supported=lang.eleven_code is not None,
            )
            for lang in LANGUAGES.values()
        ]
    )


@api_router.get(
    "/scribe-token",
    response_model=ScribeTokenResponse,
    summary="Mint a single-use ElevenLabs Scribe token",
    responses={
        500: {"model": ErrorResponse, "description": "Token generation failed"},
    },
)
async def get_scribe_token() -> ScribeTokenResponse:
    """
    Generates a single-use ElevenLabs Realtime Scribe token (valid 15 min).
    The app uses this token to open a WebSocket directly to ElevenLabs —
    the real API key is never exposed to the client.
    """
    try:
        token = create_scribe_token()
        return ScribeTokenResponse(token=token)
    except RuntimeError as exc:
        logger.error("Scribe token config error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error minting scribe token")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate transcription token.",
        )


@api_router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate a committed transcript to English",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request body"},
        500: {"model": ErrorResponse, "description": "Translation failed"},
    },
)
async def translate(body: TranslateRequest) -> TranslateResponse:
    """
    Accepts a committed transcript and source language.
    Returns the original text plus its English translation via Claude.
    If the source language is English, translation == original.
    """
    try:
        # translation = await translate_with_claude(
        #     text=body.text,
        #     source_language=body.language,
        # )
        translation  = await translate_with_openai(
            text=body.text,
            source_language=body.language,
        )
        return TranslateResponse(
            success=True,
            original=body.text,
            translation=translation,
            is_english=body.language == "english",
        )
    except Exception as exc:
        logger.exception("Translation error for language=%s", body.language)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed. Please try again.",
        )