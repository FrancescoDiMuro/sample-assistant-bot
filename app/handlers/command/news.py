from __future__ import annotations
from constants.emoji import Emoji
from os import getenv
from serpapi import GoogleSearch
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatAction


# Entry point
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # Start the "get_local_news_job" to gather information
    # about local news
    context.job_queue.run_once(
        callback=get_local_news_job,
        when=1,
        chat_id=update.message.chat_id
    )
        

async def get_local_news_job(context: ContextTypes.DEFAULT_TYPE) -> None: 

    # Inform the user that the job is started
    await context.bot.send_chat_action(
        chat_id=context.job.chat_id,
        action=ChatAction.TYPING
    )
    
    # Extract the information from the "get_news" function
    local_news: dict = await get_local_news()

    # If data has been gathered correctly
    if local_news:

        user_text = f"{Emoji.NEWSPAPER} <b>Latest local news:</b>\n"

        # Format user info
        formatted_news: dict = await format_news(response_body=local_news)

        for i, local_news in enumerate(formatted_news):
            title, link = local_news
            user_text += f"{i + 1}. <a href='{link}'>{title}</a>\n"
    else:
        
        user_text = (
            f"{Emoji.CROSS_MARK} Unable to retrieve local news at the moment.\n"
            "Try again later."
        )

    # Send the message
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=user_text
    )


async def get_local_news() -> dict | None:

    # Get the tokens to make the API call
    SERPAPI_TOKEN: str = getenv("SERPAPI_TOKEN")
    GOOGLE_NEWS_LOCAL_TOPIC_TOKEN: str = getenv("GOOGLE_NEWS_LOCAL_TOPIC_TOKEN")

    # Set the query parameters
    query_parameters = {
        "engine": "google_news",
        "topic_token": GOOGLE_NEWS_LOCAL_TOPIC_TOKEN,
        "api_key": SERPAPI_TOKEN,
    }

    # Make the request
    request = GoogleSearch(query_parameters)
    
    # Get the response body in JSON format
    response_body = request.get_json()
    
    return response_body


async def format_news(response_body: dict, news_number: int = 10) -> list:

    # Dictionary to save the local news extraced
    # from the API call response
    local_news = []

    # Get the object from JSON
    news_results = response_body.get("news_results")

    # Counter for the total number of news that the user wants to see
    total_news_extracted = 0
    
    # Index for the array of news
    i = 0

    # Loop through the news
    while total_news_extracted < news_number:
        
        # Get the i-news
        news = news_results[i]

        # Get the desired information
        title = news.get("title")
        link = news.get("link")

        # If any of these information are missing,
        # then move to the next news
        if not (title or link):
            i += 1
            continue
        else:

            # Set the news
            extracted_news = [title, link]
        
            # Add the news to the list of news
            local_news.append(extracted_news)

            # Increment index and counter
            i += 1
            total_news_extracted += 1

    return local_news


def format_local_news_date(
    input_date: str
) -> str | None:

    # Get the desired information
    month, day, year = input_date.split("/")

    return f"{year}-{month}-{day}"


# Create the Command Handler
news_handler = CommandHandler(
    command="news",
    callback=news
)
