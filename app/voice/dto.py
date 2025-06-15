from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice_id: str = Field(default='1l0C0QA9c9jN22EmWiB0', min_length=1)

    @field_validator('text')
    @classmethod
    def text_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'text' must not be whitespace only.")
        return value

    @field_validator('voice_id')
    @classmethod
    def voice_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'voice_id' must not be empty.")
        return value

class TTSVoiceCloneRequest(BaseModel):
    text: str = Field(..., min_length=1)
    audio_base64: str = Field(..., min_length=10)

    @field_validator('text')
    @classmethod
    def text_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'text' must not be whitespace only.")
        return value

    @field_validator('audio_base64')
    @classmethod
    def audio_base64_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'audio_base64' must not be empty.")
        if not all(c.isalnum() or c in '+/=' for c in value):
            raise ValueError("Field 'audio_base64' must be a valid base64 string.")
        return value

class TTSResponse(BaseModel):
    message: str
    audio_path: str
    filename: str
    voice_used: Optional[str] = None

class VoiceListResponse(BaseModel):
    total_count: int
    message: str
    voices: list[dict]