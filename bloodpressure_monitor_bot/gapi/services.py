from abc import ABC

from google.oauth2 import service_account
from googleapiclient.discovery import build


from .constants import (
    DEFAULT_GOOGLE_SCOPES,
    GOOGLE_SHEETS_SERVICE_NAME,
    GOOGLE_SHEETS_SERVICE_VERSION,
    GOOGLE_DRIVE_SERVICE_NAME,
    GOOGLE_DRIVE_SERVICE_VERSION,
)

class GoogleService(ABC):
    def __init__(self,
        service_account_file: str,
        service_name: str,
        service_version: str,
        scopes: list[str]|None = None,
    ):
        self.scopes = scopes if scopes is not None else DEFAULT_GOOGLE_SCOPES
        self._service_name = service_name
        self._service_version = service_version
        self._service_account_file = service_account_file
        self._credentials = service_account.Credentials.from_service_account_file(
            self._service_account_file,
            scopes=self.scopes
        )
        self._service = None

    def __enter__(self):
        self._service = build(
            self._service_name,
            self._service_version,
            credentials=self._credentials
        )
        return self._service

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._service.close()
        self._service = None


class SheetService(GoogleService):
    def __init__(self, service_account_file, scopes=None):
        super().__init__(
            service_account_file=service_account_file,
            service_name=GOOGLE_SHEETS_SERVICE_NAME,
            service_version=GOOGLE_SHEETS_SERVICE_VERSION,
            scopes=scopes,
        )


class DriveService(GoogleService):
    def __init__(self, service_account_file, scopes=None):
        super().__init__(
            service_account_file=service_account_file,
            service_name=GOOGLE_DRIVE_SERVICE_NAME,
            service_version=GOOGLE_DRIVE_SERVICE_VERSION,
            scopes=scopes,
        )