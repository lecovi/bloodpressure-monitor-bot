import logging

from emoji import emojize
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram import Update

from bloodpressure_monitor_bot.gapi.helpers import BloodPressureSheet as Sheet
from bloodpressure_monitor_bot.gapi.helpers import BloodPressureRecord
from bloodpressure_monitor_bot.gapi.constants import SERVICE_ACCOUNT_FILE
from .helpers import parse_bloodpressure_message


logger = logging.getLogger(__name__)
USER_EMAIL = "colomboleandro@gmail.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Starting...")

    #TODO: Ask the user a gmail address
    #TODO: Share /help info

    user_email= USER_EMAIL  #FIXME

    sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user_email)
    sheet.create_shared_sheet(title=f"Bloodpressure Monitor Sheet for {user_email}")
    context.bot_data["sheet"] = sheet

    user = update.effective_user

    welcome_message = emojize(
        f"""Hi {user.mention_html()}!
A new :link: <a href="{sheet.url}">Spreadsheet Created</a> :chart_increasing:.""",
        language='alias',
    )

    await help(update==update, context=context)  #FIXME: no se ejecuta, no sé por qué

    await update.message.reply_html(welcome_message)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hola {update.effective_user.first_name}')


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        answer = "Tenés que darme un ID de un Spreadsheet :shrug:"
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return

    sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=USER_EMAIL)
    sheet.spreadsheet_id = context.args[0]
    context.bot_data["sheet"] = sheet

    await update.message.reply_text("Conecting...")

    await status(update=update, context=context)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    message = update.message.text

    parsed_message = parse_bloodpressure_message(message)

    if not parsed_message:
        answer = "Perdón, no te entendí :worried_face:"
    else:
        record = BloodPressureRecord(*parsed_message)
        try:
            sheet = context.bot_data["sheet"]
            sheet.add_record(record)

            _, sys, dia, hb = record.to_values()
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


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = -int(context.args[0]) if context.args else -1
    sheet = context.bot_data["sheet"]
    records = sheet.get_last_records(items)
    answer = ""

    for record in records:
        timestamp, sys, dia, hb = record
        answer += f":calendar: {timestamp} :heart: <strong>{sys}/{dia}</strong> {hb}\n"

    await update.message.reply_text(
        emojize(answer, language='alias'),
        parse_mode=ParseMode.HTML,
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    sheet = context.bot_data["sheet"]

    values = sheet.get_records()

    welcome_message = emojize(f"""Hi {user.mention_html()}!
Connected with GOOGLE :link: <a href="{sheet.url}">Spreadsheet</a>. 
Spreasheet has <b>{len(values)-1} records</b> :chart_increasing:.
    """, language='alias')

    await update.message.reply_html(welcome_message)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = """:robot: <strong>How to use this bot</strong> :question:

<b>Message Format</b>
- <code>sys/dia [hb]</code>: every time you message the bot with systolic/diastolic and heart beat pulse (<i>optional</i>) the bot will record in the spreadsheet.

<b>Commands:</b>
- /status: bot will share spreadsheet URL with number of records
- /last <code>[number=1]</code>: bot will share last records.
        <code>number</code> (<i>optional</i>) is used to share more than 1 record.
- /help: will print this message
- /hello: will say "hello" to the user
"""
    await update.message.reply_text(
        emojize(help_message, language='alias'),
        parse_mode=ParseMode.HTML,
    )