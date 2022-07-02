from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Spreadheet URL: https://docs.google.com/spreadsheets/d/1sm9MEHX6cC2lpgAX4kADyV_K0AYl4rpSi6SmcUdrnGU/edit#gid=0
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/primera.json'
SPREADSHEET_ID = '1sm9MEHX6cC2lpgAX4kADyV_K0AYl4rpSi6SmcUdrnGU'
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0"
RANGE = 'Hoja 1!A1:D1000'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()


def add_record(sheet, systolic, diastolic, heart_beat, spreadsheet_id=SPREADSHEET_ID):
    now = datetime.now().isoformat()

    range_name = "A1:D1"
    values = [
        [
            now,
            systolic,
            diastolic,
            heart_beat,  
        ],
    ]
    body = {
        "values": values
    }
    value_input_option = "USER_ENTERED"

    result = sheet.values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption=value_input_option, body=body
        ).execute()

    return result