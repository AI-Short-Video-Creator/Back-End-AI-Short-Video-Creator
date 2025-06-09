from flask import Blueprint, jsonify, request
from app.script.service import ScriptService
from app.script.dto import ScriptGenerateDTO, ScriptGenerateResponseDTO
from flask_jwt_extended import jwt_required, get_jwt_identity

class ScriptController:
    def __init__(self):
        self.service = ScriptService()
        self.script_bp = Blueprint('script_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.script_bp.add_url_rule('/', view_func=self.script, methods=['POST'])

    @jwt_required()
    def script(self):
        """Script route handler."""
        try:
            data = request.json
            dto = ScriptGenerateDTO(**data)
            user_id = get_jwt_identity()  # Get the user ID from JWT token
            print(f"User ID: {user_id}")  # Debugging line to check user ID

            script = self.service.generate_script(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
script_controller = ScriptController()
script_bp = script_controller.script_bp