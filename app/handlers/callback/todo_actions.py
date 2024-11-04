from constants.emoji import Emoji
from datetime import UTC, datetime, timedelta
from handlers.callback.keyboards.todos import create_todos_keyboard
from jobs.utils import get_jobs_by_name_custom
from models.reminder.crud.delete import delete_reminder
from models.todo.crud.retrieve import retrieve_todo
from models.todo.crud.delete import delete_todo
from models.todo.crud.update import update_todo
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from uuid import UUID


async def handle_todo_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the callback query
    query = update.callback_query

    # Get the user Telegram id
    user_telegram_id: int = query.from_user.id

    # Get the various information from the callback data
    todo_action, todo_info = query.data.split(":")
    todo_action = todo_action.replace("todo_", "")
    
    # Match the action
    match todo_action:

        case "done":

            # Answer the query
            await query.answer()
            
            # Transform the todo_id as a UUID (because it was a string)
            todo_id = todo_id = UUID(hex=todo_info, version=4)
            
            # Prepare the data to update
            todo_data: dict = {"done": True}

            # Mark the todo as completed
            if update_todo(todo_id=todo_id, todo_data=todo_data):

                # Get the todo
                if todo := retrieve_todo(todo_id=todo_id):

                    # If the reminder is still present in the db because it hasn't been triggered yet
                    if reminder := todo.reminder:

                        # Delete the reminder
                        delete_reminder(reminder_id=reminder.id)

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
                    for job in await get_jobs_by_name_custom(context=context, name=f".*{todo_id.hex}"):
                        job.enabled = False
                        job.schedule_removal()

                    # User text
                    user_text = (
                        f"{Emoji.WHITE_HEAVY_CHECK_MARK} To-Do ({todo.details}) checked as completed on "
                        f"{todo_completed_time:%Y-%m-%d %H:%M}"
                    )
                    
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=user_text
                    )

        case "delete":
            
            # Here we need to delete:
            # - the to-do (and associated reminder, if present)
            # - the pending to-do (used to be completed with a message reaction)

            # Transform the todo_id as a UUID (because it was a string)
            todo_id = todo_id = UUID(hex=todo_info, version=4)

            # Get the todo
            if todo := retrieve_todo(todo_id=todo_id):

                # Answer the query
                await query.answer()

                # Get the user UTC offset
                user_utc_offset = todo.utc_offset

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
                for job in await get_jobs_by_name_custom(context=context, name=f".*{todo_id.hex}"):
                    job.enabled = False
                    job.schedule_removal()

                # Set the deletion time
                todo_deletion_time = datetime.now(UTC) + timedelta(seconds=user_utc_offset)

                # User text
                user_text = (
                    f"{Emoji.CROSS_MARK} To-Do ({todo.details}) deleted on "
                    f"{todo_deletion_time:%Y-%m-%d %H:%M}"
                )

                # Delete the to-do
                delete_todo(todo_id=todo_id)

                await context.bot.send_message(
                    chat_id=update.effective_user.id,
                    text=user_text
                )

            else:
                await query.answer("You've already deleted this Todo!")

                await query.delete_message()

        case "go_back":

            # Answer the query
            await query.answer()
                    
            # Create the todos inline keyboard
            todos_inline_keyboard = await create_todos_keyboard(user_telegram_id=user_telegram_id)

            # If the keyboard has been correctly created (and so, there is at least a todo)
            if todos_inline_keyboard:

                user_text = f"{Emoji.OPEN_BOOK} To-dos list:"

                await query.edit_message_text(
                    text=user_text,
                    reply_markup=todos_inline_keyboard
                )

            else:

                user_text = f"{Emoji.PERSON_SHRUGGING} There are no to-dos!"

                await query.edit_message_text(text=user_text)


# Create the handler
todo_actions_handler = CallbackQueryHandler(
    pattern=r"^todo_(?:done|delete|go_back):.*$",
    callback=handle_todo_actions
)

