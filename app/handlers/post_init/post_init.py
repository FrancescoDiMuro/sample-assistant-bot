from constants.bot_commands import BOT_COMMANDS
from jobs.utils import reload_jobs_post_init
from telegram import BotCommand
from telegram.ext import Application


async def post_init(application: Application) -> None:

    # Initialize an empty list of bot commands
    bot_commands: list = []

    # Set bot commands (on the left side of the input text field)
    for command, description in BOT_COMMANDS.items():
        
        # Append the command to the list of bot commands
        bot_commands.append(BotCommand(command=command, description=description))

    # Set bot commands
    await application.bot.set_my_commands(bot_commands)

    # Reload jobs from db
    await reload_jobs_post_init(application=application)

    return None