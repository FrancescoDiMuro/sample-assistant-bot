from __future__ import annotations
from constants.emoji import Emoji
from models.todo.crud.retrieve import retrieve_todos
from models.user.crud.retrieve import retrieve_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatAction


async def todos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # Retrieve the user
    if user := retrieve_user(user_telegram_id=update.effective_user.id):

        # Get the uncompleted list of user's todos
        if user_uncompleted_todos := retrieve_todos(is_done=False):

            # Create the list of todos (details) for the inline keyboard
            keyboard: list = [
                [
                    InlineKeyboardButton(
                        text=todo.details, 
                        callback_data=todo.id.hex
                    )
                ]
                for todo in user_uncompleted_todos
            ]

            # Create the keyboard
            todos_inline_keyboard = InlineKeyboardMarkup(
                inline_keyboard=keyboard,
            )

            user_text = (
                f"{Emoji.OPEN_BOOK} To-dos list:"
            )

            await update.message.reply_text(
                text=user_text,
                reply_markup=todos_inline_keyboard
            )


todos_handler = CommandHandler(
    command="todos",
    callback=todos
)
        