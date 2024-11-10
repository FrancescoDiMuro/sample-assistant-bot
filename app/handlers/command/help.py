from __future__ import annotations
from constants.emoji import Emoji
from constants.bot_commands import BOT_COMMANDS
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # If the user is asking help for a specific command
    if args := context.args:

        # Append the "/" before the command name
        command = f"/{args[0]}"

        # Get the command description from the dictionary, or the default message
        user_text = BOT_COMMANDS.get(command) or \
                    f"I don't know what you're talking about {Emoji.PERSON_SHRUGGING}"
        
    else:

        user_text = (
            f"{Emoji.HEAVY_PLUS_SIGN} This command shows you the help for the available bot commands.\n"
            "If you want the help for a specific command, use the syntax:\n"
            "<i>/help command</i>, where <i>command</i> is an available bot command."
        )

    await update.message.reply_text(
        text=user_text, 
        reply_to_message_id=update.message.id
    )
        

# Create the Command Handler
help_handler = CommandHandler(
    command="help",
    callback=help
)
