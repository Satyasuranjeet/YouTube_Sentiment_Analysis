from flask import Flask, request, jsonify
import requests
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import os

app = Flask(__name__)

# Initialize Sentiment Analyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# YouTube API Key (Replace with your actual API key)
API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")

def extract_video_id(video_url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
    return match.group(1) if match else None

def get_comments(video_id, max_results=100):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={API_KEY}&maxResults={max_results}"
    response = requests.get(url).json()
    comments = []
    if "items" in response:
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
    return comments

def analyze_sentiments(comments):
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    
    for comment in comments:
        score = sia.polarity_scores(comment)["compound"]
        if score >= 0.05:
            sentiments["positive"] += 1
        elif score <= -0.05:
            sentiments["negative"] += 1
        else:
            sentiments["neutral"] += 1
    
    return sentiments

@app.route("/analyze", methods=["POST"])
def analyze_video():
    data = request.get_json()
    video_url = data.get("url")
    
    if not video_url:
        return jsonify({"error": "YouTube URL is required"}), 400
    
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400
    
    comments = get_comments(video_id)
    if not comments:
        return jsonify({"error": "No comments found"}), 404
    
    sentiment_results = analyze_sentiments(comments)
    total_comments = sum(sentiment_results.values())
    
    positive_ratio = (sentiment_results["positive"] / total_comments) * 100 if total_comments else 0
    negative_ratio = (sentiment_results["negative"] / total_comments) * 100 if total_comments else 0
    
    verdict = "Genuine" if positive_ratio > negative_ratio else "Suspicious"
    
    return jsonify({
        "total_comments": total_comments,
        "positive": sentiment_results["positive"],
        "negative": sentiment_results["negative"],
        "neutral": sentiment_results["neutral"],
        "positive_ratio": round(positive_ratio, 2),
        "negative_ratio": round(negative_ratio, 2),
        "verdict": verdict
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
