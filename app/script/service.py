import os
import requests
import google.generativeai as genai
from app.script.dto import ScriptFormatDTO, ScriptGenerateDTO
from pytrends.request import TrendReq

RAPID_API_KEY = os.getenv("RAPID_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ScriptService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_script(self, dto: ScriptGenerateDTO) -> str:
        """
        Generate a script based on the provided keyword and topic.
        
        Args:
            dto (ScriptGenerateDTO): Data Transfer Object containing the keyword and topics.
        
        Returns:
            str: The generated script.
        """

        data = dto.model_dump()
        keyword = data.get("keyword")
        style = data.get("style")
        language = data.get("language")
        word_count = data.get("wordCount", 100)
        tone = data.get("tone", "neutral")
        perspective = data.get("perspective", "third")
        humor = data.get("humor", "none")
        quotes = data.get("quotes", "no")

        prompt = (
            f"Create a short, engaging script (about {word_count} words) for a social media video. "
            "You MUST follow these formatting rules with ABSOLUTE precision: "
            "1. Each scene MUST be structured as: <visual description> Narration: <the spoken text>. "
            "2. The label for the spoken text MUST ALWAYS be the plain text word 'Narration:'. "
            "3. DO NOT use any other labels like 'Dialogue', 'Narration', 'Narrator', 'Lời thoại', etc. "
            "4. DO NOT use any markdown formatting (like **bold** or *italics*) on the 'Narration:' label and script. It must be plain text. "
            "Here is a perfect example of the required format: "
            "[Scene 1: A bustling city street with stylishly dressed people walking by.]\n"
            "Narration: Fashion is more than just clothes; it's a form of expression."
            f"Main keyword: \"{keyword}\". "
            f"Style: {style}. "
            f"Language: {language}. "
            f"Word Count: {word_count}. "
            f"Tone: {tone}. "
            f"Perspective: {perspective}. "
            f"Humor: {humor}. "
            f"Quotes: {quotes}. "
            "Make it emotionally appealing, concise, and resonate with a young audience."
        )

        system_prompt = "You are a creative expert in short-form video content."
        
        response = self.model.generate_content([system_prompt, prompt])
        
        script = response.text
        return script

    def format_script(self, dto: ScriptFormatDTO) -> str:
        """
        Format the script to ensure it follows the required structure using Gemini.
        
        Args:
            script (str): The script to format.
        
        Returns:
            str: The formatted script.
        """
        data = dto.model_dump()
        prompt = (
            "Format the following script so that it strictly follows these rules:\n"
            "1. Each scene MUST be structured as: <visual description> Narration: <the spoken text>.\n"
            "2. The label for the spoken text MUST ALWAYS be the plain text word 'Narration:'.\n"
            "3. DO NOT use any other labels like 'Dialogue', 'Narration', 'Narrator', 'Lời thoại', etc.\n"
            "4. DO NOT use any markdown formatting (like **bold** or *italics*) on the 'Narration:' label and script. It must be plain text.\n"
            "Here is a perfect example of the required format:\n"
            "[Scene 1: A bustling city street with stylishly dressed people walking by.]\n"
            "Narration: Fashion is more than just clothes; it's a form of expression.\n"
            "Format this script accordingly:\n"
            f"{data.get('script')}\n"
            "Ensure the script is concise, engaging, and resonates with a young audience."
        )
        system_prompt = "You are a creative expert in short-form video content."
        response = self.model.generate_content([system_prompt, prompt])
        return response.text
    
    def get_topics_from_wiki(self, keyword: str, limit: int = 5):
        """
        Get trending topics related to a keyword from Wikipedia.
        
        Args:
            keyword (str): Search keyword.
            limit (int): Number of results to return.

        Returns:
            list: List of trending topics.
        """
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": keyword,
            "limit": limit,
            "namespace": 0,
            "format": "json"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data[1]
        else:
            return []
    
    def get_topics_from_google(self, keyword: str, limit: int) -> list:
        url = "https://google-api31.p.rapidapi.com/suggestion"
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "google-api31.p.rapidapi.com"
        }
        response = requests.post(url, headers=headers, json={"text": keyword})
        response.raise_for_status()
        data = response.json()
        phrases = [item["phrase"] for item in data]
        phrases = phrases[:limit]
        return [phrase.capitalize() for phrase in phrases]

    def get_topics_from_youtube(self, keyword: str, limit: int) -> list:
        url = f"https://yt-api.p.rapidapi.com/suggest_queries?query={keyword}"
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "yt-api.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        suggestions = data.get("suggestions", [])
        phrases = []
        for item in suggestions:
            if isinstance(item, dict) and "phrase" in item:
                phrases.append(item["phrase"])
            elif isinstance(item, str):
                phrases.append(item)
        phrases = phrases[:limit]
        return [phrase.capitalize() for phrase in phrases]