from constants.emoji import Emoji
from datetime import timedelta
from models.reminder.crud.delete import delete_reminder
from models.todo.crud.retrieve import retrieve_todo
from telegram.ext import ContextTypes


async def remind_user_job(context: ContextTypes.DEFAULT_TYPE):

    # Get the job instance
    job = context.job

    # Retrieve the todo
    if todo := retrieve_todo(todo_id=job.data):

        # Get the reminder (or None if not present)
        reminder = todo.reminder

        # Calculate the remind_at, adding the UTC offset based on the user's location
        if reminder:
            user_remind_at = reminder.remind_at + timedelta(seconds=todo.utc_offset)

        # Calculate the due_date, adding the UTC offset based on the user's location
        user_due_date = todo.due_date + timedelta(seconds=todo.utc_offset)

        user_text = (
            f"{Emoji.ALARM_CLOCK} Reminder (due {user_due_date:%Y-%m-%d %H:%M})\n"
            f"{f"(first reminder set at {user_remind_at:%Y-%m-%d %H:%M})\n" if reminder else ""}"
            "To-do details:\n"
            f"<i>{todo.details}</i>\n\n"
            f"<i>React with a {Emoji.THUMBS_UP_SIGN} to the message to mark the to-do as completed.</i>"
        )

        # Get the message_id of the message to send to the user
        message_id: int = (
            await context.bot.send_message(
                chat_id=job.chat_id,
                text=user_text
            )
        ).id

        # Get the user Telegram id from the job data
        user_telegram_id = job.user_id

        # Here we are using the bot_data dictionary instead of
        # the user_data one, since it's not available.
        # So, in order to keep all the data split for each user,
        # we have to created a dictionary in the bot_data one
        # for every user, using its telegram id as a key for
        # another inner dictionary, which contains other information.
        # This if avoids another declaration for the inner dictionary
        # if it already exists
        if not context.bot_data.get(user_telegram_id):
            context.bot_data[user_telegram_id] = {}

        # This if avoids another declaration for the "pending_todos"
        # inner dictionary
        if not context.bot_data.get(user_telegram_id).get("pending_todos"):
            context.bot_data[user_telegram_id]["pending_todos"] = {}

        # In any case, assign the todo id to the dictionary "hierarchy"
        context.bot_data[user_telegram_id]["pending_todos"][message_id] = todo.id

        # Delete the reminder
        if reminder:
            delete_reminder(reminder_id=reminder.id)
    