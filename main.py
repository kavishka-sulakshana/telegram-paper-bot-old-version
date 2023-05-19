
import logging
from typing import Dict

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import os
import keyBoards

from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Starting the program of telegram bot ____________________________________________________________________________

# States
TYPING_BARCODE, CHOOSING, TYPING_PAPER = range(3)

markup_1 = ReplyKeyboardMarkup(keyBoards.reply_keyboard_1, one_time_keyboard=True)


# Functions for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "This bot will help you to get your papers and marks\n"
        "Choose an option : ",
        reply_markup=markup_1,
    )
    return TYPING_BARCODE


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data: Dict[str, str] = context.user_data
    user_data.clear()
    await update.message.reply_text("Bye! I hope we can talk again some day.")
    return ConversationHandler.END


# Main Function
def main() -> None:
    application = Application.builder().token(os.getenv("API_TOKEN")).build()

    # Add conversation handler with the states that defined above
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [

            ],
            TYPING_BARCODE: [

            ],
            TYPING_PAPER: [

            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌  Close"), done)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()