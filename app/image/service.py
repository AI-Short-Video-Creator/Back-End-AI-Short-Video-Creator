import os
import requests
from app.image.dto import ImageGenerateDTO
import uuid
import io
from dotenv import load_dotenv
from app.file.service import FileService
from app.image.repo import insert_image
from flask_jwt_extended import get_jwt_identity
import re

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class ImageService:
    _instance = None
    
    HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.file_service = FileService()
        if not HF_TOKEN:
            print("Warning: HF_TOKEN environment variable not set.")

    def generate_image(self, dto: ImageGenerateDTO) -> dict:
        """
        Generate images from a script by splitting it into scenes.
        
        Args:
            dto: Data Transfer Object containing the script and session_id
            
        Returns:
            dict: Contains session_id and list of image info (image_id, image_url, sentence)
        """
        if not HF_TOKEN:
            raise ValueError("HF_TOKEN not configured.")
        
        user_id = get_jwt_identity()
        print(f"User ID at image service: {user_id}")
        
        session_id = str(uuid.uuid4())  # Generate unique session_id
        full_script = dto.script
        sentences = re.findall(r"\*\*\[Scene\s*\d+:\s*(.*?)\]\*\*", full_script)
        sentences = [s.strip() for s in sentences if s.strip()]
        print(f"Split script into {len(sentences)} scenes")
        
        image_data = []
        headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
        
        for i, sentence in enumerate(sentences):
            if len(sentence) < 10:
                continue
                
            payload = {
                "inputs": sentence,
                "parameters": {
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }
            
            try:
                print(f"Generating image for scene {i+1}/{len(sentences)}: {sentence[:50]}...")
                response = requests.post(self.HF_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                
                if response.headers.get("content-type", "").startswith("image/"):
                    image_id = str(uuid.uuid4())
                    image_bytes = io.BytesIO(response.content)
                    image_url = self.file_service.uploadImages(image_bytes, image_id)
                    
                    # Insert into MongoDB with status and session_id
                    insert_image(
                        file_id=image_id,
                        url=image_url,
                        script=sentence,
                        owner_id=user_id,
                        session_id=session_id,
                        status="pending",
                        metadata={}
                    )
                    image_data.append({"image_id": image_id, "image_url": image_url, "sentence": sentence})
                    print(f"Uploaded image {image_id} to Cloudinary")
                
                else:
                    result = response.json()
                    if isinstance(result, dict) and "error" in result:
                        print(f"API Error for scene {i+1}: {result['error']}")
                    else:
                        print(f"Unexpected response for scene {i+1}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Error for scene {i+1}: {str(e)}")
                continue
        
        print(f"Generated {len(image_data)} images successfully.")
        return {"session_id": session_id, "data": image_data}

    def regenerate_image(self, image_id: str, session_id: str) -> dict:
        """
        Regenerate an image for a given image_id and session_id.
        
        Args:
            image_id: ID of the image to regenerate
            session_id: Session ID to verify ownership
            
        Returns:
            dict: New image_id and image_url
        """
        from app.extentions import mongo
        images_collection = mongo.db.images
        
        image = images_collection.find_one({"file_id": image_id, "metadata.session_id": session_id})
        if not image:
            raise ValueError("Image not found or session mismatch")
        
        # Mark old image as regenerated
        images_collection.update_one(
            {"file_id": image_id},
            {"$set": {"status": "regenerated"}}
        )
        
        sentence = image["metadata"]["script"]
        headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "inputs": sentence,
            "parameters": {
                "num_inference_steps": 50,
                "guidance_scale": 7.5
            }
        }
        
        try:
            response = requests.post(self.HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("image/"):
                new_image_id = str(uuid.uuid4())
                image_bytes = io.BytesIO(response.content)
                new_image_url = self.file_service.uploadImages(image_bytes, new_image_id)
                
                user_id = get_jwt_identity()
                insert_image(
                    file_id=new_image_id,
                    url=new_image_url,
                    script=sentence,
                    owner_id=user_id,
                    session_id=session_id,
                    status="pending",
                    metadata={}
                )
                print(f"Regenerated image {new_image_id} for session {session_id}")
                return {"image_id": new_image_id, "image_url": new_image_url}
            
            else:
                result = response.json()
                raise ValueError(f"API Error: {result.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to regenerate image: {str(e)}")