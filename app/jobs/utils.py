from datetime import UTC, datetime
from jobs.remind_user_job import remind_user_job
from models.reminder.crud.retrieve import retrieve_reminders
from models.todo.crud.retrieve import retrieve_todos
from re import Pattern, compile
from telegram.ext import Application, ContextTypes
from uuid import UUID


async def get_jobs_by_name_custom(context: ContextTypes.DEFAULT_TYPE, name: str | Pattern) -> tuple:

    jobs = context.job_queue.jobs()

    pattern = compile(pattern=name)

    return tuple(job for job in jobs if pattern.search(string=job.name))


async def reload_jobs_post_init(application: Application):
    
    # Reload the reminder jobs
    await reload_reminder_jobs(application=application)
    
    # Reload the todo jobs
    await reload_todo_jobs(application=application)


async def reload_reminder_jobs(application: Application):

    # Get the list of reminders
    reminders = retrieve_reminders()

    # If there's at least a reminder
    if reminders:

        # Get the job queue
        job_queue = application.job_queue

        # Get the actual timestamp (in UTC)
        now_utc = datetime.now(UTC)

        for reminder in reminders:

            # Get the remind_at, and add the UTC timezone info
            remind_at_utc: datetime = reminder.remind_at.replace(tzinfo=UTC)
            
            # If the reminder didn't expire
            # TODO: inform the user that it had a reminder (?)
            if remind_at_utc > now_utc:

                # Get the todo id
                todo_id: UUID = reminder.todo_id

                # Set the job name
                reminder_job_name: str = f"remind_user_job_{todo_id.hex}"

                # Get the user_telegram_id
                user_telegram_id: int = reminder.todo.user.telegram_id

                # Prepare the PTB job data (for the reminder before the todo)
                reminder_job_data: dict = {
                    "callback": remind_user_job,
                    "name": reminder_job_name,
                    "when": remind_at_utc,
                    "data": todo_id,
                    "chat_id": user_telegram_id,
                    "user_id": user_telegram_id
                }

                # Schedule the job to run
                job_queue.run_once(**reminder_job_data)


async def reload_todo_jobs(application: Application):

    # Get the list of todos
    todos = retrieve_todos()

    # If there's at least a todo
    if todos:

        # Get the job queue
        job_queue = application.job_queue

        # Get the actual timestamp (in UTC)
        now_utc = datetime.now(UTC)

        for todo in todos:

            # Get the due_date, and add the UTC timezone info
            due_date_utc: datetime = todo.due_date.replace(tzinfo=UTC)
            
            # If the todo didn't expire
            # TODO: inform the user that it had a reminder (?)
            if due_date_utc > now_utc:

                # Get the todo id
                todo_id: UUID = todo.id

                # Set the job name
                todo_job_name: str = f"todo_user_job_{todo_id.hex}"

                # Get the user_telegram_id
                user_telegram_id: int = todo.user.telegram_id

                # Prepare the PTB job data (for the reminder before the todo)
                todo_job_data: dict = {
                    "callback": remind_user_job,
                    "name": todo_job_name,
                    "when": due_date_utc,
                    "data": todo_id,
                    "chat_id": user_telegram_id,
                    "user_id": user_telegram_id
                }

                # Schedule the job to run
                job_queue.run_once(**todo_job_data)
