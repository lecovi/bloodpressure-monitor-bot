import logging

from emoji import emojize
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update

from bloodpressure_monitor_bot.gapi.helpers import BloodPressureGoogleSheet as Sheet
from .constants import SERVICE_ACCOUNT_FILE
from .helpers import parse_bloodpressure_message


logger = logging.getLogger(__name__)

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

    parsed_message = parse_bloodpressure_message(message)

    if not parsed_message:
        answer = "Perdón, no te entendí :worried_face:"
    else:
        sys, dia, hb = parsed_message
        try:
            with Sheet(service_account_file=SERVICE_ACCOUNT_FILE) as sheet:
                sheet.add_record(
                    systolic=sys,
                    diastolic=dia,
                    heart_beat=hb,
                )
                answer = f":heart: <strong>{sys}/{dia}</strong> {hb}"
                logger.info("@%s registered SYS=%s DIA=%s HB=%s",
                    update.effective_user['username'],
                    sys,
                    dia,
                    hb,
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

    items = -int(context.args[0]) if context.args else -1

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