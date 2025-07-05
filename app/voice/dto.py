from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Request DTOs
class GCTTSRequest(BaseModel):
    provider: str = Field(default='gctts', min_length=1)
    script: str = Field(..., min_length=1)
    voice_name: str = Field(..., min_length=1)
    language_code: str = Field(default='en-US', min_length=2)
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0)
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)
    volume_gain_db: float = Field(default=0.0, ge=-96.0, le=16.0)
    
    @field_validator('script')
    @classmethod
    def script_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'script' must not be whitespace only.")
        return value
    
    @field_validator('voice_name')
    @classmethod
    def voice_name_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'voice_name' must not be empty.")
        return value

class VoiceCloneRequest(BaseModel):
    voice_name: str = Field(..., min_length=1)
    preview_script: Optional[str] = None

class ElevenlabsTTSRequest(BaseModel):
    provider: str = Field(default='elevenlabs', min_length=1)
    script: str = Field(..., min_length=1)
    voice_id: str = Field(default='1l0C0QA9c9jN22EmWiB0', min_length=1)
    stability: float = Field(default=0.5, ge=0.0, le=1.0)
    speed: float = Field(default=1.0, ge=0.7, le=1.2)

    @field_validator('script')
    @classmethod
    def script_must_not_be_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'script' must not be whitespace only.")
        return value

    @field_validator('voice_id')
    @classmethod
    def voice_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field 'voice_id' must not be empty.")
        return value

# Response DTOs
class VoiceSchema(BaseModel):
    voice_name: str = Field(alias='name') 
    language_code: str  
    gender: str
    sample_rate_hertz: int = Field(alias='natural_sample_rate_hertz')
    preview_url: Optional[str] = None
    class Config:
        from_attributes = True

class VoiceListResponse(BaseModel):
    total_count: int
    message: str
    voices: list[VoiceSchema]

class VoiceCloneResponse(BaseModel):
    message: str
    voice_id: str
    preview_url: Optional[str] = None

class SceneAudioDetail(BaseModel):
    scene_index: int
    script: str
    audio_url: str
    duration: float = Field(..., description="Duration of the audio in seconds")

class MultiTTSResponse(BaseModel):
    message: str
    total_scenes: int
    voice_used: Optional[str] = None
    scenes: list[SceneAudioDetail]

class TTSResponse(BaseModel):
    message: str
    audio_url: str
    filename: str
    voice_used: Optional[str] = None