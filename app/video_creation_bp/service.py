import os, uuid
from app.video_creation_bp.dto import CreateVideoRequestDTO
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
from PIL import Image
import cloudinary
import cloudinary.uploader
import moviepy.config as mpy_config
mpy_config.change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGE_MAGICK_PATH")})

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

OUTPUT_VIDEO_DIR = "generated_videos"
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

class VideoCreationService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not os.path.exists(OUTPUT_VIDEO_DIR):
            os.makedirs(OUTPUT_VIDEO_DIR, exist_ok=True)

    def _split_script_to_subtitles(self, script_text: str, total_duration: float, min_duration: float = 2.0):
        words = script_text.strip().split()
        total_words = len(words)
        words_per_second = max(1, total_words / total_duration)
        chunk_size = max(4, int(words_per_second * min_duration))

        subtitles = []
        start = 0.5
        i = 0
        while i < total_words:
            chunk = words[i:i + chunk_size]
            duration = max(min_duration, len(chunk) / words_per_second)
            if start + duration > total_duration:
                duration = total_duration - start - 0.1
            if duration <= 0:
                break
            subtitles.append({
                "text": " ".join(chunk),
                "start": start,
                "duration": duration
            })
            start += duration + 0.2
            i += chunk_size
        return subtitles

    def create_video_from_request(self, dto: CreateVideoRequestDTO) -> str:
        try:
            audio_clip = AudioFileClip(dto.audio_path)
            video_duration = min(audio_clip.duration, 60)

            target_width = 720
            target_height = 1280

            image_clip = (ImageClip(dto.background_path)
                          .set_duration(video_duration)
                          .resize(height=target_height)
                          .crop(x_center=ImageClip(dto.background_path).w / 2,
                                y_center=ImageClip(dto.background_path).h / 2,
                                width=target_width, height=target_height)
                          .set_position(("center", "center")))

            subs_info = self._split_script_to_subtitles(dto.script_text, video_duration)
            subtitles = []
            for sub in subs_info:
                txt_clip = (TextClip(sub["text"], fontsize=40, color='white', font=dto.font_name,
                                     bg_color='black', size=(target_width * 0.8, None), method='caption')
                            .set_position(('center', 0.8), relative=True)
                            .set_start(sub["start"])
                            .set_duration(sub["duration"])
                            .set_opacity(0.7))
                subtitles.append(txt_clip)

            video_with_subs = CompositeVideoClip([image_clip] + subtitles, size=(target_width, target_height))
            final_video = video_with_subs.set_audio(audio_clip)

            output_filename = f"{uuid.uuid4()}.mp4"
            output_path = os.path.abspath(os.path.join(OUTPUT_VIDEO_DIR, output_filename))
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload_large(
                output_path,
                resource_type="video",
                chunk_size=6000000,
                folder="ai_video_creator"
            )
            video_url = upload_result.get("secure_url")

            # Cleanup
            audio_clip.close()
            image_clip.close()
            for sub_clip in subtitles:
                sub_clip.close()
            video_with_subs.close()
            final_video.close()

            return video_url

        except Exception as e:
            print(f"Error: {e}")
            return None
