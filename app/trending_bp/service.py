from openai import OpenAI
import os
import random

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_trending_topics(country: str, topic: str = 'technology'):
    prompt = (
        f"List 12 trending subtopics under the topic '{topic}' in {country}."
        f" Provide them in the format: '<title> - <short description>'."
        f" Do not include any symbol item lsit and anything except the list."
        f" Always return in English"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_output = response.choices[0].message.content.strip()
        lines = [line.strip() for line in raw_output.split("\n") if line.strip()]
        
        topics = []
        for idx, line in enumerate(lines, 1):
            if " - " in line:
                title, description = line.split(" - ", 1)
            else:
                title, description = line, "No description provided"
            topics.append({
                "id": idx,
                "title": title.strip(),
                "description": description.strip(),
                "trendScore": random.randint(60, 100)
            })
        return topics
    except Exception as e:
        return {"error": f"Error calling GPT:\n{str(e)}"}
