from flask import Blueprint, jsonify, Response, request
from .service import fetch_trending_topics
import json

trending_bp = Blueprint('trending', __name__)

@trending_bp.route('/google', methods=['GET'])
def get_trending_gpt():
    country = request.args.get('country', 'Vietnam')
    topic = request.args.get('topic', 'technology')
    
    result = fetch_trending_topics(country, topic)
    
    if isinstance(result, dict) and result.get('error'):
        return jsonify(result), 500

    json_data = json.dumps(result, indent=2, ensure_ascii=False)
    return Response(json_data, mimetype='application/json; charset=utf-8')
