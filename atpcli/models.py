"""Pydantic models for Spice."""

from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from atpcli.constants import SPICE_COLLECTION_NAME, SPICE_MAX_TEXT_LENGTH


class SpiceNote(BaseModel):
    """Model for a Spice note record."""

    url: str = Field(..., description="The fully-qualified URL being annotated")
    text: str = Field(..., max_length=SPICE_MAX_TEXT_LENGTH, description="The annotation text")
    createdAt: str = Field(..., description="ISO 8601 / RFC 3339 datetime of record creation")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL has scheme and host."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL must include scheme and host (e.g., https://example.com)")
        return v

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that text is not empty."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v

    def to_record(self) -> dict:
        """Convert to atproto record format."""
        return {
            "url": self.url,
            "text": self.text,
            "createdAt": self.createdAt,
            "$type": SPICE_COLLECTION_NAME,
        }
