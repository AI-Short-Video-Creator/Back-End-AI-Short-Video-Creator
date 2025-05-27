from pydantic import BaseModel, EmailStr, Field

class UserLoginDTO(BaseModel):
    """
    Data Transfer Object for user login.
    """
    email: EmailStr = Field(
        ...,
        description="User's email address for login.",
        examples=["user@example.com"],
        strip_whitespace=True
    )
    password: str = Field(
        ...,
        description="User's password.",
        min_length=8,
        max_length=128,
        examples=["MyS3cureP@ssw0rd!"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "email": "login@example.com",
                    "password": "securepassword123"
                }
            ]
        }
    }

class UserRegisterDTO(UserLoginDTO):
    """
    Data Transfer Object for user registration.
    Inherits email and password fields from UserLoginDTO.
    """
    fullname: str = Field(
        ...,
        description="User's full name.",
        min_length=2,
        max_length=100,
        strip_whitespace=True,
        examples=["John Doe"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newuser@example.com",
                    "password": "newSecurePassword123",
                    "fullname": "Jane Doe"
                }
            ]
        }
    }

# class UserResponseDTO(BaseModel):
#     """
#     Data Transfer Object for representing a user in API responses.
#     Excludes sensitive information like password.
#     """
#     id: str
#     email: EmailStr
#     fullname: str

#     model_config = {
#         "from_attributes": True,
#     }