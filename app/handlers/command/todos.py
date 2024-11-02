from __future__ import annotations
from constants.emoji import Emoji
from handlers.callback.keyboards.todos import create_todos_keyboard
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, CommandHandler


async def todos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Send chat action to inform the user that there's a process ongoing
    context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    # Create the todos inline keyboard
    todos_inline_keyboard = await create_todos_keyboard(user_telegram_id=update.effective_user.id)

    # If the keyboard has been correctly created (and so, there is at least a todo)
    if todos_inline_keyboard:

        user_text = f"{Emoji.OPEN_BOOK} To-dos list:"

        await update.message.reply_text(
            text=user_text,
            reply_markup=todos_inline_keyboard
        )

    else:

        user_text = f"{Emoji.PERSON_SHRUGGING} There are no to-dos!"

        await update.message.reply_text(text=user_text)


# Create the handler
todos_handler = CommandHandler(
    command="todos",
    callback=todos
)
        