from uuid import UUID
from constants.emoji import Emoji
from datetime import datetime, timedelta
from models.todo.crud.retrieve import retrieve_todo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes


async def open_todo_details(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get the callback query and answer it
    query = update.callback_query
    await query.answer()

    # Get the todo_id and transform it as a UUID (because it was a string)
    todo_id = UUID(hex=query.data.split(":")[1], version=4)

    # Get the todo
    if todo := retrieve_todo(todo_id=todo_id):

        # Transfrom the due_date in user_due_date, adding the UTC offset (to user local time)
        user_due_date: datetime = todo.due_date + timedelta(seconds=todo.utc_offset)

        user_text = (
            f"<b>{Emoji.MEMO} Todo:</b>\n"
            f"<b>Details</b>:\n" 
            f"<code>{todo.details}</code>\n"
            f"<b>Due to:</b> {user_due_date:%Y-%m-%d %H:%M}\n"
        )

        # If there's a reminder, then add more information
        if todo.reminder:
            user_reminder_date: datetime = todo.reminder.remind_at + timedelta(seconds=todo.utc_offset)
            user_text += f"<b>Reminder:</b> {user_reminder_date:%Y-%m-%d %H:%M}"

        # Create the keyboard for the todo
        keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{Emoji.WHITE_HEAVY_CHECK_MARK}",
                    callback_data=f"todo_done:{todo_id}"
                ),
                    InlineKeyboardButton(
                    text=f"{Emoji.CROSS_MARK}",
                    callback_data=f"todo_delete:{todo_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{Emoji.LEFTWARDS_BLACK_ARROW} Todos",
                    callback_data=f"todo_go_back:"
                )
            ]
        ]

        # Create the inline keyboard
        inline_keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await query.edit_message_text(
            text=user_text,
            reply_markup=inline_keyboard
        )


# Create the handler
todo_details_handler = CallbackQueryHandler(
    pattern=r"^todo_details:.*$",
    callback=open_todo_details
)
