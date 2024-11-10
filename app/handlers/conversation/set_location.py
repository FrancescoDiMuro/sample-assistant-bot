from __future__ import annotations
from constants.emoji import Emoji
from models.location.crud.create import create_location
from models.location.crud.update import update_location
from models.user.crud.retrieve import retrieve_user
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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
async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the user Telegram id
    user_telegram_id = update.effective_user.id
    
    # Get the user from db
    if user := retrieve_user(user_telegram_id=user_telegram_id):

        # Save the user id in the context user data dictionary
        context.user_data["user_id"] = user.id

        # Check if the user has already a location
        if location := user.location:

            # Save the location id in the context user data dictionary
            context.user_data["location_id"] = location.id

            user_text = (
                f"{Emoji.ROUND_PUSHPIN} You've already set your location.\n"
                "You can either answer the question, or use the /cancel command "
                "to cancel this operation.\n"
                "Do you want to overwrite it?"
            )

            # Set the keyboard buttons
            keyboard = [
                [KeyboardButton(text="Yes")],
                [KeyboardButton(text="No")]
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

            user_text = "Click on the button below to set your location\n"
            "(or use the /cancel command to cancel this operation):"

            # Set the keyboard buttons
            keyboard = [
                [KeyboardButton(text=f"Set location {Emoji.ROUND_PUSHPIN}", request_location=True)]
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

            return INPUT_LOCATION

    else:

        user_text = (
                f"{Emoji.CROSS_MARK} It seems that you didn't sign-up.\n"
                "In order to use this command, you must sign-up."
        )

        await update.message.reply_text(text=user_text)

        return ConversationHandler.END
    

# Step USER_CHOICE
async def user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the user's choice
    user_choice_message: str = update.message.text.lower()

    # Check user choice
    if user_choice_message == "yes":

        user_text = "Click on the button below to set your location:"

        # Set the keyboard buttons
        keyboard = [
            [KeyboardButton(text=f"Set location {Emoji.ROUND_PUSHPIN}", request_location=True)]
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

        # Go to the next ConversationHandler step
        return INPUT_LOCATION
        
    elif user_choice_message == "no":

        user_text = f"{Emoji.PERSON_SHRUGGING} As requested, your location has not been updated."

        await update.message.reply_text(
            text=user_text,
            reply_markup=ReplyKeyboardRemove()
        )

        # End the conversation
        return ConversationHandler.END

    else:

        user_text = (
            f"{Emoji.CROSS_MARK} Invalid text.\n"
            "Please provide a valid entry using the keyboard below,\n"
            "or use the command /cancel to cancel this operation:"
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
        location_data: dict = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude
        }

        # If a location id is found (and deleted) in the context user data dictionary,
        # it means that the location was already set, and so it needs to be updated
        if location_id := context.user_data.pop("location_id", None):

            # Update the user's location in the db
            location_id = update_location(
                location_id=location_id,
                location_data=location_data
            )

            # Check if the location has been correctly updated
            if location_id:

                user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} Your location has been correctly updated."

                await update.message.reply_text(
                    text=user_text,
                    reply_markup=ReplyKeyboardRemove()
                )

        # Otherwise, the location wasn't set, and so it needs to be created
        else:

            # Save the user's location in the db
            location_id = create_location(location_data=location_data)

            # Check if the location has been correctly created
            if location_id:

                user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} Your location has been correctly saved."

                await update.message.reply_text(
                    text=user_text,
                    reply_markup=ReplyKeyboardRemove()
                )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Context user's data dictionary clean-up
    context.user_data.pop("user_id", None)
    context.user_data.pop("location_id", None)


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


# Filter warnings from CallbackQueryHandler
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# Handler definition
set_location_handler = ConversationHandler(
    entry_points=[
            CommandHandler(command="setlocation", callback=set_location)
    ],
    states={
        USER_CHOICE: [
            MessageHandler(
                filters=filters.TEXT & ~filters.Regex(r"^\/cancel$"),
                callback=user_choice)
        ],
        INPUT_LOCATION: [
            MessageHandler(filters=filters.LOCATION, callback=input_location),
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
