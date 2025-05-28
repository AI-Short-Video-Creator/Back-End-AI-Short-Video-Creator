from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

class VideoGenerateDTO(BaseModel):
    """
    DTO for video generation with advanced options.
    """
    image_paths: Optional[List[str]] = Field(
        None,
        description="List of paths to images to be included in the video",
        title="Image Paths",
    )
    
    fps: Optional[int] = Field(
        None,
        description="Frames per second for the video",
        title="FPS",
        ge=1,
        le=60
    )
    
    duration_per_image: Optional[float] = Field(
        None,
        description="Duration in seconds to show each image",
        title="Duration Per Image",
        ge=0.5,
        le=10
    )
    
    add_transitions: Optional[bool] = Field(
        False,
        description="Whether to add fade transitions between images",
        title="Add Transitions"
    )
    
    add_captions: Optional[bool] = Field(
        False,
        description="Whether to add captions to images",
        title="Add Captions"
    )
    
    captions: Optional[List[str]] = Field(
        None,
        description="List of captions for each image",
        title="Captions"
    )
    
    audio_path: Optional[str] = Field(
        None,
        description="Path to audio file to add as background music",
        title="Audio Path"
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