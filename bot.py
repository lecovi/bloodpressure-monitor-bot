import html
import re
import logging
import traceback
import json

from emoji import emojize
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bloodpressure_monitor_bot.gapi.helpers import BloodPressureGoogleSheet as Sheet


BLOODPRESSURE_REGEX_PATTERN = "(\d{2,3})\/(\d{2,3})( (\d{2,3}))?"
DEVELOPER_CHAT_ID = 9691064
SERVICE_ACCOUNT_FILE = 'credentials/primera.json'

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)


with open("credentials/telegram_bot.token") as f:
    TOKEN = f.read().strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Starting...")

    user = update.effective_user

    with Sheet(service_account_file=SERVICE_ACCOUNT_FILE) as sheet:
        values = sheet.get_records()

        welcome_message = emojize(f"""Hi {user.mention_html()}!
Connected with GOOGLE :link: <a href="{sheet.url}">Spreadsheet</a>. 
Spreasheet has <b>{len(values)-1} records</b> :chart_increasing:.
    """, language='alias')

        await update.message.reply_html(welcome_message)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hola {update.effective_user.first_name}')


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

        try:
            with Sheet(service_account_file=SERVICE_ACCOUNT_FILE) as sheet:
                sheet.add_record(
                    systolic=systolic,
                    diastolic=diastolic,
                    heart_beat=heart_beat
                )
                answer = f":heart: <strong>{systolic}/{diastolic}</strong> {heart_beat}"
                logger.info("@%s registered SYS=%s DIA=%s HB=%s",
                    update.effective_user['username'],
                    systolic,
                    diastolic,
                    heart_beat,
                )
        except Exception as e:
            answer = ":collision: Something went wrong trying to add record :collision:"
            logger.error(e)

    await update.message.reply_text(
        emojize(answer, language='alias'),
        parse_mode=ParseMode.HTML,
    )


async def last(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if context.args:
        items = -int(context.args[0])
    else:
        items = -1

    # sheet = context.bot_data["sheet"]
    with Sheet(service_account_file=SERVICE_ACCOUNT_FILE) as sheet:
        records = sheet.get_last_records(items)

        answer = ""
        for record in records:
            timestamp, sys, dia, hb = record
            answer += f":calendar: {timestamp} :heart: <strong>{sys}/{dia}</strong> {hb}\n"
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("last", last))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_error_handler(error_handler)

app.run_polling()
