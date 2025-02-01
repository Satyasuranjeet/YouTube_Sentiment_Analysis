from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
import re
from transformers import pipeline  # Use pipeline for lightweight inference
import numpy as np
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Sentiment Analysis API",
    description="Analyze sentiment of YouTube video comments using a lightweight model",
    version="1.0.0"
)

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("YouTube API key not found in environment variables")

# Use a lightweight sentiment analysis pipeline
print("Loading lightweight sentiment model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
print("Model loaded successfully!")

# Pydantic models for request/response
class VideoRequest(BaseModel):
    video_url: HttpUrl

class SentimentResponse(BaseModel):
    video_id: str
    total_comments: int
    sentiment_distribution: Dict[str, int]
    sentiment_percentages: Dict[str, float]
    sample_comments: Dict[str, List[str]]

# Helper functions
def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", str(url))
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format")
    return match.group(1)

def get_comments(video_id: str, max_results: int = 50) -> List[str]:
    """Fetch comments from YouTube API."""
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data:
            raise HTTPException(status_code=404, detail="No comments found")
            
        return [
            item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            for item in data["items"]
        ]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"YouTube API error: {str(e)}")

def analyze_sentiment(comment: str) -> str:
    """Analyze sentiment of a single comment."""
    try:
        result = sentiment_pipeline(comment[:512])[0]
        return result["label"].lower()
    except Exception as e:
        print(f"Error analyzing comment: {str(e)}")
        return "neutral"  # Default to neutral on error

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_video(request: VideoRequest):
    """
    Analyze sentiment of YouTube video comments.
    Returns sentiment distribution and sample comments for each category.
    """
    # Extract video ID
    video_id = extract_video_id(request.video_url)
    
    # Get comments (limit to 50 to reduce memory usage)
    comments = get_comments(video_id, max_results=50)
    
    # Initialize results
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    sample_comments = {"positive": [], "negative": [], "neutral": []}
    
    # Analyze comments
    for comment in comments:
        sentiment = analyze_sentiment(comment)
        sentiments[sentiment] += 1
        
        # Store sample comments (up to 3 per category)
        if len(sample_comments[sentiment]) < 3:
            sample_comments[sentiment].append(comment)
    
    # Calculate percentages
    total_comments = sum(sentiments.values())
    sentiment_percentages = {
        k: round(v / total_comments * 100, 2)
        for k, v in sentiments.items()
    }
    
    return SentimentResponse(
        video_id=video_id,
        total_comments=total_comments,
        sentiment_distribution=sentiments,
        sentiment_percentages=sentiment_percentages,
        sample_comments=sample_comments
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)