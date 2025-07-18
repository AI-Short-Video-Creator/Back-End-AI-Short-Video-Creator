from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PersonalStyle(BaseModel):
    style: str = Field(..., description="Video style")
    language: str = Field(..., description="Language code")
    word_count: int = Field(..., description="Word count", alias="wordCount")
    tone: str = Field(..., description="Tone of voice")
    perspective: str = Field(..., description="Perspective")
    humor: str = Field(default="none", description="Humor level")
    quotes: str = Field(default="no", description="Include quotes")

class GoogleCloudVoice(BaseModel):
    name: str = Field(..., description="Voice name")
    language_code: str = Field(..., description="Language code", alias="languageCode")
    speaking_rate: float = Field(default=1.0, description="Speaking rate", alias="speakingRate")
    pitch: float = Field(default=0.0, description="Voice pitch")
    volume: float = Field(default=0.0, description="Voice volume")

class ElevenLabsClonedVoice(BaseModel):
    voice_id: Optional[str] = Field(None, description="Voice ID", alias="voiceId")
    stability: float = Field(default=0.5, description="Voice stability")
    speed: float = Field(default=1.0, description="Voice speed")
    state: str = Field(default="idle", description="Voice state")
    preview_url: Optional[str] = Field(None, description="Preview URL", alias="previewUrl")

class VoiceConfig(BaseModel):
    tab: str = Field(..., description="Active voice tab")
    google_cloud_voice: GoogleCloudVoice = Field(..., alias="googleCloudVoice")
    eleven_labs_cloned_voice: ElevenLabsClonedVoice = Field(..., alias="elevenLabsClonedVoice")

class MediaInfo(BaseModel):
    image_id: str = Field(..., description="Image ID")
    image_url: str = Field(..., description="Image URL")
    scene: str = Field(..., description="Scene description")
    voice: str = Field(..., description="Voice description")

class SceneAudioDetail(BaseModel):
    """Mô tả chi tiết audio cho một cảnh"""
    scene_index: int
    script: str
    audio_url: str
    duration: float = Field(..., description="Thời lượng của audio tính bằng giây")

class MultiTTSResponse(BaseModel):
    """Response cho việc tạo TTS theo nhiều cảnh"""
    message: str
    total_scenes: int
    voice_used: Optional[str] = None
    scenes: list[SceneAudioDetail]

class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")
    keyword: Optional[str] = Field("", description="Main keyword")
    personal_style: Optional[PersonalStyle] = Field(None, alias="personalStyle")
    script: Optional[str] = Field("", description="Generated script")
    can_regenerate: bool = Field(True, alias="canRegenerate")
    voice_config: Optional[VoiceConfig] = Field(None, alias="voiceConfig")
    generated_audio_path: Optional[MultiTTSResponse] = Field(None, alias="generatedAudioPath")
    image_urls: List[MediaInfo] = Field(default_factory=list, alias="imageUrls")
    session_id: Optional[str] = Field(None, alias="sessionId")
    video_url: Optional[str] = Field(None, alias="videoUrl")
    video_title: Optional[str] = Field(None, alias="videoTitle")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    total_steps: int = Field(default=5, alias="totalSteps")
    current_step: int = Field(default=1, alias="currentStep")
    is_completed: bool = Field(default=False, alias="isCompleted")

class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    keyword: Optional[str] = None
    personal_style: Optional[PersonalStyle] = Field(None, alias="personalStyle")
    script: Optional[str] = None
    can_regenerate: Optional[bool] = Field(None, alias="canRegenerate")
    voice_config: Optional[VoiceConfig] = Field(None, alias="voiceConfig")
    generated_audio_path: Optional[MultiTTSResponse] = Field(None, alias="generatedAudioPath")
    image_urls: Optional[List[MediaInfo]] = Field(None, alias="imageUrls")
    session_id: Optional[str] = Field(None, alias="sessionId")
    video_url: Optional[str] = Field(None, alias="videoUrl")
    video_title: Optional[str] = Field(None, alias="videoTitle")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    total_steps: Optional[int] = Field(None, alias="totalSteps")
    current_step: Optional[int] = Field(None, alias="currentStep")
    is_completed: Optional[bool] = Field(None, alias="isCompleted")

class WorkspaceDuplicateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="New workspace name")

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    thumbnail: Optional[str]
    keyword: str
    personal_style: PersonalStyle = Field(..., alias="personalStyle")
    script: Optional[str]
    can_regenerate: bool = Field(..., alias="canRegenerate")
    voice_config: VoiceConfig = Field(..., alias="voiceConfig")
    generated_audio_path: Optional[MultiTTSResponse] = Field(None, alias="generatedAudioPath")
    image_urls: List[MediaInfo] = Field(..., alias="imageUrls")
    session_id: Optional[str] = Field(None, alias="sessionId")
    video_url: Optional[str] = Field(None, alias="videoUrl")
    video_title: Optional[str] = Field(None, alias="videoTitle")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    total_steps: int = Field(..., alias="totalSteps")
    current_step: int = Field(..., alias="currentStep")
    is_completed: bool = Field(..., alias="isCompleted")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    user_id: str = Field(..., alias="userId")

class WorkspaceListItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    thumbnail: Optional[str]
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    keyword: str
    current_step: int = Field(..., alias="currentStep")
    total_steps: int = Field(..., alias="totalSteps")
    is_completed: bool = Field(..., alias="isCompleted")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

class WorkspaceListResponse(BaseModel):
    data: List[WorkspaceListItem]
    total: int
    page: int
    limit: int
