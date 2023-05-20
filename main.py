
import logging
import pprint
import requests
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
import helperFunctions

from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Starting the program of telegram bot ____________________________________________________________________________

WEBHOOK_LINK_2 = os.getenv("WEBHOOK_PAPERS")
WEBHOOK_LINK_CMP = os.getenv("WEBHOOK_COMPS")


# States
TYPING_BARCODE, CHOOSING, TYPING_PAPER, TYPING_ISSUE = range(4)

markup_1 = ReplyKeyboardMarkup(keyBoards.reply_keyboard_1, one_time_keyboard=True)


# Functions for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Enter your barcode : "
    )
    return TYPING_BARCODE


async def enter_barcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["barcode"] = text
    await update.message.reply_text(
        "This bot will help you to get your papers and marks\n"
        "Choose an option : "
        , reply_markup=markup_1
    )
    return CHOOSING


async def enter_paper_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["paper"] = text
    # pprint.pprint(context.user_data)

    if context.user_data["choice"] == "🔖  Get Marks":
        params = {"barcode": context.user_data["barcode"], "paper_no": context.user_data["paper"]}
        paper_no = params["paper_no"]
        sheet_id = "Paper " + params["paper_no"]
        data = {"message": params['barcode'], "chat_id": update.message.chat_id, "paper_no": paper_no, "sheet_id": sheet_id}
        response = requests.post(WEBHOOK_LINK_2, data=data)
        response_data = response.json()

        if response_data["status"] == "success":
            data_record = response_data["data"][0]
            await update.message.reply_html(helperFunctions.generate_beautiful_message(
                name=data_record[1],
                marks=data_record[4],
                Drank=data_record[0],
                Arank="-",
                link="-",
                year="2023",
                paper_no=paper_no,
                ptype="ONLINE"
            ))
        elif response_data["status"] == "failed":
            await update.message.reply_text(response_data["message"])
        else:
            await update.message.reply_text("Something went wrong")

    elif context.user_data["choice"] == "🧾  Get Paper":
        await update.message.reply_html("This Feature is not available yet.")
    else:
        await update.message.reply_text("Invalid Choice")

    await update.message.reply_text(
        "Choose an option : "
        , reply_markup=markup_1
    )
    return CHOOSING


async def get_marks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        "Enter your paper no : "
    )
    return TYPING_PAPER


async def get_papers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        "Enter your paper no : "
    )
    return TYPING_PAPER


async def paper_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text(
        "Enter Your Complaint : "
    )
    return TYPING_ISSUE


async def enter_paper_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["issue"] = text
    data = {
        "barcode": context.user_data['barcode'],
        "chat_id": update.message.chat_id,
        "complaint": context.user_data["issue"]
    }

    response = requests.post(WEBHOOK_LINK_CMP, data=data)
    response_data = response.json()
    if response_data["status"] == "success":
        await update.message.reply_text(
            "\n 👨🏼‍💻 Your Complaint has been recorded !  📥 \n"
            "\n 🎲  We will check it soon 🔰🔰 \n"
        )
    else:
        await update.message.reply_text(response_data["message"])

    await update.message.reply_text(
        "Choose an option : "
        , reply_markup=markup_1
    )
    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data.clear()
    await update.message.reply_html(
        "\n<b>👋🏼 Bye! </b>\n"
        "\nGood Luck for your exams. 😄😄\n"
        "\n<u>To start again</u> /start 😎\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# Main Function
def main() -> None:
    application = Application.builder().token(os.getenv("API_TOKEN")).build()

    # Add conversation handler with the states that defined above
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^🔖  Get Marks$"), get_marks
                ),
                MessageHandler(
                    filters.Regex("^🧾  Get Paper$"), get_papers
                ),
                MessageHandler(
                    filters.Regex("^📍 Paper Issues$"), paper_issue
                ),
            ],
            TYPING_BARCODE: [
                MessageHandler(
                    filters.Regex("^[0-9]{8,10}$"), enter_barcode
                )
            ],
            TYPING_PAPER: [
                MessageHandler(
                    filters.Regex("^[0-9]{2}$"), enter_paper_no
                )
            ],
            TYPING_ISSUE: [
                MessageHandler(
                    filters.TEXT, enter_paper_issue
                )
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^❌  Close"), done)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()