from datetime import datetime
from app.extentions import mongo

def insert_image(file_id: str, url: str, scene: str, voice: str, owner_id: str, session_id: str, status: str, metadata: dict):
    """
    Insert an image document into the MongoDB images collection.
    
    Args:
        file_id: Unique identifier for the image
        url: URL of the image
        scene: Scene description
        voice: Narration or dialogue text
        owner_id: ID of the user who owns the image
        session_id: Session ID for grouping images
        status: Status of the image (e.g., pending, regenerated)
        metadata: Additional metadata (e.g., themes)
    """
    try:
        metadata["session_id"] = session_id
        document = {
            "file_id": file_id,
            "url": url,
            "scene": scene,
            "voice": voice,
            "owner_id": owner_id,
            "video_id": None,
            "status": status,
            "created_at": datetime.utcnow(),
            "metadata": metadata
        }
        mongo.db.images.insert_one(document)
    except Exception as e:
        raise Exception(f"Failed to insert image into MongoDB: {str(e)}")