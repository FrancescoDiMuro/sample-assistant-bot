from constants.emoji import Emoji
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Get user first name
    user_first_name: str = update.effective_user.first_name
    
    # User text
    user_text: str = (
        f"Hello {user_first_name} {Emoji.WAVING_HAND_SIGN}\n"
        f"I'm your personal assistant bot {Emoji.ROBOT}\n"
        "Everytime you're going to write 'Hey Bot' in this chat,\n"
        "I'm going to be listening to you, and you can ask me to:\n"
        f"- tell you the weather {Emoji.BLACK_SUN_WITH_RAYS}\n"
        f"- remind you to do a task {Emoji.SPEECH_BALLOON}\n"
        f"- tell you the news {Emoji.NEWSPAPER}\n"
        "For example: <i>Hey Bot, how's the weather like?</i>\n"
        f"In case I don't see ya, good afternoon, good evening and good night! {Emoji.GRINNING_FACE_WITH_SMILING_EYES}"
    )

    await update.message.reply_text(text=user_text)