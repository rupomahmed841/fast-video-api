from fastapi import FastAPI, Query
import yt_dlp
from facebook_scraper import get_posts
import instaloader

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is working! Use /youtube, /facebook, or /instagram with a URL parameter."}

@app.get("/youtube")
def get_youtube_link(url: str = Query(..., description="YouTube video URL")):
    """ Extracts the direct download link from a YouTube video """
    try:
        ydl_opts = {"format": "best"}
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
            return {"title": post["text"][:50], "direct_url": post["video"]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/instagram")
def get_instagram_link(url: str = Query(..., description="Instagram video URL")):
    """ Extracts the direct download link from an Instagram video """
    try:
        L = instaloader.Instaloader()
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return {"title": post.caption[:50], "direct_url": post.video_url}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
