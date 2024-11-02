from constants.emoji import Emoji
from datetime import datetime, timedelta
from models.todo.crud.retrieve import retrieve_todos
from models.user.crud.retrieve import retrieve_user
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def create_todos_keyboard(user_telegram_id: int) -> InlineKeyboardMarkup | None:

    # Retrieve the user
    if user := retrieve_user(user_telegram_id=user_telegram_id):

        # Get the uncompleted list of user's todos
        if user_uncompleted_todos := retrieve_todos(user_id=user.id, is_done=False):

            # Prepare the keyboard for the todos list
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

                # Set the todo user due date
                todo_user_due_date: datetime = \
                    f"{todo.due_date + timedelta(seconds=todo.utc_offset):%Y-%m-%d %H:%M}"
                
                # Add the todo information to the keyboard
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
                    
            # Return the keyboard
            return InlineKeyboardMarkup(inline_keyboard=keyboard)
        
    return None
