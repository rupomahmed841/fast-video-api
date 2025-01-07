import requests
from fastapi import FastAPI, Query
import yt_dlp
import fake_useragent
from facebook_scraper import get_posts
import instaloader

app = FastAPI()

# Function to generate fake cookies by simulating a request to YouTube
def generate_fake_cookies(url: str):
    fake_ua = fake_useragent.UserAgent()
    headers = {
        "User-Agent": fake_ua.random,
    }
    
    # Simulate a GET request to YouTube
    response = requests.get(url, headers=headers)
    
    # Extract cookies from the response
    cookies = response.cookies
    cookie_dict = {cookie.name: cookie.value for cookie in cookies}
    
    return cookie_dict

@app.get("/")
def home():
    return {"message": "API is working! Use /youtube, /facebook, or /instagram with a URL parameter."}

@app.get("/youtube")
def get_youtube_link(url: str = Query(..., description="YouTube video URL")):
    """ Extracts the direct download link from a YouTube video """
    try:
        # Generate fake cookies
        cookies = generate_fake_cookies(url)
        
        # Prepare yt-dlp options with the fake cookies
        ydl_opts = {
            "format": "best",
            "cookies": cookies  # Pass the cookies directly
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {"title": info["title"], "direct_url": info["url"]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/facebook")
def get_facebook_link(url: str = Query(..., description="Facebook video URL")):
    """ Extracts the direct download link from a Facebook video """
    try:
        for post in get_posts(post_urls=[url], options={"videos": True}):
            # Handling the case where "text" may not be available
            title = post.get("text", "No text available")  # Default if "text" doesn't exist
            return {"title": title[:50], "direct_url": post["video"]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/instagram")
def get_instagram_link(url: str = Query(..., description="Instagram video URL")):
    """ Extracts the direct download link from an Instagram video """
    try:
        L = instaloader.Instaloader()
        shortcode = url.split("/")[-2]  # Extract the shortcode from the URL
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return {"title": post.caption[:50], "direct_url": post.video_url}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
