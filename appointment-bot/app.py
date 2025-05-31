import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = 'creds.json'  # Download from Google Cloud Console
SHEET_NAME = 'appointments'  # Name of your Google Sheet

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()

    # Simple multi-business: ask user to enter business name first
    if incoming_msg.startswith("book"):
        # Format: book <business> <service> <time>
        try:
            _, business, service, time = incoming_msg.split(maxsplit=3)
            sheet.append_row([business, from_number, service, time, "booked"])
            msg.body(f"Booked {service} at {business} for {time}. You'll get a reminder!")
        except Exception:
            msg.body("Please use: book <business> <service> <time>\nExample: book SalonX haircut 2pm")
    elif incoming_msg == "help":
        msg.body("To book: book <business> <service> <time>\nExample: book SalonX haircut 2pm")
    else:
        msg.body("Welcome to Appointment Bot!\nSend 'help' for instructions.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
