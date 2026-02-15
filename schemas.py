from pydantic import BaseModel, field_validator
from datetime import datetime, timezone


# ─── Language schemas ─────────────────────────────────────────────────────────

class LanguageInfo(BaseModel):
    id: str
    display_name: str
    native_name: str
    eleven_labs_supported: bool


class LanguagesResponse(BaseModel):
    languages: list[LanguageInfo]


# ─── Scribe token schemas ─────────────────────────────────────────────────────

class ScribeTokenResponse(BaseModel):
    token: str


# ─── Translation schemas ──────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    language: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text must not be empty")
        return v.strip()

    @field_validator("language")
    @classmethod
    def language_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("language must not be empty")
        return v.strip().lower()


class TranslateResponse(BaseModel):
    success: bool
    original: str
    translation: str
    is_english: bool


# ─── Health schema ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: dict[str, bool]

    @classmethod
    def ok(cls, anthropic_ok: bool, elevenlabs_ok: bool) -> "HealthResponse":
        return cls(
            status="ok",
            timestamp=datetime.now(timezone.utc).isoformat(),
            services={
                "anthropic": anthropic_ok,
                "elevenlabs": elevenlabs_ok,
            },
        )


# ─── Error schema ─────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None