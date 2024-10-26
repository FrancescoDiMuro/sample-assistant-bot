from constants.emoji import Emoji
from datetime import timedelta
from models.reminder.crud.delete import delete_reminder
from models.todo.crud.retrieve import retrieve_todo
from telegram.ext import ContextTypes


async def notify_user_job(context: ContextTypes.DEFAULT_TYPE):

    # Get the job instance
    job = context.job

    # Retrieve the todo
    if todo := retrieve_todo(todo_id=job.data):

        # Calculate the due_date, adding the UTC offset based on the user's location
        user_due_date = todo.due_date + timedelta(seconds=todo.utc_offset)

        user_text = (
            f"{Emoji.ALARM_CLOCK} Reminder (due {user_due_date}):\n"
            f"{todo.details}"
        )

        await context.bot.send_message(
            chat_id=job.chat_id,
            text=user_text
        )

        # Delete the reminder
        delete_reminder(reminder_id=todo.reminder.id)