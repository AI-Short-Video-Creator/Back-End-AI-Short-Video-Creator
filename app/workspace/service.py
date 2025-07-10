import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from flask import current_app
from app.extentions import mongo
from app.workspace.dto import (
    WorkspaceCreateRequest, 
    WorkspaceUpdateRequest, 
    WorkspaceResponse, 
    WorkspaceListItem,
    WorkspaceListResponse
)
import logging

logger = logging.getLogger(__name__)

class WorkspaceService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def create_workspace(self, user_id: str, dto: WorkspaceCreateRequest) -> WorkspaceResponse:
        """Create a new workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            image_urls_data = []
            if dto.image_urls is not None:
                for image in dto.image_urls:
                    image_urls_data.append(image.model_dump(by_alias=True))
            
            generated_audio_data = None
            if dto.generated_audio_path:
                generated_audio_data = dto.generated_audio_path.model_dump(by_alias=True)
            
            default_personal_style = {
                "style": "informative",
                "language": "en",
                "wordCount": 100,
                "tone": "neutral",
                "perspective": "third",
                "humor": "none",
                "quotes": "no"
            }
            
            default_voice_config = {
                "tab": "google",
                "googleCloudVoice": {
                    "name": "en-US-Standard-A",
                    "languageCode": "en-US",
                    "speakingRate": 1.0,
                    "pitch": 0.0,
                    "volume": 0.0
                },
                "elevenLabsClonedVoice": {
                    "voiceId": None,
                    "stability": 0.5,
                    "speed": 1.0,
                    "state": "idle",
                    "previewUrl": None
                }
            }
            
            workspace_data = {
                "_id": workspace_id,
                "user_id": user_id,
                "name": dto.name,
                "description": dto.description,
                "thumbnail": image_urls_data[0]["image_url"] if image_urls_data else None,
                "keyword": dto.keyword,
                "personal_style": dto.personal_style.model_dump(by_alias=True) if dto.personal_style else default_personal_style,
                "script": dto.script,
                "can_regenerate": dto.can_regenerate,
                "voice_config": dto.voice_config.model_dump(by_alias=True) if dto.voice_config else default_voice_config,
                "generated_audio_path": generated_audio_data if generated_audio_data else None,
                "image_urls": image_urls_data,
                "session_id": dto.session_id,
                "video_url": dto.video_url,
                "video_title": dto.video_title,
                "thumbnail_url": dto.thumbnail_url,
                "total_steps": dto.total_steps,
                "current_step": dto.current_step,
                "is_completed": dto.is_completed,
                "created_at": now,
                "updated_at": now
            }
            
            result = mongo.db.workspaces.insert_one(workspace_data)
            
            if result.inserted_id:
                created_workspace = mongo.db.workspaces.find_one({"_id": workspace_id})
                return self._convert_to_response(created_workspace)
            else:
                raise Exception("Failed to create workspace")
                
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            raise e

    def get_workspace_by_id(self, workspace_id: str, user_id: str) -> Optional[WorkspaceResponse]:
        """Get workspace by ID and user ID"""
        try:
            workspace = mongo.db.workspaces.find_one({
                "_id": workspace_id,
                "user_id": user_id
            })
            
            if workspace:
                return self._convert_to_response(workspace)
            return None
            
        except Exception as e:
            logger.error(f"Error getting workspace {workspace_id}: {e}")
            raise e

    def get_workspaces_by_user(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 12, 
        search: Optional[str] = None
    ) -> WorkspaceListResponse:
        """Get workspaces by user ID with pagination and search"""
        try:
            query = {"user_id": user_id}
            
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                ]
            
            skip = (page - 1) * limit
            
            total = mongo.db.workspaces.count_documents(query)
            
            # Get workspaces with pagination
            workspaces = list(
                mongo.db.workspaces.find(query)
                .sort("updated_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            workspace_items = [self._convert_to_list_item(workspace) for workspace in workspaces]
            
            return WorkspaceListResponse(
                data=workspace_items,
                total=total,
                page=page,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error getting workspaces for user {user_id}: {e}")
            raise e

    def update_workspace(
        self, 
        workspace_id: str, 
        user_id: str, 
        dto: WorkspaceUpdateRequest
    ) -> Optional[WorkspaceResponse]:
        """Update workspace"""
        try:
            update_data = {"updated_at": datetime.utcnow()}
            
            if dto.name is not None:
                update_data["name"] = dto.name
            if dto.description is not None:
                update_data["description"] = dto.description
            if dto.keyword is not None:
                update_data["keyword"] = dto.keyword
            if dto.personal_style is not None:
                update_data["personal_style"] = dto.personal_style.model_dump(by_alias=True)
            if dto.script is not None:
                update_data["script"] = dto.script
            if dto.can_regenerate is not None:
                update_data["can_regenerate"] = dto.can_regenerate
            if dto.voice_config is not None:
                update_data["voice_config"] = dto.voice_config.model_dump(by_alias=True)
            if dto.generated_audio_path is not None:
                generated_audio_data = dto.generated_audio_path.model_dump(by_alias=True)
                update_data["generated_audio_path"] = generated_audio_data
            if dto.image_urls is not None:
                image_urls_data = []
                for image in dto.image_urls:
                    image_urls_data.append(image.model_dump(by_alias=True))
                update_data["image_urls"] = image_urls_data
                # Update thumbnail if first image is available
                if dto.image_urls and len(dto.image_urls) > 0:
                    update_data["thumbnail"] = dto.image_urls[0].image_url
            if dto.session_id is not None:
                update_data["session_id"] = dto.session_id
            if dto.video_url is not None:
                update_data["video_url"] = dto.video_url
            if dto.video_title is not None:
                update_data["video_title"] = dto.video_title
            if dto.thumbnail_url is not None:
                update_data["thumbnail_url"] = dto.thumbnail_url
            if dto.total_steps is not None:
                update_data["total_steps"] = dto.total_steps
            if dto.current_step is not None:
                update_data["current_step"] = dto.current_step
            if dto.is_completed is not None:
                update_data["is_completed"] = dto.is_completed
            
            result = mongo.db.workspaces.find_one_and_update(
                {"_id": workspace_id, "user_id": user_id},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                return self._convert_to_response(result)
            return None
            
        except Exception as e:
            logger.error(f"Error updating workspace {workspace_id}: {e}")
            raise e

    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace"""
        try:
            result = mongo.db.workspaces.delete_one({
                "_id": workspace_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting workspace {workspace_id}: {e}")
            raise e

    def duplicate_workspace(
        self, 
        workspace_id: str, 
        user_id: str, 
        new_name: str
    ) -> Optional[WorkspaceResponse]:
        """Duplicate workspace"""
        try:
            original = mongo.db.workspaces.find_one({
                "_id": workspace_id,
                "user_id": user_id
            })
            
            if not original:
                return None
            
            new_workspace_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            new_workspace = original.copy()
            new_workspace["_id"] = new_workspace_id
            new_workspace["name"] = new_name
            new_workspace["created_at"] = now
            new_workspace["updated_at"] = now
            
            result = mongo.db.workspaces.insert_one(new_workspace)
            
            if result.inserted_id:
                created_workspace = mongo.db.workspaces.find_one({"_id": new_workspace_id})
                return self._convert_to_response(created_workspace)
            else:
                raise Exception("Failed to duplicate workspace")
                
        except Exception as e:
            logger.error(f"Error duplicating workspace {workspace_id}: {e}")
            raise e

    def _convert_to_response(self, workspace_doc: Dict[str, Any]) -> WorkspaceResponse:
        """Convert MongoDB document to WorkspaceResponse"""
        return WorkspaceResponse(
            id=workspace_doc["_id"],
            name=workspace_doc["name"],
            description=workspace_doc.get("description"),
            thumbnail=workspace_doc.get("thumbnail"),
            keyword=workspace_doc["keyword"],
            personalStyle=workspace_doc["personal_style"],
            script=workspace_doc.get("script"),
            canRegenerate=workspace_doc["can_regenerate"],
            voiceConfig=workspace_doc["voice_config"],
            generatedAudioPath=workspace_doc.get("generated_audio_path"),
            imageUrls=workspace_doc.get("image_urls", []),
            sessionId=workspace_doc.get("session_id"),
            videoUrl=workspace_doc.get("video_url"),
            videoTitle=workspace_doc.get("video_title"),
            thumbnailUrl=workspace_doc.get("thumbnail_url"),
            totalSteps=workspace_doc["total_steps"],
            currentStep=workspace_doc["current_step"],
            isCompleted=workspace_doc["is_completed"],
            createdAt=workspace_doc["created_at"],
            updatedAt=workspace_doc["updated_at"],
            userId=workspace_doc["user_id"]
        )

    def _convert_to_list_item(self, workspace_doc: Dict[str, Any]) -> WorkspaceListItem:
        """Convert MongoDB document to WorkspaceListItem"""
        return WorkspaceListItem(
            id=workspace_doc["_id"],
            name=workspace_doc["name"],
            description=workspace_doc.get("description"),
            thumbnail=workspace_doc.get("thumbnail"),
            keyword=workspace_doc["keyword"],
            currentStep=workspace_doc["current_step"],
            totalSteps=workspace_doc["total_steps"],
            isCompleted=workspace_doc["is_completed"],
            createdAt=workspace_doc["created_at"],
            updatedAt=workspace_doc["updated_at"]
        )