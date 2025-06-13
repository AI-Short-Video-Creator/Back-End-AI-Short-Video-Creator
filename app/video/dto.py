from pydantic import BaseModel
from typing import List, Optional

class VideoGenerateDTO(BaseModel):
    image_urls: List[str]
    voices: List[str]
    fps: Optional[int] = None
    duration_per_image: Optional[float] = None
    add_captions: bool = True
    add_transitions: bool = True
    audio_url: Optional[str] = None