from multiprocessing import allow_connection_pickling
from multiprocessing.connection import answer_challenge
import re
import logging

from emoji import emojize
from telegram import Update, ForceReply
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bloodpressure_monitor_bot.gapi.helpers import (
    sheet, SPREADSHEET_ID, RANGE, SPREADSHEET_URL, add_record
    )


BLOODPRESSURE_REGEX_PATTERN = "(\d{2,3})\/(\d{2,3})( (\d{2,3}))?"


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


with open("credentials/telegram_bot.token") as f:
    TOKEN = f.read().strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID, 
        range=RANGE
    ).execute()

    values = result.get('values', [])

    welcome_message = emojize(f"""Hi {user.mention_html()}!
Connected with GOOGLE :link: <a href="{SPREADSHEET_URL}">Spreadsheet</a>. 
Spreasheet has <b>{len(values)-1} records</b> :chart_increasing:.
""", language='alias')

    await update.message.reply_html(welcome_message)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    message = update.message.text
    answer = emojize("Perdón, no te entendí :worried_face:", language='alias')

    match = re.match(BLOODPRESSURE_REGEX_PATTERN, message)
    if match:
        systolic = match.group(1)
        diastolic = match.group(2)
        heart_beat = match.group(3)
        if heart_beat:
            heart_beat = match.group(4)

        result = add_record(
            sheet=sheet,
            systolic=systolic,
            diastolic=diastolic,
            heart_beat=heart_beat
        )

        if result:
            answer = f"SYS={systolic} DIA={diastolic} HB={heart_beat}"
            logger.info("@%s registered %s", update.effective_user['username'], answer)
        else:
            answer = f":collision: Something went wrong trying to add record on spreadsheet"

    await update.message.reply_text(answer)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()
