import os
import requests
import logging
import time
import random
from app.image.dto import ImageGenerateDTO
import uuid
from dotenv import load_dotenv
from app.image.repo import insert_image
from flask_jwt_extended import get_jwt_identity
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

class ImageService:
    _instance = None
    
    TOGETHER_API_URL = "https://api.together.xyz/v1/images/generations"
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 5  # Seconds
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not TOGETHER_API_KEY:
            logger.warning("TOGETHER_API_KEY environment variable not set.")

    def generate_image(self, dto: ImageGenerateDTO) -> dict:
        """
        Generate images from a script by splitting it into scenes using FLUX.1-schnell-Free.
        
        Args:
            dto: Data Transfer Object containing the script and themes
            
        Returns:
            dict: Contains session_id and list of image info (image_id, image_url, scene, voice)
        """
        if not TOGETHER_API_KEY:
            logger.error("TOGETHER_API_KEY not configured.")
            raise ValueError("TOGETHER_API_KEY not configured.")
        
        user_id = get_jwt_identity()
        logger.info(f"User ID at image service: {user_id}")
        
        session_id = str(uuid.uuid4())
        full_script = dto.script
        themes = dto.themes or "cartoon"
        logger.info(f"Using theme: {themes}")
        
        # Extract scenes and voices
        scene_matches = list(re.finditer(r"\*\*\[Scene\s*\d+:\s*(.*?)\]\*\*", full_script))
        voice_matches = list(re.finditer(r"\*\*(.*?):\*\*\s*\"(.*?)\"", full_script))
        
        scenes = []
        for scene_match, voice_match in zip(scene_matches, voice_matches):
            scene_text = scene_match.group(1).strip()
            voice_text = voice_match.group(2).strip()
            if scene_text and voice_text:
                scenes.append({"scene": scene_text, "voice": voice_text})
        
        logger.info(f"Split script into {len(scenes)} scenes with voices")
        
        image_data = []
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        for i, scene_info in enumerate(scenes):
            scene = scene_info["scene"]
            voice = scene_info["voice"]
            if len(scene) < 10:
                logger.info(f"Skipping short scene {i+1}: {scene}")
                continue
                
            prompt = f"{scene}, {themes} style"
            payload = {
                "model": "black-forest-labs/FLUX.1-schnell-Free",
                "prompt": prompt,
                "steps": 4,
                "n": 1,
                "guidance_scale": 0.0
            }
            
            retries = 0
            while retries < self.MAX_RETRIES:
                try:
                    logger.info(f"Generating image for scene {i+1}/{len(scenes)}: {prompt[:50]}...")
                    response = requests.post(self.TOGETHER_API_URL, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    result = response.json()
                    if "data" in result and len(result["data"]) > 0:
                        image_url = result["data"][0]["url"]
                        image_id = str(uuid.uuid4())
                        
                        try:
                            insert_image(
                                file_id=image_id,
                                url=image_url,
                                scene=scene,
                                voice=voice,
                                owner_id=user_id,
                                session_id=session_id,
                                status="pending",
                                metadata={"themes": themes}
                            )
                        except Exception as e:
                            logger.error(f"MongoDB insertion failed for scene {i+1}: {str(e)}")
                            break
                            
                        image_data.append({
                            "image_id": image_id,
                            "image_url": image_url,
                            "scene": scene,
                            "voice": voice
                        })
                        logger.info(f"Stored image {image_id} with URL")
                        break
                        
                    else:
                        logger.error(f"Unexpected response for scene {i+1}: {result}")
                        break
                        
                except requests.exceptions.HTTPError as e:
                    if response.status_code == 429:
                        retries += 1
                        retry_after = response.headers.get("Retry-After")
                        delay = int(retry_after) if retry_after and retry_after.isdigit() else self.BASE_RETRY_DELAY * (2 ** retries) + random.uniform(0, 0.1)
                        logger.warning(f"Rate limit hit for scene {i+1}, retry {retries}/{self.MAX_RETRIES} after {delay:.2f}s")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Together AI API error for scene {i+1}: {str(e)}")
                        break
                except requests.exceptions.RequestException as e:
                    logger.error(f"Together AI API error for scene {i+1}: {str(e)}")
                    break
            
            if retries >= self.MAX_RETRIES:
                logger.error(f"Max retries exceeded for scene {i+1}, skipping")
                continue
            
            time.sleep(6.0)  # Throttle for 10 images/min
        
        logger.info(f"Generated {len(image_data)} images successfully.")
        return {"session_id": session_id, "data": image_data}

    def regenerate_image(self, image_id: str, session_id: str) -> dict:
        """
        Regenerate an image for a given image_id and session_id using FLUX.1-schnell-Free.
        
        Args:
            image_id: ID of the image to regenerate
            session_id: Session ID to verify ownership
            
        Returns:
            dict: New image_id, image_url, scene, and voice
        """
        from app.extentions import mongo
        images_collection = mongo.db.images
        
        image = images_collection.find_one({"file_id": image_id, "metadata.session_id": session_id})
        if not image:
            logger.error(f"Image not found or session mismatch: image_id={image_id}, session_id={session_id}")
            raise ValueError("Image not found or session mismatch")
        
        images_collection.update_one(
            {"file_id": image_id},
            {"$set": {"status": "regenerated"}}
        )
        
        scene = image["scene"]
        voice = image["voice"]
        themes = image["metadata"].get("themes", "cartoon")
        prompt = f"{scene}, {themes} style"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": prompt,
            "steps": 4,
            "n": 1,
            "guidance_scale": 0.0
        }
        
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                logger.info(f"Regenerating image {image_id} for session {session_id}")
                response = requests.post(self.TOGETHER_API_URL, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if "data" in result and len(result["data"]) > 0:
                    new_image_url = result["data"][0]["url"]
                    new_image_id = str(uuid.uuid4())
                    
                    user_id = get_jwt_identity()
                    insert_image(
                        file_id=new_image_id,
                        url=new_image_url,
                        scene=scene,
                        voice=voice,
                        owner_id=user_id,
                        session_id=session_id,
                        status="pending",
                        metadata={"themes": themes}
                    )
                    logger.info(f"Regenerated image {new_image_id} for session {session_id}")
                    return {
                        "image_id": new_image_id,
                        "image_url": new_image_url,
                        "scene": scene,
                        "voice": voice
                    }
                
                else:
                    logger.error(f"API Error for regeneration: {result}")
                    raise ValueError(f"API Error: {result.get('error', 'Unknown error')}")
                    
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retries += 1
                    retry_after = response.headers.get("Retry-After")
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else self.BASE_RETRY_DELAY * (2 ** retries) + random.uniform(0, 0.1)
                    logger.warning(f"Rate limit hit for regeneration, retry {retries}/{self.MAX_RETRIES} after {delay:.2f}s")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Failed to regenerate image {image_id}: {str(e)}")
                    raise ValueError(f"Failed to regenerate image: {str(e)}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to regenerate image {image_id}: {str(e)}")
                raise ValueError(f"Failed to regenerate image: {str(e)}")
        
        logger.error(f"Max retries exceeded for regeneration of image {image_id}")
        raise ValueError("Failed to regenerate image after max retries")