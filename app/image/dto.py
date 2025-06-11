from pydantic import BaseModel

class ImageGenerateDTO(BaseModel):
    script: str
    owner_id: str
    themes: str = "cartoon"  # Default to cartoon theme