from __future__ import annotations
from bs4 import BeautifulSoup, ResultSet
from constants.emoji import Emoji
from difflib import SequenceMatcher
from geopy import Nominatim
from models.user.crud.retrieve import retrieve_user
from requests.compat import quote
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, CommandHandler
from uuid import uuid4
import requests


# Entry point
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    # Start the "get_local_news_job" to gather information
    # about local news
    context.job_queue.run_once(
        callback=get_local_news_job,
        when=1,
        user_id=update.effective_user.id,
        chat_id=update.message.chat_id
    )
        

async def get_local_news_job(context: ContextTypes.DEFAULT_TYPE) -> None:

    # Inform the user that the job is started
    await context.bot.send_chat_action(
        chat_id=context.job.chat_id,
        action=ChatAction.TYPING
    )

    # Check if the user exists
    if not (user := retrieve_user(user_telegram_id=context.job.user_id)):

        user_text = (
            f"{Emoji.CROSS_MARK} It seems that you didn't sign-up.\n"
            "In order to use this bot, you must sign-up and set a location."
        )

        # Send the message
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=user_text
        )

        return None

    # If the user doesn't have a location
    if not (user_location := user.location):

        user_text = (
            f"{Emoji.CROSS_MARK} It seems that you didn't set a location.\n"
            "In order to use this command, you must set a location."
        )

        # Send the message
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=user_text
        )

        return None
    
    # Get the user detailed location
    user_detailed_location = get_user_detailed_location(
        latitude=user_location.latitude,
        longitude=user_location.longitude
    )
    
    # Compose the local news URL for the user
    url = compose_user_local_news_url(location=user_detailed_location)
    
    # Extract the information from the "get_local_news" function
    news_list: dict = await get_local_news(url=url)

    # If data has been gathered correctly
    if news_list:

        user_text = f"{Emoji.NEWSPAPER} <b>Latest local news:</b>\n"

        # Please note: the news_datetime is not used
        for i, news in enumerate(news_list):
            title, link, news_datetime = news
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


async def get_local_news(url: str):

    # Get the news content (to scrape)
    news_content = await get_news_content(url=url)
    
    # Get the news from content (scraped)
    all_news = get_news_from_content(content=news_content)
    
    # Filter news (remove similiar news),
    # sorted by post time
    return filter_news(news_list=all_news)


async def get_news_content(url: str) -> bytes:

    # Get the Google News results
    response = requests.get(url=url)

    return response.content or None


def get_news_from_content(content: bytes) -> list:

    # Define the source to append to the links
    source: str = "https://news.google.com"
    
    # Initialize an empty list of news
    news_list: list = []
    
    # Create the scraper
    soup = BeautifulSoup(markup=content, features="html.parser")

    # Get all the c-wiz tags with the specified class class
    c_wizs: ResultSet = soup.find_all(name="c-wiz", class_="XBspb")

    # If at least of tag has been found
    if c_wizs:

        # For each tag found
        for c_wiz in c_wizs:
            
            # Extract the anchor tag with the specified class in the c-wiz
            a = c_wiz.find(name="a", class_="JtKRv")
            
            # Get the time tag with the specified class in the c-wiz
            time = c_wiz.find(name="time", class_="hvbAAd")

            # Extract the text, href and datetime of the tags
            news_title: str = a.text
            news_link: str = f"{source}/{a['href'][2:]}"
            news_datetime: str = time['datetime']
            
            # Set the row of news with the various information
            news = [news_title, news_link, news_datetime]

            # Append the news row to the news list
            news_list.append(news)

    return news_list


def filter_news(news_list: list, count: int = 10) -> list:
        
    # Initialize a list of filtered news
    filtered_news: list = []

    # Threshold to avoid similiar results
    threshold: float = 0.2

    for news in news_list:
        if not any(is_similar(text1=news, text2=filtered, threshold=threshold) for filtered in filtered_news):
            filtered_news.append(news)
    
    # Sort the filtered news by post datetime, in descending order
    filtered_news = sorted(filtered_news, key=lambda row: row[2], reverse=True)
    
    # Return the specified amount of news
    return filtered_news[:count]


def is_similar(text1, text2, threshold):
    return SequenceMatcher(
        isjunk=None,
        a=text1,
        b=text2,
        autojunk=True
   ).ratio() > threshold


def get_user_detailed_location(latitude: float, longitude: float) -> dict:

    # Set the coordinates
    coordinates = f"{latitude},{longitude}"
    
    # Instatiate the geolocator with a random UUID as User-Agent
    geolocator = Nominatim(user_agent=uuid4().hex)

    # Get the location
    location = geolocator.reverse(query=coordinates, language="en")

    return location.raw['address'] if location else None


def compose_user_local_news_url(location: dict):

    # Get the city (quoted), safe for HTML
    city: str = quote(location['city'])
    
    # Get the country (quoted), safe for HTML
    country: str = quote(location['country'])
    
    # Host language (for now always "en")
    host_language = "en"

    # Compose the URL
    url = f"https://news.google.com/search?q={city}%2C%20{country}&hl={host_language}"

    return url


# Create the Command Handler
news_handler = CommandHandler(
    command="news",
    callback=news
)
