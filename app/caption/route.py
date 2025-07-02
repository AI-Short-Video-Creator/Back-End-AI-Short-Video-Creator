from flask import Blueprint, jsonify, Response, request
from .service import fetch_captions
import json

caption_bp = Blueprint('caption', __name__)

@caption_bp.route('/social', methods=['GET'])
def get_caption_gpt():
    video_context = request.args.get('video_context')
    lang = request.args.get('lang', 'en')  # mặc định tiếng Anh
    result = fetch_captions(video_context, lang)
    if isinstance(result, dict) and result.get('error'):
        return jsonify(result), 500
    
    json_data = json.dumps(result, indent=2, ensure_ascii=False)
    return Response(json_data, mimetype='application/json; charset=utf-8')