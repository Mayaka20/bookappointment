import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
CREDS_FILE = os.environ.get('GOOGLE_CREDS_FILE', 'creds.json')  # Path to your creds.json
SHEET_NAME = os.environ.get('GOOGLE_SHEET_NAME', 'appointments')  # Sheet name

# Authorize Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # You can use .worksheet(business) for per-business tabs

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()

    # Multi-business: book <business> <service> <time>
    if incoming_msg.lower().startswith("book"):
        try:
            # Split only into 4 parts: "book", business, service, time
            parts = incoming_msg.split(maxsplit=3)
            if len(parts) < 4:
                raise ValueError("Not enough arguments")
            _, business, service, time = parts
            # Save booking: [business, phone, service, time, status]
            sheet.append_row([business, from_number, service, time, "booked"])
            msg.body(f"✅ Booked *{service}* at *{business}* for *{time}*.\nYou'll get a reminder!")
        except Exception:
            msg.body("❗️Please use: book <business> <service> <time>\nExample: book SalonX haircut 2pm")
    elif incoming_msg.lower() == "help":
        msg.body(
            "To book an appointment, send:\n"
            "book <business> <service> <time>\n"
            "Example: book SalonX haircut 2pm"
        )
    else:
        msg.body(
            "👋 Welcome to Appointment Bot!\n"
            "To book: book <business> <service> <time>\n"
            "Send 'help' for instructions."
        )

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
