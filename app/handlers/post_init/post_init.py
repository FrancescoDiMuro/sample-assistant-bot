from constants.bot_commands import BOT_COMMANDS
from telegram import BotCommand
from telegram.ext import Application


async def post_init(application: Application) -> None:

    # Initialize an empty list of bot commands
    bot_commands: list = []

    # Set bot commands (on the left side of the input text field)
    for command in BOT_COMMANDS:
        
        # Append the command to the list of bot commands
        bot_commands.append(BotCommand(**command))

    await application.bot.set_my_commands(bot_commands)

    return None