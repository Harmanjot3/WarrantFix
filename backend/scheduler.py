import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC51802bca71499b6da25284cf0471f8ef")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "57de58d69e299a2151ac4144c646b6f4")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+13343842190")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_twilio_sms(body: str, to_phone_number: str):
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        print(f"Twilio SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Twilio SMS sending failed: {str(e)}")
