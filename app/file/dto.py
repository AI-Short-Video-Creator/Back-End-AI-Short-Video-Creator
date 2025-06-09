from pydantic import BaseModel, Field, ConfigDict
from typing import List



class UploadImageDTO(BaseModel):
    """
    DTO for uploading images.
    """
    images: List[ImageItem] = Field(
        ...,
        description="List of images with file path and file id",
        title="Images",
        max_length=100,
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            set: lambda v: list(v),
        }
        use_enum_values = True
        validate_assignment = True
        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            validate_default=True,
        )

class UploadVideoDTO(BaseModel):
    """
    DTO for uploading images.
    """
    images: VideoItem = Field(
        ...,
        description="video path to upload",
        title="video path and id",
        max_length=100,
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            set: lambda v: list(v),
        }
        use_enum_values = True
        validate_assignment = True
        model_config = ConfigDict(
            from_attributes=True,
            populate_by_name=True,
            validate_default=True,
        )