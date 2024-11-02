from datetime import UTC, datetime, timedelta
from constants.emoji import Emoji
from models.todo.crud.retrieve import retrieve_todo
from models.todo.crud.update import update_todo
from telegram import Update
from telegram.ext import (
    ApplicationHandlerStop, 
    ContextTypes, 
    MessageReactionHandler
)


async def mark_todo_as_done(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the various information for further processing
    message_reaction_updated = update.message_reaction
    message_id = message_reaction_updated.message_id
    user_telegram_id = message_reaction_updated.user.id

    # Guards
    if not (user_data := context.bot_data.get(user_telegram_id)):
        raise ApplicationHandlerStop()
    if not (pending_todos := user_data.get("pending_todos")):
        raise ApplicationHandlerStop()
    if message_id not in pending_todos.keys(): 
        raise ApplicationHandlerStop()

    # If there's a todo_id assigned to the specified message
    if todo_id := pending_todos.get(message_id):
        
        # If there is a todo with the specified id
        if todo := retrieve_todo(todo_id=todo_id):

            # If there is a new_reaction for the current message_reaction_updated
            if reaction := message_reaction_updated.new_reaction:

                # Get the 0-th reaction's emoji
                emoji = reaction[0].emoji
            
                # If the to-do is not in the state of "done",
                # and the user's reaction to the todo-reminder is a "thumbs-up"
                if (not todo.done) and emoji == Emoji.THUMBS_UP_SIGN:

                    # Prepare the data to update
                    todo_data: dict = {
                        "done": True
                    }

                    # Update the todo
                    if update_todo(
                        todo_id=todo_id,
                        todo_data=todo_data
                    ):
                        
                        # Get the user UTC offset
                        user_utc_offset = todo.utc_offset

                        # Calculate the completed time for the current to-do
                        todo_completed_time = datetime.now(UTC) + timedelta(seconds=user_utc_offset)
                        
                        # Delete the pending todo
                        context.bot_data[user_telegram_id]["pending_todos"].pop(message_id)

                        # Set the job name
                        todo_job_name: str = f"todo_user_job_{todo_id.hex}"

                        # Delete the other job
                        jobs = context.job_queue.get_jobs_by_name(name=todo_job_name)

                        # If the job has been found
                        if(jobs):

                            # Get the job
                            todo_job = jobs[0]

                            # Disable and delete the job
                            todo_job.enabled = False
                            todo_job.schedule_removal()

                        # User text
                        user_text = (
                            f"To-Do checked as completed on "
                            f"{todo_completed_time:%Y-%m-%d %H:%M}"
                        )
                        
                        await context.bot.send_message(
                            chat_id=user_telegram_id,
                            text=user_text,
                            reply_to_message_id=message_id
                        )


# Create the handler
message_reaction_handler = MessageReactionHandler(callback=mark_todo_as_done)
    