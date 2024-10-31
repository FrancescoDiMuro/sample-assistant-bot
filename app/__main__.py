from dotenv import load_dotenv
from handlers.command.news import news_handler
from handlers.command.todos import todos_handler
from handlers.command.weather import weather_handler
from handlers.conversation.start import start_handler
from handlers.conversation.set_location import set_location_handler
from handlers.conversation.todo import create_todo_handler
from handlers.message_reaction.todo import message_reaction_handler
from handlers.post_init.post_init import post_init
from os import getenv
from telegram import LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults


# Load environment variables from local .env
load_dotenv()

# If the bot token has been found and it is valorized
if BOT_TOKEN := getenv("BOT_TOKEN"):

    # Add default values to the bot settings
    defaults = Defaults(
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True))
    
    # Create the app
    app = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .post_init(post_init=post_init) \
        .defaults(defaults=defaults) \
        .build()
    
    
    # ---------- (message reaction) ----------
    app.add_handler(handler=message_reaction_handler)
    
    # ---------- /news (command) ----------
    app.add_handler(handler=news_handler)
    
    # ---------- /setlocation (conversation) ----------
    app.add_handler(handler=set_location_handler)
    
    # ---------- /start (conversation) ----------
    app.add_handler(handler=start_handler)

    # ---------- /todo (conversation) ----------
    app.add_handler(handler=create_todo_handler)

    # ---------- /todos (command) ----------
    app.add_handler(handler=todos_handler)

    # ---------- /weather (command) ----------
    app.add_handler(handler=weather_handler)
    
    # Run bot polling, allowing all the updates to be processed
    app.run_polling(allowed_updates=Update.ALL_TYPES)
