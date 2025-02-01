# YouTube Video Sentiment Analysis API

This API analyzes YouTube video comments to determine whether a video is **Genuine** or **Suspicious** based on sentiment analysis.

## 🚀 Features
- Extracts comments from a YouTube video using the YouTube Data API.
- Performs **sentiment analysis** on comments using **NLTK's SentimentIntensityAnalyzer**.
- Returns a **verdict** on the video based on the sentiment ratio.

## 📌 Tech Stack
- **Flask** (Backend framework)
- **NLTK** (Sentiment Analysis)
- **Requests** (For API calls)

## 🔧 Setup & Installation
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/youtube-sentiment-api.git
cd youtube-sentiment-api
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set Environment Variables
Create a `.env` file and add your **YouTube API Key**:
```
YOUTUBE_API_KEY=your_api_key_here
```

### 4️⃣ Run the Flask Server
```bash
python app.py
```

The API will be available at: `http://127.0.0.1:5000`

---

## 🎯 Usage
### **POST** `/analyze`
**Request:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```
**Response:**
```json
{
    "total_comments": 100,
    "positive": 70,
    "negative": 20,
    "neutral": 10,
    "positive_ratio": 70.0,
    "negative_ratio": 20.0,
    "verdict": "Genuine"
}
```

## 📡 Deployment
To deploy on **Render**, follow these steps:
1. Create a **new Web Service** on [Render](https://render.com/).
2. Set the **Start Command**: `python app.py`
3. Add the **Environment Variable** for `YOUTUBE_API_KEY`.
4. Deploy and access your API at `https://your-app-name.onrender.com/analyze`

---

## 🔥 Author
- **Satya Suranjeet Jena** ([GitHub](https://github.com/Satyasuranjeet))

🚀 Happy Coding! 🎯
