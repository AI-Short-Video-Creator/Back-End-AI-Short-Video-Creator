import os
import uuid
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips
from app.video.dto import VideoGenerateDTO
from dotenv import load_dotenv
import logging
import tempfile
import shutil

import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class VideoService:
    _instance = None
    
    DEFAULT_FPS = 24
    DEFAULT_DURATION = 2  # Seconds per image
    DEFAULT_RESOLUTION = (1024, 1024)
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        config = cloudinary.config(secure=True)

    def generate_video(self, dto: VideoGenerateDTO) -> str:
        """
        Generate a video from image URLs with transitions and captions from voice text,
        and upload to Cloudinary.
        
        Args:
            dto: Data Transfer Object containing image URLs, voices, and video parameters
            
        Returns:
            str: Cloudinary URL of the generated video
        """
        if not dto.image_urls or not dto.voices or len(dto.image_urls) != len(dto.voices):
            logger.error("Invalid input: image_urls and voices must be non-empty and equal length")
            raise ValueError("Image URLs and voices must be provided and match in number")
        
        logger.info(f"Generating video with {len(dto.image_urls)} images")
        
        temp_dir = tempfile.mkdtemp()
        video_filename = os.path.join(temp_dir, f"video_{uuid.uuid4()}.mp4")
        
        try:
            fps = dto.fps if dto.fps else self.DEFAULT_FPS
            duration = dto.duration_per_image if dto.duration_per_image else self.DEFAULT_DURATION
            clips = []
            
            for i, (image_url, voice) in enumerate(zip(dto.image_urls, dto.voices)):
                logger.info(f"Processing image {i+1}/{len(dto.image_urls)}: {image_url[:50]}...")
                
                try:
                    response = requests.get(image_url, stream=True)
                    response.raise_for_status()
                    img = Image.open(response.raw).convert("RGB")
                    img = img.resize(self.DEFAULT_RESOLUTION, Image.LANCZOS)
                    
                    if dto.add_captions and voice:
                        try:
                            font = ImageFont.truetype("arial.ttf", 40)
                        except:
                            font = ImageFont.load_default()
                        
                        draw = ImageDraw.Draw(img)
                        caption = voice
                        bbox = draw.textbbox((0, 0), caption, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        position = ((img.width - text_width) // 2, img.height - text_height - 30)
                        draw.rectangle(
                            [position, (position[0] + text_width, position[1] + text_height)],
                            fill=(0, 0, 0, 180)
                        )
                        draw.text(position, caption, font=font, fill=(255, 255, 255))
                    
                    temp_path = os.path.join(temp_dir, f"temp_{i}.png")
                    img.save(temp_path)
                    
                    img_array = np.array(Image.open(temp_path))
                    clip = ImageClip(img_array, duration=duration)
                    
                    if dto.add_transitions:
                        clip = clip.fadein(0.5).fadeout(0.5)
                    
                    clips.append(clip)
                    
                except Exception as e:
                    logger.error(f"Error processing image {image_url}: {str(e)}")
                    continue
            
            if not clips:
                raise ValueError("No valid images to create video")
            
            final_clip = concatenate_videoclips(clips, method="compose")
            
            if dto.audio_url:
                try:
                    response = requests.get(dto.audio_url, stream=True)
                    response.raise_for_status()
                    audio_temp = os.path.join(temp_dir, "audio.mp3")
                    with open(audio_temp, "wb") as f:
                        shutil.copyfileobj(response.raw, f)
                    
                    from moviepy.editor import AudioFileClip
                    audio = AudioFileClip(audio_temp)
                    if audio.duration < final_clip.duration:
                        audio = audio.loop(duration=final_clip.duration)
                    else:
                        audio = audio.subclip(0, final_clip.duration)
                    
                    final_clip = final_clip.set_audio(audio)
                except Exception as e:
                    logger.error(f"Error adding audio {dto.audio_url}: {str(e)}")
            
            final_clip.write_videofile(video_filename, fps=fps, codec='libx264')
            logger.info(f"Video generated locally: {video_filename}")
            
            # Upload to Cloudinary
            logger.info(f"Uploading video to Cloudinary: {video_filename}")
            upload_response = cloudinary.uploader.upload(
                video_filename,
                resource_type="video",
                public_id=f"videos/video_{uuid.uuid4()}",
                folder="user_videos"
            )
            video_url = upload_response["secure_url"]
            logger.info(f"Video uploaded to Cloudinary: {video_url}")
            
            return video_url
            
        except Exception as e:
            logger.error(f"Error creating or uploading video: {str(e)}")
            raise e
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)