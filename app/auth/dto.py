from pydantic import BaseModel, EmailStr, Field, root_validator

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
    )

    @root_validator(pre=True)
    def validate_password(cls, values):
        password = values.get("password")
        if not password or len(password) < 8:
            raise ValueError("Invalid password. It must be at least 8 characters long.")
        return values
    
    @root_validator(pre=True)
    def validate_email(cls, values):
        email = values.get("email")
        if not email or "@" not in email:
            raise ValueError("Invalid email address.")
        return values

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

    @root_validator(pre=True)
    def validate_fullname(cls, values):
        fullname = values.get("fullname")
        if not fullname or len(fullname) < 2:
            raise ValueError("Invalid full name. It must be at least 2 characters long.")
        return values

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