import openai
import os
from app.script.dto import ScriptGenerateDTO

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ScriptService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.llm = openai.OpenAI(
            api_key=OPENAI_API_KEY,
        )
    
    def generate_script(self, dto: ScriptGenerateDTO) -> str:
        """
        Generate a script based on the provided keyword and topic.
        
        Args:
            dto (ScriptGenerateDTO): Data Transfer Object containing the keyword and topics.
        
        Returns:
            str: The generated script.
        """

        data = dto.model_dump()
        keywords = data.get("keywords")
        topic = data.get("topic")
        
        prompt = (
            "Create a short, engaging script (100-150 words) for a social media video. "
            "For each scene, follow this pattern: <visual description> <dialogue or narration for that scene>. "
            f"Main topic: \"{topic}\". "
            f"Related keywords: {', '.join(keywords)}. "
            "Make it emotionally appealing, concise, and resonate with a young audience."
        )

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative expert in short-form video content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )

        script = response.choices[0].message.content
        return script
        