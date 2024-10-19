from __future__ import annotations
from datetime import datetime
from constants.emoji import Emoji
from models.todo.crud.create import create_todo
from models.user.crud.retrieve import retrieve_user
from handlers.utils.inline_calendar import create_calendar
from re import compile, IGNORECASE, X
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationHandlerStop, 
    CallbackQueryHandler,
    ContextTypes, 
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    filters
)
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings


# Conversation Handler steps
INPUT_TODO_DETAILS, SELECT_TODO_COMPLETION_DATE, INPUT_TODO_COMPLETION_TIME = range(3)

# Time pattern to validate the user's input
VALID_INPUT_TIME_PATTERN: str = r"^(?:[0-1]\d|2[0-3]):(?:[0-5]\d)$"

# Same as above, but compiled (for the MessageHandler filter)
VALID_INPUT_TIME_PATTERN_COMPILED = compile(
    pattern=VALID_INPUT_TIME_PATTERN,
    flags=IGNORECASE | X
)


# Entry point
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Initialize an empty dictionary to store the user's todo data
    context.user_data["todo_data"] = {}

    # Get the user Telegram id
    user_telegram_id = update.effective_user.id
    
    # Get the user from db
    if user := retrieve_user(user_telegram_id=user_telegram_id):
        
        # Save the user id in the context user data dictionary
        context.user_data["todo_data"]["user_id"] = user.id

        user_text = (
            f"{Emoji.SQUARED_NEW} You are creating a new To-Do.\n"
            "You can always cancel this operation using the /cancel command.\n"
            "Tell me some details about it:"
        )

        await update.message.reply_text(text=user_text)

        # Next step
        return INPUT_TODO_DETAILS
    
    else:

        user_text = (
            f"{Emoji.CROSS_MARK} User not found!\n"
            "Are you sure that you signed-up?"
        )

        await update.message.reply_text(text=user_text)

        return ConversationHandler.END
    

# Step USER_CHOICE
async def input_todo_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Store the todo details
    context.user_data["todo_data"]["details"] = update.message.text    

    # Show the calendar to the user for the current month and year
    inline_calendar = create_calendar()

    user_text = (
        f"{Emoji.CALENDAR} Select the date of completion:"
    )

    await update.message.reply_text(
        text=user_text,
        reply_markup=inline_calendar
    )

    # Next step
    return SELECT_TODO_COMPLETION_DATE


async def handle_calendar_move_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    # Get the callback data
    callback_data = query.data
    
    # Get the year and the month to build the calendar for the previous month
    year, month = [
        int(item) 
        for item in callback_data.replace("<", "").replace(">", "").split("-")
    ]
    
    # Create the calendar
    inline_calendar = create_calendar(year=year, month=month)

    # Edit the message
    await query.edit_message_reply_markup(inline_calendar)

    # Return to the date selection step
    return SELECT_TODO_COMPLETION_DATE


async def select_todo_completion_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    expires_on_date = query.data
                
    context.user_data["todo_data"]["expires_on"] = expires_on_date

    user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} Date of completion selected: {expires_on_date}"
    await query.edit_message_text(text=user_text)

    user_text = f"{Emoji.ALARM_CLOCK} Select the hour for the completion time:"

    keyboard: list = []

    for hour in range(0, 24):

        for minute in range(0, 60, 5):

            time = f"{hour:02d}:{minute:02d}"

            button = KeyboardButton(text=time)

            keyboard.append([button])
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=user_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=False
        )
    )
    
    return INPUT_TODO_COMPLETION_TIME


async def handle_calendar_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    return SELECT_TODO_COMPLETION_DATE


async def input_todo_completion_time(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the time expiration
    expires_on_time: str = update.message.text

    # If there is the todo_data dictionary
    if todo_data := context.user_data.pop("todo_data"):
                
        # Get the full date and concatenate to it the time expiration
        expires_on: str = f"{todo_data["expires_on"]} {expires_on_time}"
        
        # Transform the expires_on str in a datetime with the specified format
        expires_on: datetime = datetime.strptime(expires_on, "%Y-%m-%d %H:%M")

        # Overwrite the expires_on field from str to datetime
        # TODO: it has to be save in UTC format!
        todo_data["expires_on"] = expires_on

        # Save the todo to db
        if create_todo(todo_data=todo_data):

            await update.message.reply_text(
                f"{Emoji.WHITE_HEAVY_CHECK_MARK} To-Do data saved!",
                reply_markup=ReplyKeyboardRemove()
            )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Context user's data dictionary clean-up
    context.user_data.pop("todo_data")

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
create_todo_handler = ConversationHandler(
    entry_points=[
            CommandHandler(
                command="todo", 
                callback=todo
            )
    ],
    states={
        INPUT_TODO_DETAILS: [
            MessageHandler(
                filters=filters.TEXT & ~filters.Regex(r"^\/cancel$"),
                callback=input_todo_details
            )
        ],
        SELECT_TODO_COMPLETION_DATE: [
            CallbackQueryHandler(
                pattern=r"^\d{4}\-\d{2}\-\d{2}$",
                callback=select_todo_completion_date
            ),
            CallbackQueryHandler(
                pattern=r"^(?:<|>)\d{4}\-\d+$",
                callback=handle_calendar_move_month
            ),
        ],
        INPUT_TODO_COMPLETION_TIME: [
            MessageHandler(
                filters=filters.Regex(pattern=VALID_INPUT_TIME_PATTERN_COMPILED) & ~filters.Regex(r"^\/cancel$"),
                callback=input_todo_completion_time
            ),
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
