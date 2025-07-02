from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.workspace.service import WorkspaceService
from app.workspace.dto import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
    WorkspaceDuplicateRequest
)
import logging

logger = logging.getLogger(__name__)

class WorkspaceController:
    def __init__(self):
        self.service = WorkspaceService()
        self.workspace_bp = Blueprint('workspace_bp', __name__)
        self._register_routes()

    def _register_routes(self):
        self.workspace_bp.add_url_rule('', view_func=self.get_workspaces, methods=['GET'])
        self.workspace_bp.add_url_rule('', view_func=self.create_workspace, methods=['POST'])
        self.workspace_bp.add_url_rule('/<string:workspace_id>', view_func=self.get_workspace, methods=['GET'])
        self.workspace_bp.add_url_rule('/<string:workspace_id>', view_func=self.update_workspace, methods=['PUT'])
        self.workspace_bp.add_url_rule('/<string:workspace_id>', view_func=self.delete_workspace, methods=['DELETE'])
        self.workspace_bp.add_url_rule('/<string:workspace_id>/duplicate', view_func=self.duplicate_workspace, methods=['POST'])

    @jwt_required()
    def get_workspaces(self):
        """Get list of workspaces"""
        try:
            user_id = get_jwt_identity()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 12))
            search = request.args.get('search')
            
            result = self.service.get_workspaces_by_user(user_id, page, limit, search)
            return jsonify(result.model_dump(by_alias=True)), 200
            
        except ValueError as ve:
            logger.error(f"Validation error in get_workspaces: {ve}")
            return jsonify({"message": "Invalid pagination parameters"}), 400
        except Exception as e:
            logger.error(f"Error getting workspaces: {e}")
            return jsonify({"message": "Failed to get workspaces"}), 500

    @jwt_required()
    def get_workspace(self, workspace_id):
        """Get workspace by ID"""
        try:
            user_id = get_jwt_identity()
            workspace = self.service.get_workspace_by_id(workspace_id, user_id)
            
            if not workspace:
                return jsonify({"message": "Workspace not found"}), 404
            
            return jsonify(workspace.model_dump(by_alias=True)), 200
            
        except Exception as e:
            logger.error(f"Error getting workspace {workspace_id}: {e}")
            return jsonify({"message": "Failed to get workspace"}), 500

    @jwt_required()
    def create_workspace(self):
        """Create new workspace"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            dto = WorkspaceCreateRequest(**data)
            workspace = self.service.create_workspace(user_id, dto)
            
            return jsonify(workspace.model_dump(by_alias=True)), 201
            
        except ValidationError as ve:
            logger.error(f"Validation error in create_workspace: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            return jsonify({"message": "Failed to create workspace"}), 500

    @jwt_required()
    def update_workspace(self, workspace_id):
        """Update workspace"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            dto = WorkspaceUpdateRequest(**data)
            workspace = self.service.update_workspace(workspace_id, user_id, dto)
            
            if not workspace:
                return jsonify({"message": "Workspace not found"}), 404
            
            return jsonify(workspace.model_dump(by_alias=True)), 200
            
        except ValidationError as ve:
            logger.error(f"Validation error in update_workspace: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error updating workspace {workspace_id}: {e}")
            return jsonify({"message": "Failed to update workspace"}), 500

    @jwt_required()
    def delete_workspace(self, workspace_id):
        """Delete workspace"""
        try:
            user_id = get_jwt_identity()
            success = self.service.delete_workspace(workspace_id, user_id)
            
            if not success:
                return jsonify({"message": "Workspace not found"}), 404
            
            return '', 204
            
        except Exception as e:
            logger.error(f"Error deleting workspace {workspace_id}: {e}")
            return jsonify({"message": "Failed to delete workspace"}), 500

    @jwt_required()
    def duplicate_workspace(self, workspace_id):
        """Duplicate workspace"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            dto = WorkspaceDuplicateRequest(**data)
            workspace = self.service.duplicate_workspace(workspace_id, user_id, dto.name)
            
            if not workspace:
                return jsonify({"message": "Workspace not found"}), 404
            
            return jsonify(workspace.model_dump(by_alias=True)), 201
            
        except ValidationError as ve:
            logger.error(f"Validation error in duplicate_workspace: {ve}")
            return jsonify({"message": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error duplicating workspace {workspace_id}: {e}")
            return jsonify({"message": "Failed to duplicate workspace"}), 500


workspace_controller_instance = WorkspaceController()
workspace_bp = workspace_controller_instance.workspace_bp