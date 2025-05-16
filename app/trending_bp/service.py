from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_trending_topics(country: str):
    prompt = f"Liệt kê 5 chủ đề cụ thể về hiện tượng giải trí nổi bật hiện nay ở {country}, theo dạng danh sách đánh số từ 1 đến 5. Không thêm từ ngữ nào ngoài danh sách."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý hữu ích."},
                {"role": "user", "content": prompt}
            ]
        )
        topics_text = response.choices[0].message.content.strip()
        topics = [line.strip() for line in topics_text.split("\n") if line.strip()]
        return topics
    except Exception as e:
        return {"error": f"Lỗi khi gọi GPT:\n{str(e)}"}
