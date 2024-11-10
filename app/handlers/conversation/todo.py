from __future__ import annotations
from constants.emoji import Emoji
from datetime import datetime, timedelta, UTC
from handlers.utils.inline_calendar import create_calendar
from jobs.remind_user_job import remind_user_job
from models.reminder.crud.create import create_reminder
from models.todo.crud.create import create_todo
from models.user.crud.retrieve import retrieve_user
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
from uuid import UUID
from warnings import filterwarnings
from zoneinfo import ZoneInfo


# Conversation Handler steps
INPUT_TODO_DETAILS, SELECT_TODO_DUE_DATE, \
INPUT_TODO_DUE_TIME, USER_CHOICE, \
SELECT_REMINDER_TIME = range(5)

# Time pattern to validate the user's input
VALID_INPUT_TIME_PATTERN: str = r"^(?:[0-1]\d|2[0-3]):(?:[0-5]\d)$"

# Same as above, but compiled (for the MessageHandler filter)
VALID_INPUT_TIME_PATTERN_COMPILED = compile(
    pattern=VALID_INPUT_TIME_PATTERN,
    flags=IGNORECASE | X
)

# Yes | No pattern for the user choice
YES_NO_PATTERN: str = r"^yes|no$"

# Same as above, but compiled
YES_NO_PATTERN_COMPILED = compile(
    pattern=YES_NO_PATTERN,
    flags=IGNORECASE
)

# Reminder time pattern
REMINDER_TIME_PATTERN: str = (
    r"^" 
    r"(?:(?:5|[1-5][05])\sminutes\sbefore)"
    r"|"
    r"(?:1\shour|(?:[2-9]|1[0-9]|2[0-3])\shours)\sbefore"
    r"|"
    r"(?:1\sday|(?:[2-9]|1[0-9]|2[0-3])\sdays)\sbefore"
    r"$"
)

# Same as above, but compiled
REMINDER_TIME_PATTERN_COMPILED = compile(
    pattern=REMINDER_TIME_PATTERN,
    flags=X
)


# Entry point
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Initialize an empty dictionary to store the user's todo data
    context.user_data["todo_data"] = {}

    # Get the user Telegram id
    user_telegram_id = update.effective_user.id
    
    # Get the user from db
    if user := retrieve_user(user_telegram_id=user_telegram_id):

        # If the user has a location associated
        if user.location:
        
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
                f"{Emoji.CROSS_MARK} It seems that you didn't set a location.\n"
                "In order to use this command, you must set a location."
            )

            await update.message.reply_text(text=user_text)

            return ConversationHandler.END
    
    else:

        user_text = (
                f"{Emoji.CROSS_MARK} It seems that you didn't sign-up.\n"
                "In order to use this command, you must sign-up."
        )

        await update.message.reply_text(text=user_text)

        return ConversationHandler.END
    
    
# Step 1
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


# Step 2
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

    user_text = f"{Emoji.CLOCK_FACE_SEVEN_OCLOCK} Select the hour for the due time:"

    # Create the hours keyboard
    hours_keyboard = create_hours_keyboard()
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text=user_text,
        reply_markup=hours_keyboard
    )
    
    return INPUT_TODO_DUE_TIME


async def handle_calendar_month_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    # Get the callback data
    callback_data = query.data
    
    # Get the year and the month to build the calendar for the previous
    # or next month (depening which button has been clicked)
    year, month = [
        int(item) 
        for item in callback_data[1:].split("-")
    ]
    
    # Create the calendar
    inline_calendar = create_calendar(year=year, month=month)

    # Edit the message
    await query.edit_message_reply_markup(inline_calendar)

    # Return to the date selection step
    return SELECT_TODO_DUE_DATE


async def handle_calendar_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # This function simply ignores every callback query coming from any other button
    # in the inline keyboard, just to not have a callback query hanging around until 
    # the timeout
    
    # Get the callback query from the update and answer it
    query = update.callback_query
    await query.answer()

    return SELECT_TODO_DUE_DATE

# Step 3
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

    # If the user_tzinfo and UTC offset have been correctly extracted
    if user_tzinfo and utc_offset:

        # Convert the naive datetime in an aware datetime in the user tzinfo
        due_dt = due_dt.replace(tzinfo=user_tzinfo)

        # Get the current time in UTC format
        utc_current_time = datetime.now(tz=UTC)

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
        due_dt_utc = due_dt.astimezone(tz=UTC)

        # Overwrite the due_date value with full converted due datetime
        context.user_data["todo_data"]["due_date"] = due_dt_utc
        
        # Save the utc offset to the context user data dictionary
        context.user_data["todo_data"]["utc_offset"] = utc_offset

        user_text = f"{Emoji.ALARM_CLOCK} Would you like to be reminded of this to-do?"

        # Create the user choice keyboard
        user_choice_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Yes")],
                [KeyboardButton(text="No")],
            ],
            one_time_keyboard=True,
            is_persistent=False,
            resize_keyboard=True
        )

        await update.message.reply_text(
            text=user_text,
            reply_markup=user_choice_keyboard
        )

        return USER_CHOICE

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
        "or type them in the correct format <i>hh:mm</i>,\n"
        "where <i>hh</i> stands for hours (24-hours clock zero padded) between 00 (midnight) to 23, "
        "and <i>mm</i> stands for zero padded minutes between 00 to 59.\n"
        "(Example: 12:35):"
    )

    await update.message.reply_text(text=user_text)

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

# Step 4
async def user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the user choice
    user_choice: str = update.message.text.lower()

    if user_choice == "yes":

        # Create the list of reminder buttons
        reminder_times: list = [
            *[[KeyboardButton(text=button)] for button in [f"{i} minutes before" for i in range(5, 60, 5)]],
            *[
                [KeyboardButton(text=button)] 
                for button in 
                [f"{i} hour{"" if i == 1 else "s"} before" for i in range(1, 24)]
            ],
            *[
                [KeyboardButton(text=button)] 
                for button in 
                [f"{i} day{"" if i == 1 else "s"} before" for i in range(1, 8)]
            ]
        ]

        # Create the reminder times keyboard
        reminder_times_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            keyboard=reminder_times,
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=False
        )

        user_text = "Select a time for the reminder:"

        await update.message.reply_text(
            text=user_text,
            reply_markup=reminder_times_keyboard
        )

        # Next step
        return SELECT_REMINDER_TIME

    elif user_choice == "no":

        # Get the user Telegram id
        user_telegram_id: int = update.effective_user.id

        # If there is the todo_data dictionary
        if todo_data := context.user_data.pop("todo_data"):
                
            # If the todo is correctly saved
            if todo_id := save_todo(todo_data=todo_data):
                user_text = (
                    f"{Emoji.WHITE_HEAVY_CHECK_MARK} To-Do without reminder saved correctly.\n"
                    "You'll be reminded at the to-do specified time."
                )

                # Set the todo job name
                todo_job_name: str = f"todo_user_job_{todo_id.hex}"

                # Prepare the PTB job data (for the reminder at todo specified date)
                todo_job_data: dict = {
                    "callback": remind_user_job,
                    "name": todo_job_name,
                    "when": todo_data["due_date"],
                    "data": todo_id,
                    "chat_id": user_telegram_id,
                    "user_id": user_telegram_id
                }

                # Get the job queue
                job_queue = context.job_queue

                # Run the todo job
                job_queue.run_once(**todo_job_data)

            await update.message.reply_text(
                text=user_text,
                reply_markup=ReplyKeyboardRemove()
            )

    return ConversationHandler.END
    

async def handle_wrong_user_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_text = (
        f"{Emoji.WARNING_SIGN} Warning!\n"
        "The inserted choice is not valid.\n"
        "Please use the keyboard below to make a choice:"
    )

    await update.message.reply_text(text=user_text)

    return USER_CHOICE


# Step 5
async def select_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # Get the reminder time, and split it 0: type, 1:amount
    reminder_time = update.message.text.split(" ")

    # Extract the needed information
    # Here we are sure of the data we're dealing with
    # because of the strictness of the pattern in the handler,
    # so we can directly manage the data without doing additional checking
    reminder_time = {reminder_time[1]: int(reminder_time[0])}
    
    # Get the due date
    due_date: datetime = context.user_data["todo_data"]["due_date"]

    # Calculate the reminder datetime (in UTC), since due_date is in UTC
    reminder_datetime = due_date - timedelta(**reminder_time)    

    # If the reminder_time is less than the current time (everything in UTC),
    # ask the user to insert another reminder_time
    if reminder_datetime <= (datetime.now(UTC)):

        # Create the list of reminder buttons
        reminder_times: list = [
            *[[KeyboardButton(text=button)] for button in [f"{i} minutes before" for i in range(5, 60, 5)]],
            *[
                [KeyboardButton(text=button)] 
                for button in 
                [f"{i} hour{"" if i == 1 else "s"} before" for i in range(1, 24)]
            ],
            *[
                [KeyboardButton(text=button)] 
                for button in 
                [f"{i} day{"" if i == 1 else "s"} before" for i in range(1, 8)]
            ]
        ]

        # Create the reminder times keyboard
        reminder_times_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
            keyboard=reminder_times,
            one_time_keyboard=True,
            resize_keyboard=True,
            is_persistent=False
        )

        user_text = (
            f"{Emoji.WARNING_SIGN} Warning!\n"
            "The reminder time is before or equal the current time.\n"
            "Please select another reminder time:"
        )

        await update.message.reply_text(
            text=user_text,
            reply_markup=reminder_times_keyboard
        )

        return SELECT_REMINDER_TIME

    # If there is the todo_data dictionary
    if todo_data := context.user_data.pop("todo_data"):
            
        # If the todo is correctly saved
        if todo_id := save_todo(todo_data=todo_data):

            # Get the job queue
            job_queue = context.job_queue

            # Get the user Telegram id
            user_telegram_id: int = update.effective_user.id

            # Set the todo job name
            todo_job_name: str = f"todo_user_job_{todo_id.hex}"

            # If the todo job is not already in the jobs queue
            # (because the user choose a reminder)
            if not (job_queue.get_jobs_by_name(name=todo_job_name)):

                # Prepare the PTB job data (for the reminder at todo specified date)
                todo_job_data: dict = {
                    "callback": remind_user_job,
                    "name": todo_job_name,
                    "when": todo_data["due_date"],
                    "data": todo_id,
                    "chat_id": user_telegram_id,
                    "user_id": user_telegram_id
                }

                # Run the todo job
                job_queue.run_once(**todo_job_data)
            
            # Set the job name
            reminder_job_name: str = f"remind_user_job_{todo_id.hex}"

            # Prepare the PTB job data (for the reminder before the todo)
            reminder_job_data: dict = {
                "callback": remind_user_job,
                "name": reminder_job_name,
                "when": reminder_datetime,
                "data": todo_id,
                "chat_id": user_telegram_id,
                "user_id": user_telegram_id
            }
            
            # Schedule the job to run
            reminder_job = job_queue.run_once(**reminder_job_data)

            # If the job have been correctly added to the queue
            if reminder_job:

                # Prepare the reminder data
                reminder_data: dict = {
                    "name": reminder_job_name,
                    "todo_id": todo_id,
                    "remind_at": reminder_datetime
                }

                # Create the reminder
                if create_reminder(reminder_data=reminder_data):

                    user_text = (
                        f"{Emoji.WHITE_HEAVY_CHECK_MARK} To-Do with reminder saved correctly.\n"
                        "You'll be notified at the specified reminder time, and, if the to-do "
                        "will not be marked as 'done', you'll be reminded a second time at the "
                        "to-do specified time."
                    )

                    await update.message.reply_text(
                        text=user_text,
                        reply_markup=ReplyKeyboardRemove()
                    )

                    return ConversationHandler.END


async def get_user_utc_offset(user_telegram_id: int, local_naive_dt: datetime):

    # Transform the local dt (datetime) in a timestamp object
    local_dt_timestamp = local_naive_dt.timestamp()

    # Tranform the local timestamp in utc dt (datetime)
    utc_dt = datetime.fromtimestamp(local_dt_timestamp, tz=UTC)

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


def save_todo(todo_data: dict) -> UUID:

    # Save the todo to db
    return create_todo(todo_data=todo_data)


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
                filters=filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^\/cancel$"),
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
                callback=handle_calendar_month_update
            ),
            CallbackQueryHandler(callback=handle_calendar_unknown)
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
        ],
        USER_CHOICE: [
            MessageHandler(
                filters=filters.Regex(YES_NO_PATTERN_COMPILED) 
                & ~filters.Regex(r"^\/cancel$"),
                callback=user_choice
            ),
            MessageHandler(
                filters=filters.TEXT 
                & ~filters.Regex(r"^\/cancel$"),
                callback=handle_wrong_user_choice
            )
        ],
        SELECT_REMINDER_TIME: [
            MessageHandler(filters=filters.Regex(REMINDER_TIME_PATTERN_COMPILED) 
                & ~filters.Regex(r"^\/cancel$"),
                callback=select_reminder_time
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
