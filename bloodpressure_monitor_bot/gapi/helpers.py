import logging
from datetime import datetime
from pickletools import read_uint1

from httplib2 import Http
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp


logger = logging.getLogger(__name__)


DEFAULT_GOOGLE_SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
        ]

class BloodPressureGoogleSheet:
    def __init__(self,
        service_account_file,
        id='1sm9MEHX6cC2lpgAX4kADyV_K0AYl4rpSi6SmcUdrnGU',
        sheet_range='Hoja 1!A1:D1000',
        scopes=None,
    ):
        self.service_account_file = service_account_file
        self.id = id
        self.complete_range = sheet_range
        self.scopes = scopes if scopes is not None else DEFAULT_GOOGLE_SCOPES

        self._credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.scopes
        )

        self._last_result = None
        self._service = None
        self.sheet = None

    def __enter__(self):
        self._service = build('sheets', 'v4', credentials=self._credentials)
        self.sheet = self._service.spreadsheets()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.sheet = None
        self._service.close()

    @property
    def url(self):
        SPREADSHEET_URL_TEMPLATE = f"https://docs.google.com/spreadsheets/d/{self.id}/edit#gid=0"
        return SPREADSHEET_URL_TEMPLATE

    def add_record(self,
        systolic,
        diastolic,
        heart_beat,
        value_input_option="USER_ENTERED",
        range_name="A1:D1",
    ):
        record = BloodPressureRecord(systolic, diastolic, heart_beat)

        self._last_result = self.sheet.values().append(
            spreadsheetId=self.id, 
            range=range_name,
            valueInputOption=value_input_option,
            body=record.to_spreadsheet_body()
        ).execute()
        self._last_result["timestamp"] = record.timestamp  #TODO: became decorator

    def get_records(self, range=None):
        if range is None:
            range = self.complete_range 

        self._last_result = self.sheet.values().get(
            spreadsheetId=self.id,
            range=range,
        ).execute()
        now = datetime.now().isoformat()  #TODO: became decorator
        self._last_result["timestamp"] = now  #TODO: became decorator
        return self._last_result.get('values', [])

    def get_last_records(self, items=-1):
        return self.get_records()[items:]

class BloodPressureRecord:

    def __init__(self, sys, dia, hb=None, timestamp=None):
        self.sys = sys
        self.dia = dia
        self.hb = hb if hb else "N/A"
        self.timestamp = timestamp

        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_values(self):
        """Returns a list of its values."""
        return [
            self.timestamp,
            self.sys,
            self.dia,
            self.hb,
        ]

    def to_spreadsheet_body(self):
        """Returns the values ready to post on the body for spreadsheet"""
        return {
            "values": [
                self.to_values(),
            ]
        }