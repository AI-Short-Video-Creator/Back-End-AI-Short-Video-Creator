from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class ImageGenerateDTO(BaseModel):
    """
    DTO for script generation.
    """
    script: str = Field(
        ...,
        description="Keywords for script generation",
        title="Keywords",
        max_length=5000,
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
