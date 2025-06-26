from pydantic import BaseModel
from typing import Optional, Dict

class SharedOnDTO(BaseModel):
    facebook: bool = False
    youtube: bool = False
    tiktok: bool = False

class LinkDTO(BaseModel):
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None

class SocialVideoDTO(BaseModel):
    id: str
    sharedOn: SharedOnDTO
    link: LinkDTO