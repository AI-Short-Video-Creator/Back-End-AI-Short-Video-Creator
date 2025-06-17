from pydantic import BaseModel, Field, field_validator
from typing import Optional

class GoogleTTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language_code: str = Field(default='vi-VN')
    voice_name: str = Field(default='vi-VN-Wavenet-D')

    @field_validator('text')
    @classmethod
    def text_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'text' must not be whitespace only.")
        return value

class TTSResponse(BaseModel):
    message: str
    audio_path: str
    filename: str
    voice_used: Optional[str] = None
    language_code: Optional[str] = None