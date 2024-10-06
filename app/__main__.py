from dotenv import load_dotenv
from handlers.command.start import start
from os import getenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler


# DEBUG
print(f".env loaded: {load_dotenv()}")

# If the bot token has been found and it is valorized
if BOT_TOKEN := getenv("BOT_TOKEN"):
    
    # Create the app
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .build()
    
    start_handler = CommandHandler(command="start", callback=start)
    app.add_handler(handler=start_handler)
    
# Run bot polling, allowing all the updates to be processed
app.run_polling(allowed_updates=Update.ALL_TYPES)
