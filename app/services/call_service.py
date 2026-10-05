import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from google import genai
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

load_dotenv()


def generate_lesson_script(recipient_name: str, topic: str) -> str:
    """
    Use Gemini to create a lively, 2-3 sentence personalized teaching script.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return f"Hey {recipient_name}! I'm calling to share an update on {topic}. What would you like to know?"

    client = genai.Client(api_key=gemini_key)
    prompt = f"""
You are TechMate AI, an enthusiastic, friendly teacher and mentor.
You are calling a student/colleague named "{recipient_name}" to teach and explain the topic: "{topic}".

Instructions:
1. Greet {recipient_name} warmly and introduce yourself as TechMate AI.
2. Explain the core concept of "{topic}" simply in 2 to 3 engaging sentences.
3. End with an open question asking what they think or if they want to dive deeper.
4. Keep it conversational and easy to speak over a phone call.
5. Return ONLY the spoken dialogue.
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        if response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini generation error: {e}")

    return (
        f"Hey {recipient_name}! This is TechMate AI. Today we are exploring {topic}. "
        f"It is one of the most exciting areas in technology today! Does this sound interesting to you?"
    )


def synthesize_lesson_audio(script_text: str, output_filename: str = "lesson.mp3") -> bool:
    """
    Synthesize the spoken lesson with ElevenLabs using the agent's female voice.
    """
    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    if not eleven_key:
        return False

    # Standard female voice ID or agent default
    voice_id = "cjVigY5qzO86Huf0OWal"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        res = requests.post(
            url,
            headers={"xi-api-key": eleven_key, "Content-Type": "application/json"},
            json={"text": script_text, "model_id": "eleven_multilingual_v2"},
            timeout=20,
        )
        if res.status_code == 200:
            Path(output_filename).write_bytes(res.content)
            return True
    except Exception as e:
        print(f"ElevenLabs TTS error: {e}")

    return False


def make_teaching_call(recipient_name: str, to_phone_number: str, caller_id: str, topic: str):
    """
    Initiate a teaching call with custom caller ID, recipient, and topic.
    """
    name = recipient_name.strip() if recipient_name else "Friend"
    subject = topic.strip() if topic else "Modern Artificial Intelligence"

    # Step 1: Generate custom teaching script with Gemini
    spoken_text = generate_lesson_script(name, subject)

    # Step 2: Synthesize audio with ElevenLabs for preview/playback
    audio_created = synthesize_lesson_audio(spoken_text, "lesson.mp3")

    # Step 3: Trigger Twilio phone call
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    effective_caller = caller_id.strip() if caller_id and caller_id.strip() else from_number

    call_result = {"status": "not_attempted"}

    if account_sid and auth_token and to_phone_number:
        client = Client(account_sid, auth_token)

        public_url = os.getenv("PUBLIC_URL", "").rstrip("/")
        if public_url and audio_created:
            # When deployed publicly, Twilio plays the high-fidelity ElevenLabs voice audio directly on the cellular call!
            audio_url = f"{public_url}/api/lesson-audio"
            twiml_content = f"""
            <Response>
                <Play>{audio_url}</Play>
                <Pause length="1"/>
                <Say voice="alice">I am listening. What do you think about this lesson?</Say>
                <Gather input="speech" timeout="5" speechTimeout="auto"/>
            </Response>
            """
        else:
            twiml_content = f"""
            <Response>
                <Say voice="alice">{spoken_text}</Say>
                <Pause length="1"/>
                <Say voice="alice">I am listening. What do you think about this lesson?</Say>
                <Gather input="speech" timeout="5" speechTimeout="auto"/>
            </Response>
            """

        try:
            # Twilio requires an account-owned sender for carrier routing
            call = client.calls.create(
                to=to_phone_number,
                from_=from_number,
                twiml=twiml_content,
            )
            call_result = {
                "status": "success",
                "call_sid": call.sid,
                "message": f"Twilio cellular call ringing {name} at {to_phone_number} from {from_number}!",
            }
        except TwilioRestException as e:
            call_result = {
                "status": "error",
                "code": e.code,
                "message": str(e.msg),
                "details": (
                    "Twilio trial accounts can only call Verified Caller IDs (registered numbers). "
                    "Make sure your phone number is verified in Twilio Console (Manage > Verified Caller IDs) "
                    "and TWILIO_PHONE_NUMBER is set to your active Twilio number."
                ),
            }

    return {
        "recipient_name": name,
        "phone_number": to_phone_number,
        "caller_id": effective_caller,
        "topic": subject,
        "spoken_text": spoken_text,
        "audio_available": audio_created,
        "call_result": call_result,
    }


def make_mobile_call(to_phone_number: str):
    """
    Backwards-compatible standard news call.
    """
    return make_teaching_call("Friend", to_phone_number, "", "Today's Technology News Highlights")
