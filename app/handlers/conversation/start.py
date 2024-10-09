from __future__ import annotations
from constants.emoji import Emoji
from models.location.crud.create import create_location
from models.user.crud.create import create_user
from models.user.crud.retrieve import retrieve_user
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, User
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
USER_CHOICE, INPUT_LOCATION = range(2)


# Entry point
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Get the Telegram user from the update
    telegram_user = update.effective_user

    # Get the user Telegram id
    user_telegram_id: int = telegram_user.id

    # Get user first name
    user_first_name: str = telegram_user.first_name

    # If the user doesn't already exist in the db
    if not (user := retrieve_user(user_telegram_id=user_telegram_id)):

        # User text
        user_text: str = (
            f"Hello {user_first_name} {Emoji.WAVING_HAND_SIGN}\n"
            f"This is your personal assistant bot {Emoji.ROBOT}\n\n"
            "Before we start, you need to be informed about a couple of things:\n"
            "1. this bot will store part of the data that is publicly visibile in your Telegram account, "
            "like your first name, last name (if set), your Telegram's username (if set), "
            "and your Telegram's user ID;\n"
            "2. some commands require your location.\n"
            "Since this bot is bornt with sample purposes, you don't have to share your <i>actual</i> location,"
            "but any location to let you use location related commands.\n"
            "Whenever you want, you can set another location with the command /setlocation.\n"
            "These information are stored securely, and they are not shared with anybody.\n\n"
            "Since it's the first time you use this bot, you're going to be asked if you want to proceed, "
            "accepting that your data is going to be stored, or to not proceed, "
            "refusing that your data is going to be stored.\n"
            "In the last case, it's not possible to use the bot, since every command is user "
            "and location related.\n\n"
            "Do you want to proceed?"
        )

        # Set the keyboard buttons
        keyboard = [
            [KeyboardButton(text=f"Yes")],
            [KeyboardButton(text=f"No")]
        ]
        
        # Create the keyboard
        reply_keyboard_markup = ReplyKeyboardMarkup(
            keyboard=keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        )

        # Reply to the user
        await update.message.reply_text(
            text=user_text,
            reply_markup=reply_keyboard_markup
        )

        return USER_CHOICE
    
    else:

        # If the user already set the location
        if user.has_location:

            # User text
            user_text: str = (
                f"Hello again {user_first_name} {Emoji.WAVING_HAND_SIGN}\n"
                "You've already set up everything to start to use this bot.\n"
                "You can use the provided commands to interact with the bot, "
                "the ones that you can find clicking on the 'Menu' button on the left "
                "of the input textbox.\n"
                f"{Emoji.SOUTH_WEST_ARROW}"
            )

            await update.message.reply_text(text=user_text)
        
        else:

            user_text = (
                f"{Emoji.THINKING_FACE} It seems that you still didn't set a location.\n"
                "If you want to use location related commands, remember to set it through the command /setLocation."
            )

            await update.message.reply_text(text=user_text)
    

# Step USER_CHOICE
async def user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the user's choice
    user_choice_message: str = update.message.text.lower()

    # Check user choice
    if user_choice_message == "yes":

        # Extract the user's info
        user_data = get_user_info(telegram_user=update.effective_user)

        # Save user's info
        user_id = create_user(user_data=user_data)

        # Check if the user has been correctly created
        if user_id:
        
            # Save the user id in its context user_data's dictionary
            context.user_data["user_id"] = user_id

            user_text = (
                f"{Emoji.WHITE_HEAVY_CHECK_MARK} You accepted to share your information.\n"
                "Your public information (first name, last name, username, Telegram id) have been saved.\n"
                "Now, send me your location clicking on "
                f"{Emoji.PAPERCLIP} button {Emoji.RIGHTWARD_ARROW} Location,\n"
                "or use the /skip command to don't set your location now."
            )

        await update.message.reply_text(
            text=user_text,
            reply_markup=ReplyKeyboardRemove()
        )

        # Move to the next Conversation Handler step
        return INPUT_LOCATION
        
    elif user_choice_message == "no":

        user_text = (
            f"{Emoji.NO_ENTRY} You refused to share your information.\n"
            f"As stated before, the use of the majority of the bot's commands are user and location dependent, "
            "so, if you want to use the bot, use the /start command again and press 'Yes'."
        )

        await update.message.reply_text(
            text=user_text,
            reply_markup=ReplyKeyboardRemove()
        )

        # End the conversation
        return ConversationHandler.END

    else:

        user_text = (
            f"{Emoji.CROSS_MARK} Invalid text.\n"
            "Please provide a valid entry using the keyboard below\n"
            f"<i>(click on the right icon you can find near the message text box):</i>"
        )

        await update.message.reply_text(text=user_text)

        # Return to this step
        return USER_CHOICE


async def input_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the latitude and longitude from the message
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    # If the location is correctly obtained
    if latitude and longitude:

        # Get (and delete) the user id from its context user_data's dictionary
        user_id = context.user_data.pop("user_id")

        # Set the location data
        location_data = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Save the user's location in the db
        location_id = create_location(location_data=location_data)

        # Check if the location has been correctly created
        if location_id:

            user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} Your data has been correctly saved."

            await update.message.reply_text(text=user_text)

    return ConversationHandler.END


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_text: str = (
        f"{Emoji.RUNNER} Location skipped.\n"
        "You can always set it up later with the command /setlocation."
    )

    await update.message.reply_text(text=user_text)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Context user's data dictionary clean-up
    context.user_data.pop("user_id")

    await update.message.reply_text(
        text=f"{Emoji.STOP_SIGN} Operation canceled.",
        reply_markup=ReplyKeyboardRemove()
    )

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


def get_user_info(telegram_user: User) -> dict:

    return {
        "first_name": telegram_user.first_name,
        "last_name": telegram_user.last_name,
        "username": f"@{username}" if (username := telegram_user.username) else None,
        "telegram_id": telegram_user.id
    }


# Filter warnings from CallbackQueryHandler
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# Handler definition
start_handler = ConversationHandler(
    entry_points=[
            CommandHandler(command="start", callback=start)
    ],
    states={
        USER_CHOICE: [
            MessageHandler(filters=filters.TEXT, callback=user_choice)
        ],
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
