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
        self.script_bp.add_url_rule('/topics/wiki', view_func=self.get_wiki_trends, methods=['GET'])
        self.script_bp.add_url_rule('/topics/google', view_func=self.get_google_trends, methods=['GET'])
        self.script_bp.add_url_rule('/topics/youtube', view_func=self.get_youtube_trends, methods=['GET'])
    
    @jwt_required()
    def script(self):
        """Script route handler."""
        try:
            data = request.json
            dto = ScriptGenerateDTO(**data)

            script = self.service.generate_script(dto)
            return jsonify({"data": script}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @jwt_required()
    def get_wiki_trends(self):
        """Get trending topics from Wikipedia."""
        try:
            keyword = request.args.get('keyword')
            limit = int(request.args.get('limit', 5))
            topics = self.service.get_topics_from_wiki(keyword, limit)
            return jsonify(topics), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
    @jwt_required()
    def get_google_trends(self):
        """Get trending topics from Google."""
        try:
            keyword = request.args.get('keyword')
            limit = int(request.args.get('limit', 5))
            print(f"Keyword: {keyword}, Limit: {limit}")  # Debugging line to check keyword and limit
            topics = self.service.get_topics_from_google(keyword, limit)
            return jsonify(topics), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @jwt_required()
    def get_youtube_trends(self):
        """Get trending topics from YouTube."""
        try:
            keyword = request.args.get('keyword')
            limit = int(request.args.get('limit', 5))
            topics = self.service.get_topics_from_youtube(keyword, limit)
            return jsonify(topics), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
script_controller = ScriptController()
script_bp = script_controller.script_bp