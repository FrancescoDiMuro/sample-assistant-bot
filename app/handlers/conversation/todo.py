from __future__ import annotations
from constants.emoji import Emoji
from datetime import datetime, timedelta, timezone
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
from timezonefinder import TimezoneFinder
from warnings import filterwarnings
from zoneinfo import ZoneInfo


# Conversation Handler steps
INPUT_TODO_DETAILS, SELECT_TODO_DUE_DATE, INPUT_TODO_DUE_TIME = range(3)

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
    

async def input_todo_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Store the todo details
    context.user_data["todo_data"]["details"] = update.message.text    

    # Show the calendar to the user for the current month and year
    inline_calendar = create_calendar()

    user_text = (
        f"{Emoji.CALENDAR} Select the due date:"
    )

    await update.message.reply_text(
        text=user_text,
        reply_markup=inline_calendar
    )

    # Next step
    return SELECT_TODO_DUE_DATE


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
    return SELECT_TODO_DUE_DATE


async def select_todo_due_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    # Get the expires on date and store it in the context user data dictionary
    due_date = query.data
    context.user_data["todo_data"]["due_date"] = due_date

    # Edit the message to remove the keyboard and show the user the selected date
    user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} Due date selected: {due_date}"
    await query.edit_message_text(text=user_text)

    user_text = f"{Emoji.ALARM_CLOCK} Select the hour for the due time:"

    # Create the hours keyboard
    hours_keyboard = create_hours_keyboard()
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=user_text,
        reply_markup=hours_keyboard
    )
    
    return INPUT_TODO_DUE_TIME


def create_hours_keyboard() -> ReplyKeyboardMarkup:

    # Create the keyboard for the hour selection
    # Using a list comprehension with nested loops
    keyboard: list = [
        [KeyboardButton(text=f"{hour:02d}:{minute:02d}")]
        for hour in range (0, 24)
        for minute in range(0, 60, 5)
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        one_time_keyboard=True,
        resize_keyboard=True,
        is_persistent=False
    )


async def handle_calendar_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # This function simply ignores every callback query coming from any other button
    # in the inline keyboard, just to not have a callback query hanging around until 
    # the timeout
    
    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    return SELECT_TODO_DUE_DATE


async def input_todo_due_time(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the due time
    due_time: str = update.message.text

    # Get the due date
    due_date = context.user_data["todo_data"]["due_date"]

    # Concatenate the due date and time 
    due_full = f"{due_date} {due_time}"

    # Convert the due date and time datetime format
    due_dt = datetime.strptime(due_full, "%Y-%m-%d %H:%M")

    # Get the user time zone and UTC offset based on the user's location and the (local) due_dt
    user_tzinfo, utc_offset =  await get_user_utc_offset(
        user_telegram_id=update.effective_user.id, 
        local_naive_dt=due_dt
    )

    # If the UTC offset has been correctly extracted
    if utc_offset:

        # Convert the naive datetime in an aware datetime in the user tzinfo
        due_dt = due_dt.astimezone(user_tzinfo)

        # Get the current time in UTC format
        utc_current_time = datetime.now(tz=timezone.utc)

        # Compare the user due time (in UTC) and the UTC current time
        if due_dt  <= utc_current_time:

            # Create the hours keyboard
            hours_keyboard = create_hours_keyboard()
            
            user_text = (
                f"{Emoji.WARNING_SIGN} Warning!\n"
                "The inserted time is invalid (becasue it's already past or current).\n"
                "Please insert another time:"
            )

            await update.message.reply_text(
                text=user_text,
                reply_markup=hours_keyboard
            )

            return INPUT_TODO_DUE_TIME

        # Transform the due_dt in UTC format
        due_dt_utc = due_dt - timedelta(seconds=utc_offset)

        # Overwrite the due_date value with full converted due datetime
        context.user_data["todo_data"]["due_date"] = due_dt_utc
        
        # Save the utc offset to the context user data dictionary
        context.user_data["todo_data"]["utc_offset"] = utc_offset

        # If there is the todo_data dictionary
        if todo_data := context.user_data.pop("todo_data"):
        
            # Save the todo to db
            if create_todo(todo_data=todo_data):
                user_text = f"{Emoji.WHITE_HEAVY_CHECK_MARK} To-Do saved correctly."

    else:

        user_text = (
            f"{Emoji.WARNING_SIGN} Warning!\n"
            "Something went wrong during the todo save.\n"
            "Check that you correctly setup a location and try again."
        )

    await update.message.reply_text(
            text=user_text,
            reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


async def invalid_todo_due_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_text = (
        f"{Emoji.WARNING_SIGN} Warning!\n"
        "The typed due time is not valid.\n"
        "Please use one of the provided due time in the keboard below, "
        "or type them in the correct format <i>hh:mm</i> (E.g. 12:35):"
    )

    await update.message.reply_text(text=user_text)

    return INPUT_TODO_DUE_TIME


async def get_user_utc_offset(user_telegram_id: int, local_naive_dt: datetime):

    # Transform the local dt (datetime) in a timestamp object
    local_dt_timestamp = local_naive_dt.timestamp()

    # Tranform the local timestamp in utc dt (datetime)
    utc_dt = datetime.fromtimestamp(local_dt_timestamp, tz=timezone.utc)

    # Get the user location to find out what is its timezone
    if user := retrieve_user(user_telegram_id=user_telegram_id):

        # If the location is correctly retrieved
        if location := user.location:

            # Get the latitude and longitude from the user's location
            latitude, longitude = location.latitude, location.longitude

            # If the user's timezone is correctly obtained
            if user_timezone := TimezoneFinder().timezone_at(lat=latitude, lng=longitude):

                # Get the user time zone info
                user_tzinfo = ZoneInfo(key=user_timezone)

                # Get the UTC offset by the user_timezone
                utc_offset = utc_dt.replace(tzinfo=user_tzinfo).strftime("%z")

                # Get the sign, hours an minutes for the offset
                sign, hours, minutes = utc_offset[0], int(utc_offset[1:3]), int(utc_offset[3:5])

                # Convert the utc offset in seconds
                utc_offset = int(f"{sign}{(hours * 60 * 60) + (minutes * 60)}")

                return [user_tzinfo, utc_offset]
            
    return None


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
        SELECT_TODO_DUE_DATE: [
            CallbackQueryHandler(
                pattern=r"^\d{4}\-\d{2}\-\d{2}$",
                callback=select_todo_due_date
            ),
            CallbackQueryHandler(
                pattern=r"^(?:<|>)\d{4}\-\d+$",
                callback=handle_calendar_move_month
            ),
        ],
        INPUT_TODO_DUE_TIME: [
            MessageHandler(
                filters=filters.Regex(
                    pattern=VALID_INPUT_TIME_PATTERN_COMPILED
                ) & ~filters.Regex(r"^\/cancel$"),
                callback=input_todo_due_time
            ),
            MessageHandler(
                filters=filters.TEXT & ~filters.Regex(r"^\/cancel$"),
                callback=invalid_todo_due_time
            )
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
