class CreateVideoRequestDTO:
    def __init__(self, audio_path: str, script_text: str, background_path: str, font_name: str = "Arial"):
        self.audio_path = audio_path
        self.script_text = script_text
        self.background_path = background_path
        self.font_name = font_name


class CreateVideoResponseDTO:
    def __init__(self, video_url: str, message: str):
        self.video_url = video_url
        self.message = message

    def to_dict(self):
        return {
            "video_url": self.video_url,
            "message": self.message
        }
