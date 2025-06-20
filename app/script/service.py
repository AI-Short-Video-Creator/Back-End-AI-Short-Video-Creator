import openai
import os
import requests
from app.script.dto import ScriptGenerateDTO
from pytrends.request import TrendReq

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

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
            "For each scene, follow this pattern: <visual description> <dialogue or narration for that scene>. "
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