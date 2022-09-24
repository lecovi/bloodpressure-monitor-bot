import logging
from datetime import datetime

from httplib2 import Http
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp


logger = logging.getLogger(__name__)


class BloodPressureGoogleSheet:
    def __init__(self,
        service_account_file,
        id='1sm9MEHX6cC2lpgAX4kADyV_K0AYl4rpSi6SmcUdrnGU',
        sheet_range='Hoja 1!A1:D1000',
        google_default_read_timeout=50,
    ):
        self.service_account_file = service_account_file
        self.id = id
        self.complete_range = sheet_range
        self.timeout = google_default_read_timeout
        self._last_append_result = None
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
        ]
        self.url = f"https://docs.google.com/spreadsheets/d/{self.id}/edit#gid=0"

        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.scopes
        )

        http = Http(timeout=self.timeout)
        auth_http = AuthorizedHttp(credentials, http=http)

        service = build('sheets', 'v4', http=auth_http)

        self.sheet = service.spreadsheets()

    def add_record(self,
        systolic,
        diastolic,
        heart_beat,
        value_input_option="USER_ENTERED",
        range_name="A1:D1",
    ):
        now = datetime.now().isoformat()

        values = [
            [
                now,
                systolic,
                diastolic,
                heart_beat if heart_beat else "N/A",
            ],
        ]
        body = {
            "values": values
        }

        result = self.sheet.values().append(
            spreadsheetId=self.id, 
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()

        self._last_append_result = result

    def get_records(self, range=None):
        if range is None:
            range = self.complete_range 

        results = self.sheet.values().get(
            spreadsheetId=self.id,
            range=range,
        ).execute()
        values = results.get('values', [])
        return values

    def get_last_record(self):
        if self._last_append_result is None:
            return None

        range_ = self._last_append_result["updates"]["updatedRange"]
        range_ = range_.split("!")[1]
        return self.get_records(range=range_)[0]