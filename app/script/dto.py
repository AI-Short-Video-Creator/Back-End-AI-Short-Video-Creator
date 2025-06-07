from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class ScriptGenerateDTO(BaseModel):
    """
    DTO for script generation.
    """
    keywords: list[str] = Field(
        ...,
        description="Keywords for script generation",
        title="Keywords",
        max_length=100,
    )
    topic: str = Field(
        ...,
        description="Topic for script generation",
        title="Topic",
        max_length=100,
    )
    style: str = Field(
        ...,
        description="Style for script generation",
        title="Style",
        max_length=100,
    )
    language: str = Field(
        ...,
        description="Language for script generation",
        title="Language",
        max_length=100,
    )
    wordCount: int = Field(
        ...,
        description="Word count for script generation",
        title="Word Count",
        ge=1,
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

class ScriptGenerateResponseDTO(BaseModel):
    """
    DTO for script generation response.
    """
    script: str = Field(
        ...,
        description="Generated script",
        title="Script",
        max_length=10000,
    )
    status: Optional[str] = Field(
        None,
        description="Status of the script generation",
        title="Status",
        max_length=100,
    )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            set: lambda v: list(v),
        }
        use_enum_values = True
        validate_assignment = True