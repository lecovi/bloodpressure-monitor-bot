import json

import typer
from rich import print
from rich.table import Table
from googleapiclient.errors import HttpError


from .constants import SERVICE_ACCOUNT_FILE, DEFAULT_GOOGLE_SCOPES
from .services import DriveService, GoogleService


app = typer.Typer()


with open(SERVICE_ACCOUNT_FILE) as f:
    account_file = json.load(f)
    BOT_EMAIL = account_file["client_email"]


@app.command()
def me():
    scopes = DEFAULT_GOOGLE_SCOPES.copy()
    scopes.append("https://www.googleapis.com/auth/userinfo.profile") # See your personal info, including any personal info you've made publicly available"
    with GoogleService(SERVICE_ACCOUNT_FILE, "people", "v1", scopes) as gservice:
        result = gservice.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()
    print(result)


@app.command()
def list():
    print("Connecting to Google Drive...")
    with DriveService(SERVICE_ACCOUNT_FILE) as gservice:
        result = gservice.files().list(
        ).execute()
        for i, file in enumerate(result["files"]):
            file["#"] = i
            file["permissions"] = gservice.files().get(fileId=file["id"], fields="permissions").execute()
            file["url"] = f"https://docs.google.com/spreadsheets/d/{file['id']}/edit#gid=0"

    files = result["files"]
    print(f"The :robot: Bot has access to :file_cabinet: {len(files)} files")

    table = Table(title="Bot Google Drive files")

    table.add_column("#", justify="center", style="cyan")
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("Type", justify="center", style="green")
    table.add_column("Shared count", justify="center", style="white")
    table.add_column("Shared with", justify="center", style="white")
    table.add_column("ID", style="blue", no_wrap=True)

    for file in files:
        filetype = "spreadsheet" if file["mimeType"] == "application/vnd.google-apps.spreadsheet" else file["mimeType"]

        shared = []
        for permission in file["permissions"]["permissions"]:
            if permission["emailAddress"] == BOT_EMAIL:
                continue
            shared.append(permission["emailAddress"])

        table.add_row(
            str(file["#"]),
            file["name"],
            filetype,
            str(len(file["permissions"]["permissions"])),
            ",".join(shared),
            file["id"],
        )

    print(table)

@app.command()
def delete(file_id):
    print("Connecting to Google Drive...")
    with DriveService(SERVICE_ACCOUNT_FILE) as gservice:
        try:
            result = gservice.files().delete(fileId=file_id).execute()
            print(result)
            print(f":wastebasket: Deleted {file_id}!")
        except HttpError as err:
            print(err)

