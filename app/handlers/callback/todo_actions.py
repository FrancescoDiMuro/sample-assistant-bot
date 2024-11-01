from uuid import UUID
from constants.emoji import Emoji
from datetime import UTC, datetime, timedelta
from models.todo.crud.retrieve import retrieve_todo
from models.todo.crud.update import update_todo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes


async def handle_todo_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the callback query and answer it
    query = update.callback_query
    await query.answer()

    # Get the user Telegram id
    user_telegram_id: int = query.from_user.id

    # Get the various information from the callback data
    todo_action, todo_id = query.data.split(":")
    todo_action = todo_action.replace("todo_", "")
    
    # Transform the todo_id as a UUID (because it was a string)
    todo_id = UUID(hex=todo_id, version=4)
    
    # Match the action
    match todo_action:

        case "done":
            
            # Prepare the data to update
            todo_data: dict = {"done": True}

            # Mark the todo as completed
            if update_todo(todo_id=todo_id, todo_data=todo_data):

                # Get the todo
                if todo := retrieve_todo(todo_id=todo_id):

                    # Get the user UTC offset
                    user_utc_offset = todo.utc_offset

                    # Calculate the completed time for the current to-do
                    todo_completed_time = datetime.now(UTC) + timedelta(seconds=user_utc_offset)
                
                    # Delete the pending todo(s)
                    if user_data := context.bot_data.get(user_telegram_id):
                    
                        # Since we can't delete keys in the same dictionary we're iterating through,
                        # we need to make a copy of it, so we can do whatever we want on the original one
                        pending_todos = user_data["pending_todos"].copy()
                        
                        # If there's a pending_todo, delete it
                        # (just after the reminder remind_at and/or the todo due time is passed)
                        for k, v in pending_todos.items():
                            if v == todo_id:
                                del context.bot_data[user_telegram_id]["pending_todos"][k]

                    # NOTE: here I'm using a custom version of "get_jobs_by_name" function,
                    # that supports searching the jobs through regular expressions
                    # For each job that has the todo_id, disable it and remove it
                    for job in context.job_queue.get_jobs_by_name(name=todo_id.hex, use_regex=True):
                        job.enabled = False
                        job.schedule_removal()

                    # User text
                    user_text = (
                        f"To-Do checked as completed on "
                        f"{todo_completed_time:%Y-%m-%d %H:%M}"
                    )
                    
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=user_text
                    )

        case "delete":
            pass

        case "go_back":
            pass


todo_actions_handler = CallbackQueryHandler(
    pattern=r"^todo_(?:done|delete|go_back):.+$",
    callback=handle_todo_actions
)

