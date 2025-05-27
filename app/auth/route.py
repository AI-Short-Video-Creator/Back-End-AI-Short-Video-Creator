from flask import Blueprint, jsonify, request
from app.auth.service import UserService
from app.auth.dto import UserLoginDTO, UserRegisterDTO

class UserController:
    def __init__(self):
        self.service = UserService()
        self.user_bp = Blueprint('user_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.user_bp.add_url_rule('/login', view_func=self.login, methods=['POST'])
        self.user_bp.add_url_rule('/register', view_func=self.register, methods=['POST'])

    def login(self):
        """Login route handler."""
        try:
            data = request.json
            dto = UserLoginDTO(**data)

            user, token = self.service.login(dto)
            return jsonify({"user": user, "access_token": token}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def register(self):
        """Register route handler."""
        try:
            data = request.json
            dto = UserRegisterDTO(**data)

            user_id = self.service.register(dto)
            return jsonify({"user_id": user_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

user_controller = UserController()
user_bp = user_controller.user_bp
