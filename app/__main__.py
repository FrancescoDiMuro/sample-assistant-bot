from dotenv import load_dotenv
from handlers.command.weather import weather_handler
from handlers.conversation.start import start_handler
from handlers.conversation.set_location import set_location_handler
from handlers.post_init.post_init import post_init
from os import getenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults


# Load environment variables from local .env
load_dotenv()

# If the bot token has been found and it is valorized
if BOT_TOKEN := getenv("BOT_TOKEN"):

    # Add default values to the bot settings
    defaults = Defaults(parse_mode=ParseMode.HTML)
    
    # Create the app
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .post_init(post_init=post_init) \
        .defaults(defaults=defaults) \
        .build()
    
    # ---------- /start (conversation) ----------
    app.add_handler(handler=start_handler)

    # ---------- /setlocation (conversation) ----------
    app.add_handler(handler=set_location_handler)

    # ---------- /weather (command) ---------- 
    app.add_handler(handler=weather_handler)
    
    # Run bot polling, allowing all the updates to be processed
    app.run_polling(allowed_updates=Update.ALL_TYPES)
