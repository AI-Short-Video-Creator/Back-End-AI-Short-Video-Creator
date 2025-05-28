import os
import glob
import uuid
from typing import List
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips
from app.video.dto import VideoGenerateDTO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VideoService:
    _instance = None
    
    # Video settings
    DEFAULT_FPS = 24
    DEFAULT_DURATION = 2  # Seconds per image
    DEFAULT_RESOLUTION = (1024, 1024)
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        # Đảm bảo thư mục output tồn tại
        os.makedirs("output", exist_ok=True)
    
    def generate_video(self, dto: VideoGenerateDTO) -> str:
        """
        Generate a video from images in the output folder with transitions and captions.
        
        Args:
            dto: Data Transfer Object containing video parameters
            
        Returns:
            str: Path to the generated video file
        """
        # Lấy danh sách ảnh từ thư mục output
        image_files = []
        
        # Nếu có image_paths trong DTO, sử dụng chúng
        if dto.image_paths and len(dto.image_paths) > 0:
            image_files = dto.image_paths
            print(f"Using {len(image_files)} images from provided paths")
        else:
            # Nếu không, tìm tất cả file png trong thư mục output
            image_files = sorted(glob.glob("output/*.png"))
            print(f"Found {len(image_files)} images in output folder")
        
        if not image_files:
            raise ValueError("No images found to create video")
        
        # Tạo tên file video
        video_filename = f"output/video_{uuid.uuid4()}.mp4"
        
        # Xác định các tham số
        fps = dto.fps if dto.fps else self.DEFAULT_FPS
        duration = dto.duration_per_image if dto.duration_per_image else self.DEFAULT_DURATION
        
        # Tạo danh sách clips
        clips = []
        
        for i, img_path in enumerate(image_files):
            try:
                print(f"Processing image {i+1}/{len(image_files)}: {img_path}")
                
                # Mở ảnh bằng PIL
                img = Image.open(img_path).convert("RGB")
                
                # Thêm caption nếu có
                if dto.add_captions and dto.captions and i < len(dto.captions):
                    caption = dto.captions[i]
                    # Tạo font
                    try:
                        font = ImageFont.truetype("arial.ttf", 40)
                    except:
                        font = ImageFont.load_default()
                    
                    draw = ImageDraw.Draw(img)
                    # Tính toán vị trí text
                    bbox = draw.textbbox((0, 0), caption, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Vị trí ở dưới cùng, giữa ảnh
                    position = ((img.width - text_width) // 2, img.height - text_height - 30)
                    
                    # Vẽ nền cho text
                    draw.rectangle(
                        [position, (position[0] + text_width, position[1] + text_height)],
                        fill=(0, 0, 0, 180)
                    )
                    # Vẽ text
                    draw.text(position, caption, font=font, fill=(255, 255, 255))
                
                # Chuyển đổi sang numpy array cho MoviePy
                img_array = np.array(img)
                
                # Tạo clip
                clip = ImageClip(img_array, duration=duration)
                
                # Thêm hiệu ứng nếu được yêu cầu
                if dto.add_transitions:
                    clip = clip.fadein(0.5).fadeout(0.5)
                
                clips.append(clip)
                
            except Exception as e:
                print(f"Error processing image {img_path}: {str(e)}")
                continue
        
        if not clips:
            raise ValueError("No valid images to create video")
        
        try:
            # Kết hợp các clips
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Thêm audio nếu có
            if dto.audio_path and os.path.exists(dto.audio_path):
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(dto.audio_path)
                # Lặp audio nếu ngắn hơn video
                if audio.duration < final_clip.duration:
                    audio = audio.loop(duration=final_clip.duration)
                else:
                    # Cắt audio nếu dài hơn video
                    audio = audio.subclip(0, final_clip.duration)
                
                final_clip = final_clip.set_audio(audio)
            
            # Xuất video
            final_clip.write_videofile(video_filename, fps=fps, codec='libx264')
            print(f"Video created successfully: {video_filename}")
            
            return video_filename
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            raise e