import os
import logging

from telegram import MessageEntity
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bloodpressure_monitor_bot.bot.errors import error_handler
from bloodpressure_monitor_bot.bot.commands import (
    start,
    last,
    status,
    help,
    connect,
    cancel,
)
from bloodpressure_monitor_bot.bot.conversation import (
    ask_mail,
    create_sheet,
    consent,
    echo,
)
from bloodpressure_monitor_bot.bot.constants import (
    MAIL, 
    CONSENT,
    CREATE_SHEET,
    REGISTER_TA,
)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


TG_TOKEN_FILE=os.getenv("TG_TOKEN_FILE")
with open(TG_TOKEN_FILE) as f:
    TOKEN = f.read().strip()


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MAIL: [
            MessageHandler(filters.Regex("^(Yes|No)$"), ask_mail),
        ],
        CREATE_SHEET: [
            MessageHandler(filters.Entity(MessageEntity.EMAIL), create_sheet),
        ],
        CONSENT: [
            MessageHandler(filters.Regex("^(Compartir|No compartir)$"), consent),
        ],
        REGISTER_TA: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, echo),
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
    ],
)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("last", last))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("connect", connect))

app.add_handler(conversation_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.add_error_handler(error_handler)


app.run_polling()
