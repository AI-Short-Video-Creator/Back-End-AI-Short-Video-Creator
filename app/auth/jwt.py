from flask_jwt_extended import JWTManager
from flask import jsonify

jwt = JWTManager()

@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    return jsonify({
        "error": "Unauthorized",
        "message": "Missing or invalid JWT"
    }), 401

@jwt.invalid_token_loader
def custom_invalid_token_response(error):
    return jsonify({
        "error": "Invalid token",
        "message": error
    }), 401

@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token expired",
        "message": "The token has expired"
    }), 401
