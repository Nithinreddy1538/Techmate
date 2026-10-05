import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import requests

from pydantic import BaseModel

from app.services.news_service import fetch_news
from app.services.gemini_service import summarize_news_articles
from app.services.call_service import make_mobile_call, make_teaching_call


app = FastAPI(
    title="TechMate AI",
    description="AI-powered technology news calling assistant",
    version="0.1.0",
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
LATEST_LESSON = {
    "spoken_text": (
        "Hey there! This is TechMate AI, your friendly tech tutor. Today we are diving into our interactive lesson! "
        "What questions do you have to get started?"
    )
}

ACTIVE_CALL = {
    "call_id": None,
    "recipient_name": "Nithin Kumar",
    "phone_number": "+916302807060",
    "caller_id": "+1 (800) 555-0199",
    "topic": "Python Object Oriented Programming",
    "spoken_text": (
        "Hey there! This is TechMate AI, your friendly tech tutor. Today we are diving into our interactive lesson! "
        "What questions do you have to get started?"
    ),
    "status": "idle",  # "idle", "ringing", "in_call", "ended"
    "timestamp": 0,
}


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """
    User interaction dashboard to call TechMate AI and view live tech news.
    """
    html_file = TEMPLATES_DIR / "dashboard.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Dashboard file not found</h2>", status_code=404)


@app.get("/receive-call", response_class=HTMLResponse)
def get_receive_call():
    """
    Interactive incoming call receiver screen for mobile devices.
    """
    html_file = TEMPLATES_DIR / "receive_call.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>Receive call page not found</h2>", status_code=404)


@app.get("/api/latest-lesson")
def get_latest_lesson():
    return LATEST_LESSON


@app.get("/api/active-call")
def get_active_call():
    return ACTIVE_CALL


@app.post("/api/answer-call")
def answer_call():
    ACTIVE_CALL["status"] = "in_call"
    return {"status": "ok", "call_status": "in_call", "active_call": ACTIVE_CALL}


@app.post("/api/end-call")
def end_call():
    ACTIVE_CALL["status"] = "ended"
    return {"status": "ok", "call_status": "ended"}


@app.post("/api/reset-call")
def reset_call():
    ACTIVE_CALL["status"] = "idle"
    return {"status": "ok", "call_status": "idle"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "TechMate AI",
    }


@app.get("/api/twilio-status")
def get_twilio_status():
    """
    Live diagnostic endpoint to check Twilio carrier readiness for physical SIM calls.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    env_from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token:
        return {
            "configured": False,
            "can_call_cellular": False,
            "error": "TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is missing in .env",
        }

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        acct = client.api.accounts(account_sid).fetch()
        incoming = [n.phone_number for n in client.incoming_phone_numbers.list()]
        outgoing = [n.phone_number for n in client.outgoing_caller_ids.list()]

        has_number = len(incoming) > 0
        from_valid = env_from_number in incoming if env_from_number else False

        diagnosis = []
        if acct.type == "Trial":
            diagnosis.append("Twilio Account is on Free Trial tier.")
            if not incoming:
                diagnosis.append("You have 0 active Twilio numbers. Go to Twilio Console and click 'Get Phone Number'.")
            elif not from_valid:
                diagnosis.append(f"TWILIO_PHONE_NUMBER in .env ({env_from_number}) does not match your active Twilio numbers ({incoming}).")
            if not outgoing:
                diagnosis.append("No numbers verified. Twilio Trial accounts require verifying recipient numbers via SMS before dialing them.")
            diagnosis.append("Twilio Trial restricts dialing Indian SIM cards (+91) over cellular towers unless upgraded with balance.")

        return {
            "configured": True,
            "account_status": acct.status,
            "account_type": acct.type,
            "active_twilio_numbers": incoming,
            "verified_recipient_numbers": outgoing,
            "env_from_number": env_from_number,
            "from_number_valid": from_valid,
            "can_call_cellular": has_number and len(outgoing) > 0,
            "diagnosis": diagnosis,
        }
    except Exception as e:
        return {
            "configured": False,
            "can_call_cellular": False,
            "error": str(e),
        }



@app.get("/api/signed-url")
def get_signed_url():
    """
    Generate an authenticated signed URL for direct ElevenLabs ConvAI calling.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")

    if not api_key or not agent_id:
        raise HTTPException(
            status_code=500,
            detail="ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID is not configured in .env",
        )

    url = f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={agent_id}"
    response = requests.get(url, headers={"xi-api-key": api_key})

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@app.get("/api/greeting-audio")
def get_greeting_audio():
    audio_path = Path("greeting.mp3")
    if audio_path.exists():
        return FileResponse(audio_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio not found")


class CallRequest(BaseModel):
    phone_number: str


@app.post("/api/call-mobile")
def call_mobile(req: CallRequest):
    """
    Trigger an outbound cellular phone call to a user's mobile number.
    """
    return make_mobile_call(req.phone_number)


class TeachingCallRequest(BaseModel):
    recipient_name: str = "Friend"
    phone_number: str
    caller_id: str = "+1 (800) 555-0199"
    topic: str = "Introduction to Python Programming"


@app.post("/api/teaching-call")
def trigger_teaching_call(req: TeachingCallRequest):
    """
    Trigger a personalized teaching call with custom caller ID, recipient name, and topic.
    """
    import time
    call_id = f"call_{int(time.time() * 1000)}"

    result = make_teaching_call(
        recipient_name=req.recipient_name,
        to_phone_number=req.phone_number,
        caller_id=req.caller_id,
        topic=req.topic,
    )
    spoken_text = result.get("spoken_text") or (
        f"Hey {req.recipient_name}! This is TechMate AI. Today we are exploring {req.topic}. "
        "What questions do you have to get started?"
    )
    LATEST_LESSON["spoken_text"] = spoken_text

    ACTIVE_CALL.update({
        "call_id": call_id,
        "recipient_name": req.recipient_name,
        "phone_number": req.phone_number,
        "caller_id": req.caller_id or "+1 (800) 555-0199",
        "topic": req.topic,
        "spoken_text": spoken_text,
        "status": "ringing",
        "timestamp": time.time(),
    })

    result["active_call"] = ACTIVE_CALL
    result["free_call_ready"] = True
    return result


@app.get("/api/lesson-audio")
def get_lesson_audio():
    audio_path = Path("lesson.mp3")
    if audio_path.exists():
        return FileResponse(audio_path, media_type="audio/mpeg")
    return get_greeting_audio()


@app.get("/news")
def get_news():
    """
    Get real technology news
    and generate AI summaries using Gemini.
    """
    articles = fetch_news()
    summarized_articles = summarize_news_articles(articles)

    return {
        "total_articles": len(summarized_articles),
        "articles": summarized_articles,
    }