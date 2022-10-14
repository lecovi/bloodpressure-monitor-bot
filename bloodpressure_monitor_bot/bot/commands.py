from datetime import datetime
import logging

from emoji import emojize
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

from bloodpressure_monitor_bot.db.core import User
from bloodpressure_monitor_bot.gapi.helpers import BloodPressureSheet as Sheet
from bloodpressure_monitor_bot.gapi.constants import SERVICE_ACCOUNT_FILE
from .constants import (
    HELP_MESSAGE,
    MAIL,
    REGISTER_TA,
)


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Starting...")
    # Everything is inside update.effective_user object
    #     full_name == f"{first_name} {last_name}"
    #     name == f"@{username}"
    #     link == f"https://t.me/{username}"
    user = update.effective_user

    logger.debug("~~~~~~~~~~~~~~~ Starting with user %s", user)

    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        emojize(HELP_MESSAGE, language='alias'),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True,
            input_field_placeholder="Do you want to continue?",
        ),
    )

    return MAIL


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        answer = "Tenés que darme un ID de un Spreadsheet :shrug:"
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return REGISTER_TA

    tg_id = update.effective_user.username
    gsheet_id = context.args[0]

    user = User.get_by_tg_id(tg_id=tg_id)
    if user is None:
        answer = f':wave: Hola <b>{update.effective_user.username}</b> usá /start'
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return MAIL

    user.update(gsheet_id=gsheet_id)

    logger.debug("User %s connecting %s Google Spreadsheet", tg_id, gsheet_id)

    sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user.email)
    sheet.spreadsheet_id = gsheet_id
    context.bot_data["sheet"] = sheet

    await update.message.reply_text("Conecting...")

    await status(update=update, context=context)


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    items = -int(context.args[0]) if context.args else -1

    user = User.get_by_tg_id(tg_id=tg_user.id)
    if user is None:
        answer = f':wave: Hola <b>{tg_user.username}</b> usá /start'
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END


    logger.debug("User %s asked last {%s} items.", tg_user.first_name, items)

    sheet = context.bot_data.get("sheet")
    if sheet is None:
        sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user.email)
        sheet.spreadsheet_id = user.gsheet_id

    records = sheet.get_last_records(items)
    answer = ""

    for record in records:
        timestamp, sys, dia, hb = record
        timestamp = datetime.fromisoformat(timestamp).strftime("%c")
        answer += f":calendar: {timestamp} :heart: <strong>{sys}/{dia}</strong> {hb}\n"

    await update.message.reply_text(
        emojize(answer, language='alias'),
        parse_mode=ParseMode.HTML,
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    
    user = User.get_by_tg_id(tg_id=tg_user.id)
    if user is None:
        answer = f':wave: Hola <b>{tg_user.username}</b> usá /start'
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    logger.debug("User %s asked for status.", tg_user.first_name)

    sheet = context.bot_data.get("sheet")
    if sheet is None:
        sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user.email)
        sheet.spreadsheet_id = user.gsheet_id

    values = sheet.get_records()

    welcome_message = emojize(f"""Hi {tg_user.mention_html()}!
Connected with GOOGLE :link: <a href="{sheet.url}">Spreadsheet</a>. 
Spreasheet has <b>{len(values)-1} records</b> :chart_increasing:.
    """, language='alias')

    await update.message.reply_html(welcome_message)

    return REGISTER_TA


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user

    logger.debug("User %s asked for help.", user.first_name)

    await update.message.reply_text(
        emojize(HELP_MESSAGE, language='alias'),
        parse_mode=ParseMode.HTML,
    )

    return REGISTER_TA


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        "Bye! I hope we can talk again some day. Start again with /start",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
