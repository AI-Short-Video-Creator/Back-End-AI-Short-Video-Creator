from flask import Blueprint, jsonify, request
from app.script.service import ScriptService
from app.script.dto import ScriptGenerateDTO, ScriptGenerateResponseDTO

class ScriptController:
    def __init__(self):
        self.service = ScriptService()
        self.script_bp = Blueprint('script_bp', __name__)

        self._register_routes()

    def _register_routes(self):
        self.script_bp.add_url_rule('/', view_func=self.script, methods=['POST'])

    def script(self):
        """Script route handler."""
        try:
            data = request.json
            dto = ScriptGenerateDTO(**data)

            script = self.service.generate_script(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
script_controller = ScriptController()
script_bp = script_controller.script_bp