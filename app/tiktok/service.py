import os
import requests

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

def exchange_code_for_access_token(code: str, redirect_uri: str):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }
    response = requests.post(url, data=data)
    # Sau khi gọi /oauth/token xong
    print("TikTok Token Response:", response.json())

    response.raise_for_status()
    return response.json()

def get_tiktok_user_info(access_token: str):
    url = "https://open.tiktokapis.com/v2/user/info/"
    params = {
        "fields": "display_name,avatar_url"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()