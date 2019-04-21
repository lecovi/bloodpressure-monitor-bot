from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/bloodpressure-monitor-bot-6216165d7280.json'
SAMPLE_SPREADSHEET_ID = '1JJMl75yUGBWAzOm5sEhCHhtN4tsjlQBp4liQoQoCdpE'
RANGE = 'Hoja 1!A1:D1000'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=RANGE).execute()
values = result.get('values', [])
print(values)
print(len(values))