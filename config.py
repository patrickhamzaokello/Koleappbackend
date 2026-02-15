from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── API keys ──────────────────────────────────────────────────────────────
    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    openai_api_key: str = ""

    # ── Server ────────────────────────────────────────────────────────────────
    port: int = 3000
    allowed_origins: list[str] = ["*"]

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_per_minute: int = 60

    # ── Claude model ──────────────────────────────────────────────────────────
    claude_model: str = "claude-opus-4-5-20251101"
    claude_max_tokens: int = 1024

    # ── OpenAI model ─────────────────────────────────────────────────────────
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1024

    @field_validator("anthropic_api_key", "elevenlabs_api_key", "openai_api_key", mode="before")
    @classmethod
    def strip_key(cls, v: str) -> str:
        return v.strip() if v else ""

    @property
    def anthropic_configured(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def elevenlabs_configured(self) -> bool:
        return bool(self.elevenlabs_api_key)

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()