# TechMate AI 🎓📞

> **AI-Powered Voice Teaching & Interactive Calling Assistant**  
> Built with FastAPI, Google Gemini 3.5, ElevenLabs Conversational Voice, Twilio, and Web Audio.

---

## 🌟 Overview

**TechMate AI** is an intelligent voice assistant capable of:
1. **Interactive AI Teaching Calls:** Personalizes a lesson on any tech topic for any recipient name, synthesizes realistic speech with ElevenLabs, and calls the user.
2. **100% Free Web-Phone Calling Receiver:** Real-time incoming call simulator that rings with realistic telephone bells and vibration on mobile phones/tablets, allows picking up/answering, speaks the lesson aloud, and gathers 2-way microphone feedback.
3. **Physical SIM Cellular Calling (Twilio):** Dial cellular networks to deliver lessons directly to physical mobile phones.
4. **Live Tech News Aggregator & Gemini Summarizer:** Scrapes RSS feeds across AI, Programming, and Cybersecurity, summarizing them into concise audio-friendly briefings using `gemini-3.5-flash-lite`.

---

## 🎨 User Interface

- **Theme:** Clean glassmorphism in pastel light green with soft pink accents.
- **Card Design:** Single simple animated card with:
  - Recipient Name, Recipient Phone Number, Display Caller ID, and Topic Description.
  - Interactive Soundwave equalizer (`Speaking Lesson:`).
  - Instant Mobile QR Code camera scan.
  - Live carrier diagnostics (`⚙️ Check Physical Mobile Status`).

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key
- ElevenLabs API Key & Conversational Agent ID
- *(Optional)* Twilio Account SID, Auth Token & Number

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/nithinkreddy1538-sketch/techmate-ai.git
cd techmate-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
ELEVENLABS_AGENT_ID=your_agent_id
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number
```

### 4. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Open the dashboard: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
- Open the mobile receiver: `http://<your-local-ip>:8000/receive-call`

---

## 📦 Deployment

### Method A: Deploy on Render.com (Free)
1. Push this repository to GitHub.
2. Go to [Render.com](https://render.com) and create a **New Web Service**.
3. Link your GitHub repository.
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add your environment variables in the Render dashboard.

### Method B: Deploy with Docker
```bash
docker build -t techmate-ai .
docker run -p 8000:8000 --env-file .env techmate-ai
```

---

## 🛡️ License
MIT License
