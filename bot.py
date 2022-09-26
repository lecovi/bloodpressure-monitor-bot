import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from bloodpressure_monitor_bot.bot.errors import error_handler
from bloodpressure_monitor_bot.bot.commands import (
    start,
    hello,
    last,
    echo,
    status,
    help,
    connect,
) 


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)


with open("credentials/telegram_bot.token") as f:
    TOKEN = f.read().strip()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("last", last))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("connect", connect))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.add_error_handler(error_handler)


app.run_polling()
