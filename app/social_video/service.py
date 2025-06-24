from app.extentions import mongo
from .dto import SocialVideoDTO

def save_or_update_social_video(video_id: str, platform: str, link: str):
    # Tìm và cập nhật hoặc tạo mới
    update = {
        f"sharedOn.{platform}": True,
        f"link.{platform}": link
    }
    result = mongo.db.social_videos.find_one_and_update(
        {"id": video_id},
        {"$set": update, "$setOnInsert": {"id": video_id}},
        upsert=True,
        return_document=True
    )
    # Lấy lại document mới nhất
    doc = mongo.db.social_videos.find_one({"id": video_id})
    return SocialVideoDTO(**doc)

def get_all_social_videos():
    docs = list(mongo.db.social_videos.find())
    return [SocialVideoDTO(**doc) for doc in docs]