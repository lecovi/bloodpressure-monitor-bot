import logging

from emoji import emojize
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from bloodpressure_monitor_bot.db.core import User
from bloodpressure_monitor_bot.gapi.helpers import (
    BloodPressureSheet as Sheet,
    BloodPressureRecord,
)
from bloodpressure_monitor_bot.gapi.constants import SERVICE_ACCOUNT_FILE
from .helpers import parse_bloodpressure_message
from .constants import (
    MAIL,
    CREATE_SHEET,
    CONSENT,
    REGISTER_TA,
)

logger = logging.getLogger(__name__)



async def ask_mail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    logger.debug("========== MAIL with user %s", user)

    message = update.message.text

    if message == "No":
        message = "Bueno, si te arrepentís me podés hablar con /start"

        await update.message.reply_text(
            emojize(message, language='alias'),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END 

    message = "Decime una dirección de mail, asegurate que sea una dirección en la que se pueda compartir un Google Doc"

    await update.message.reply_text(
        emojize(message, language='alias'),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    return CREATE_SHEET


async def create_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user

    logger.debug("========== CREATE SHEET with user %s", tg_user)

    user_email = update.message.text

    message = f"Voy a crear el spreadsheet y lo voy a compartir con {user_email}"
    await update.message.reply_text(
        emojize(message, language='alias'),
        parse_mode=ParseMode.HTML,
    )

    sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user_email)
    sheet.create_shared_sheet(
        title=f"Bloodpressure Monitor Sheet for @{tg_user.username}"
    )
    context.bot_data["sheet"] = sheet

    message = f"""Hi {tg_user.mention_html()}!
A new :link: <a href="{sheet.url}">Spreadsheet Created</a> :chart_increasing:.
Querés compartir esta info de manera anónima? """
    await update.message.reply_text(
        emojize(message, language='alias'),
        parse_mode=ParseMode.HTML,
    )

    user = User.get_by_tg_id(tg_id=tg_user.id)
    if user is None:
        user = User.add(
            tg_id=tg_user.id,
            tg_username=tg_user.username,
            email=user_email,
            gsheet_id=sheet.spreadsheet_id,
        )
    else:
        user.update(email=user_email)

    message = "Esta información podría ser útil para la medicina en gral, querés compartirla anónimamente?"
    reply_keyboard = [["Compartir", "No compartir"]]

    await update.message.reply_text(
        emojize(message, language='alias'),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True,
            input_field_placeholder="Querés compartir tu información?",
        ),
    )

    return CONSENT


async def consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    sheet = context.bot_data["sheet"]

    # TODO: Registrar la respuesta del USER, IF True => Guardar en la DB

    logger.debug("========== CONSENT with user %s %s", user, sheet.spreadsheet_id)

    message = "Ahora sí, podés usarme para registra tu TA"
    await update.message.reply_text(
        emojize(message, language='alias'),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    return REGISTER_TA


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_tg_id = update.effective_user.id

    logger.debug("Responding to user %s.", user_tg_id)

    user = User.get_by_tg_id(tg_id=user_tg_id)

    if user is None:
        answer = f':wave: Hola <b>{update.effective_user.username}</b> usá /start'
        await update.message.reply_text(
            emojize(answer, language='alias'),
            parse_mode=ParseMode.HTML,
        )
        return MAIL

    message = update.message.text

    parsed_message = parse_bloodpressure_message(message)

    if not parsed_message:
        answer = "Perdón, no te entendí :worried_face:"
    else:
        record = BloodPressureRecord(*parsed_message)
        try:
            sheet = context.bot_data.get("sheet")
            if sheet is None:
                sheet = Sheet(service_account_file=SERVICE_ACCOUNT_FILE, user_email=user.email)
                sheet.spreadsheet_id = user.gsheet_id
            sheet.add_record(record)

            _, sys, dia, hb, comments = record.to_values()
            answer = f":heart: <strong>{sys}/{dia}</strong> {hb}"
            logger.info("@%s registered SYS=%s DIA=%s HB=%s comments=%s",
                update.effective_user['username'],
                sys,
                dia,
                hb,
                comments,
            )
        except Exception as e:
            answer = ":collision: Something went wrong trying to add record :collision:"
            logger.error(e)

    await update.message.reply_text(
        emojize(answer, language='alias'),
        parse_mode=ParseMode.HTML,
    )
    return REGISTER_TA
