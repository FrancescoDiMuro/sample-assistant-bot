from constants.emoji import Emoji
from telegram import Update
from telegram.ext import (
    ApplicationHandlerStop, 
    ContextTypes, 
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    filters
)
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings


# Conversation Handler steps
INPUT_LOCATION: int = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Get user first name
    user_first_name: str = update.effective_user.first_name

    # User text
    user_text: str = (
        f"Hello {user_first_name} {Emoji.WAVING_HAND_SIGN}\n"
        f"I'm your personal assistant bot {Emoji.ROBOT}\n"
        "Using the provided commands, you can ask me to:\n"
        f"- tell you the weather {Emoji.BLACK_SUN_WITH_RAYS}\n"
        f"- remind you to do a task {Emoji.SPEECH_BALLOON}\n"
        f"- tell you the news {Emoji.NEWSPAPER}\n"
        "For example:\n"
        "- <i>Hey Bot, what's the weather like?</i>\n"
        "or\n"
        "- using the command <i>/weather</i>\n\n"
        "Now, in order to send you location-related information,\n"
        "I need that you send me a location.\n"
        "You can either set it now,\n"
        "or use the command /skip to do it further.\n"
        "Invoking commands which require a location will fail,\n"
        "but you can always set it through the command /setlocation.\n"
        "If you want, send me the location using the 'Location' button on Telegram:"
    )

    await update.message.reply_text(text=user_text)

    return INPUT_LOCATION


async def input_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the latitude and longitude from the message
    latitude = update.message.location.latitude
    longitude = update.message.location.latitude

    # If the location is correctly obtained
    if latitude and longitude:

        # Save the user's location in the db

        await update.message.reply_text(f"Location set up correctly: {latitude}, {longitude}")

    return ConversationHandler.END


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_text: str = (
        f"{Emoji.RIGHTWARD_ARROW} Location skipped.\n"
        "You can always set it up later with the command /setlocation."
    )

    await update.message.reply_text(text=user_text)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(text=f"{Emoji.STOP_SIGN} Operation canceled.")

    return ConversationHandler.END


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # User text
    user_text: str = (
        f"{Emoji.CROSS_MARK} You can't use bot commands or use any other message type now!\n"
        "Type the command /cancel to exit this procedure."
    )
    
    await update.message.reply_text(text=user_text)
    
    # The ConversationHandler remains in the state it was before,
    # but the update is not passed to other handlers
    raise ApplicationHandlerStop()


# Filter warnings from CallbackQueryHandler
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# Handler definition
start_handler = ConversationHandler(
    entry_points=[
            CommandHandler(command="start", callback=start)
    ],
    states={
        INPUT_LOCATION: [
            MessageHandler(filters=filters.LOCATION, callback=input_location),
            CommandHandler(command="skip", callback=skip_location)
        ]
    },
    fallbacks=[
        CommandHandler(
            command="cancel", 
            callback=cancel
        ),
        # The order matters!
        # filters.COMMAND filters all the messages that are a command (starting with /),
        # while ~filters.TEXT filters all the messages that are not a text, but since
        # /sample_command is a text, it's not filtered just with the second filter (on the text)
        MessageHandler(
            filters=filters.COMMAND | ~filters.TEXT,
            callback=handle_unknown
        )
    ]
)