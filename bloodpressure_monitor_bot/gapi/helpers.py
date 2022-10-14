import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from .constants import (
    DEFAULT_GOOGLE_SHEET_VALUE_INPUT_OPTION,
    DEFAULT_GOOGLE_SHEET_RANGE_NAME,
    DEFAULT_GOOGLE_SHEET_COMPLETE_RANGE_NAME,
    DEFAULT_TIMEZONE,
)
from .services import SheetService, DriveService


logger = logging.getLogger(__name__)


class BloodPressureRecord:
    def __init__(self,
        sys,
        dia,
        hb=None,
        timestamp=None,
        tz=ZoneInfo(DEFAULT_TIMEZONE),
    ):
        self.sys = sys
        self.dia = dia
        self.hb = hb if hb else "N/A"
        self.timestamp = timestamp

        if self.timestamp is None:
            self.timestamp = datetime.now().astimezone(tz=tz).isoformat()

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


class BloodPressureSheet:
    def __init__(self, service_account_file, user_email):
        self._service_account_file = service_account_file
        self.user_email = user_email
        self._last_result = None
        self.spreadsheet_id = None

    @property
    def url(self):
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid=0"

    def _create_sheet_file(self, title):
        body = {
            'properties': {
                'title': title
                }
        }
        with SheetService(self._service_account_file) as gservice:
            self._last_result = gservice.spreadsheets().create(
                body=body, 
                fields='spreadsheetId'
            ).execute()
            self.spreadsheet_id = self._last_result["spreadsheetId"]

        logger.info("Spreadsheet %s created for %s",
            self.spreadsheet_id,
            self.user_email,
        )
        return self._last_result

    def _write_bloodpressure_headers(self, headers: list|None = None):
        body = {
            "values": headers if headers else [["Timestamp", "SYS", "DIA", "HB"],]
        }
        with SheetService(self._service_account_file) as gservice:
            self._last_result = gservice.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id, 
                range=DEFAULT_GOOGLE_SHEET_RANGE_NAME,
                valueInputOption=DEFAULT_GOOGLE_SHEET_VALUE_INPUT_OPTION,
                body=body
            ).execute()

        logger.debug("Bloodpressure Headers writed on Spreadsheet %s",
            self.spreadsheet_id,
        )

        return self._last_result

    def _share_sheet(self, sheet_id, email):
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email,
        }

        with DriveService(self._service_account_file) as gservice:
            self._last_result = gservice.permissions().create(
                fileId=sheet_id,
                body=user_permission,
                fields='id',
            ).execute()
        
        logger.info("Spreadsheet %s shared with %s",
            self.spreadsheet_id,
            self.user_email,
        )
        return self._last_result

    def create_shared_sheet(self, title):
        self._create_sheet_file(title=title)

        self._write_bloodpressure_headers()

        self._share_sheet(sheet_id=self.spreadsheet_id, email=self.user_email)

    def add_record(self, record: BloodPressureRecord):
        with SheetService(self._service_account_file) as gservice:
            self._last_result = gservice.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id, 
                range=DEFAULT_GOOGLE_SHEET_RANGE_NAME,
                valueInputOption=DEFAULT_GOOGLE_SHEET_VALUE_INPUT_OPTION,
                body=record.to_spreadsheet_body()
            ).execute()
        return self._last_result

    def get_records(self, range=DEFAULT_GOOGLE_SHEET_COMPLETE_RANGE_NAME):
        with SheetService(self._service_account_file) as gservice:
            self._last_result = gservice.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range,
            ).execute()

        return self._last_result.get('values', [])

    def get_last_records(self, items=-1):
        return self.get_records()[items:]
