import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_captions(video_context: str, lang: str = "en"):
    prompt = (
        f"Generate a suitable title and caption for this video to share on social platforms. "
        f"Video context: '{video_context}'. Respond in JSON with keys 'title' and 'caption'. "
        f"Use language: {lang}."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # dùng model chính xác hơn
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_output = response.choices[0].message.content.strip()
        print("Raw output:", raw_output)  # Debug output

        # Remove ```json or ``` if exists
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?\s*|```$", "", raw_output.strip(), flags=re.MULTILINE).strip()

        # Parse JSON
        result = json.loads(raw_output)
        return {
            "title": result.get("title", ""),
            "caption": result.get("caption", "")
        }
    except Exception as e:
        return {"error": f"Error calling GPT:\n{str(e)}"}
