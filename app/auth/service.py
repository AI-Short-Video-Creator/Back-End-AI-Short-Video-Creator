import datetime
from flask_jwt_extended import create_access_token
from app import mongo, bcrypt
from app.auth.dto import UserLoginDTO, UserRegisterDTO
from typing import Tuple

class AuthService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def generate_token(self, user_id: str) -> str:
        """
        Generate a JWT token for the user.
        
        Args:
            user_id (str): The ID of the user.
        
        Returns:
            str: The generated JWT token.
        """
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=user_id, expires_delta=expires)
        return access_token

class UserService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.auth_service = AuthService()

    def generate_password_hash(self, password: str) -> str:
        """
        Generate a hashed password using bcrypt.
        
        Args:
            password (str): The plain text password to hash.
        
        Returns:
            str: The hashed password.
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password_hash(self, hashed_password: str, password: str) -> bool:
        """
        Check if the provided password matches the hashed password.
        
        Args:
            hashed_password (str): The hashed password stored in the database.
            password (str): The plain text password to check.
        
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        return bcrypt.check_password_hash(hashed_password, password)

    def login(self, user_login_dto: UserLoginDTO) -> Tuple[dict, str]:
        """
        Authenticate the user and generate a JWT token.

        Args:
            user_login_dto (UserLoginDTO): The login credentials of the user (already validated by schema).

        Returns:
            Tuple[dict, str]: A tuple containing the authenticated user and the generated token.
        """
        data = user_login_dto.model_dump()

        if not data.get("email") or not data.get("password"):
            raise ValueError("Please enter email and password")

        user = mongo.db.users.find_one({"email": data["email"]})
        if not user or not self.check_password_hash(user["password"], data["password"]):
            raise ValueError("Incorrect email or password")
        
        token = self.auth_service.generate_token(str(user["_id"]))
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "fullname": user.get("fullname", ""),
        }

        return user_data, token

    def register(self, user_register_dto: UserRegisterDTO) -> Tuple[dict, str]:
        """
        Register a new user.
        
        Args:
            user_register_dto (UserRegisterDTO): The registration details of the user.
        
        Returns:
            Tuple[dict, str]: A tuple containing the registered user data and the generated token.
        """
        data = user_register_dto.model_dump()
        existing_user = mongo.db.users.find_one({"email": data["email"]})
        if existing_user:
            raise ValueError("Email already exists")

        new_user = {
            "email": data["email"],
            "fullname": data["fullname"],
            "password": self.generate_password_hash(data["password"])
        }
        mongo.db.users.insert_one(new_user)

        token = self.auth_service.generate_token(str(new_user["_id"]))
        user_data = {
            "id": str(new_user["_id"]),
            "email": new_user["email"],
            "fullname": new_user["fullname"],
        }

        return user_data, token