from __future__ import annotations
from datetime import datetime, timedelta
from constants.emoji import Emoji
from models.todo.crud.retrieve import retrieve_todos
from models.user.crud.retrieve import retrieve_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, CommandHandler


async def todos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Send chat action to inform the user that there's a process ongoing
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # Retrieve the user
    if user := retrieve_user(user_telegram_id=update.effective_user.id):

        # Get the uncompleted list of user's todos
        if user_uncompleted_todos := retrieve_todos(user_id=user.id, is_done=False):

            keyboard: list = [
                [
                    InlineKeyboardButton(
                        text=f"{Emoji.CALENDAR} Due to", 
                        callback_data="placeholder"
                    ),
                    InlineKeyboardButton(
                        text=f"{Emoji.OPEN_BOOK} Details", 
                        callback_data="placeholder"
                    ),
                ]
            ]

            # Create the list of todos (details) for the inline keyboard
            for todo in user_uncompleted_todos:

                todo_user_due_date: datetime = \
                    f"{todo.due_date + timedelta(seconds=todo.utc_offset):%Y-%m-%d %H:%M}"
                
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            text=todo_user_due_date, 
                            callback_data="placeholder"
                        ),
                        InlineKeyboardButton(
                            text=todo.details, 
                            callback_data=f"todo_details:{todo.id.hex}"
                        )
                    ]
                )
                    
            # Create the keyboard
            todos_inline_keyboard = InlineKeyboardMarkup(
                inline_keyboard=keyboard,
            )

            user_text = (
                f"{Emoji.OPEN_BOOK} To-dos list:"
            )

        else:

            user_text = f"{Emoji.PERSON_SHRUGGING} There are no to-dos!"

        await update.message.reply_text(
                text=user_text,
                reply_markup=todos_inline_keyboard
        )

todos_handler = CommandHandler(
    command="todos",
    callback=todos
)
        