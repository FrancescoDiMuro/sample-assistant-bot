from __future__ import annotations
from constants.emoji import Emoji
from constants.wmo_codes import WMO_CODES
from datetime import datetime
from models.user.crud.retrieve import retrieve_user
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

import requests

# Entry point
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Check if the user exists
    if user := retrieve_user(user_telegram_id=update.effective_user.id):
        
        # Check if the user has a location
        if location := user.location:

            # Get the location
            location = location[0]

            # Get the location data for further processing
            location_data: dict = {
                "latitude": location.latitude,
                "longitude": location.longitude
            }

            # Start the "get_weather_info_job" to gather information
            # about weather at the user's location
            context.job_queue.run_once(
                callback=get_weather_info_job,
                when=1,
                data=location_data,
                chat_id=update.message.chat_id
            )
            

async def get_weather_info_job(context: ContextTypes.DEFAULT_TYPE) -> None: 

    # Get the location data from the job data
    location_data: dict = context.job.data

    # Extract the information from the "get_weather_info" function
    weather_info: dict = await get_weather_info(location_data=location_data)

    # If data has been gathered correctly
    if weather_info:

        # Format user info
        formatted_weather_info: dict = await format_weather_info(response_body=weather_info)

        # User text
        user_text = "\n".join(
            [f"{k}: {v}" for k,v in formatted_weather_info.items()]
        )

    else:
        
        user_text = (
            f"{Emoji.CROSS_MARK} Unable to retrieve weather information at the moment.\n"
            "Try again later."
        )    

    # Send the message
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=user_text
    )


async def get_weather_info(location_data: dict) -> dict | None:

    # Base URL for the Open-Meteo APIs
    base_url: str = "https://api.open-meteo.com/v1"
    
    # Endpoint to call
    endpoint: str = "forecast"
    
    # List of variables with the desired display name
    # and the actual name
    variables: list = [
        "weather_code",
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "is_day",
        "cloud_cover",
        "wind_speed_10m"
    ]

    # Format query parameters
    query_parameters: dict = {
        "latitude": location_data.get("latitude"),
        "longitude": location_data.get("longitude"),
        "current": ",".join([variable for variable in variables])
    }

    # Compose the URL
    url = f"{base_url}/{endpoint}"

    # Call the APIs
    response = requests.get(url=url, params=query_parameters)

    # If the response is ok (200)
    if response.ok:

        # Get the response body in JSON format
        response_body: dict = response.json()

        return response_body
    
    return None


async def format_weather_info(response_body: dict) -> dict:
    
    # List of variables with the desired display name
    # and the actual name
    variables: list = [
        {
            "display_name": "Summary",
            "variable_name": "weather_code",
            "emoji": Emoji.OPEN_BOOK,
        },
        {
            "display_name": "Temperature",
            "variable_name": "temperature_2m",
            "emoji": Emoji.THERMOMETER
        },
        {
            "display_name": "Relative Humidity",
            "variable_name": "relative_humidity_2m",
            "emoji": Emoji.SPLASHING_SWEAT_SYMBOL
        },
        {
            "display_name": "Feels like",
            "variable_name": "apparent_temperature",
            "emoji": Emoji.FACE_MASSAGE
        },
        {
            "display_name": "Day/Night",
            "variable_name": "is_day",
            "emoji": "",
        },
        {
            "display_name": "Cloud Cover",
            "variable_name": "cloud_cover",
            "emoji": Emoji.CLOUD
        },
        {
            "display_name": "Wind Speed",
            "variable_name": "wind_speed_10m",
            "emoji": Emoji.WIND_FACE
        }
    ]

    # Dictionary to save the weather info extraced
    # from the API call response
    weather_info = {}

    # Get the current values and current units for the selected variables
    current_values: dict = response_body.get("current")
    current_units: dict = response_body.get("current_units")

    # For every dictionary in the variables list
    for d in variables:

        # Get the display name and the variable name
        display_name = d.get("display_name")
        variable_name = d.get("variable_name")
        variable_emoji = d.get("emoji")

        # Get the variable value and the variable unit
        variable_value = current_values.get(variable_name)
        variable_unit = current_units.get(variable_name)

        # Tuning variable values
        if variable_name == "is_day":
            current_variable_value = variable_value
            variable_value = "Day" if current_variable_value == 1 else "Night"
            variable_emoji = Emoji.BLACK_SUN_WITH_RAYS if current_variable_value == 1 \
                else Emoji.NEW_MOON_SYMBOL 

        # Get the detailed info about weather code
        # and reset variable unit
        if variable_name == "weather_code":
            variable_value = WMO_CODES[variable_value]
            variable_unit = ""

        # Create the key for the dictionary
        key = f"{variable_emoji} {display_name}"

        # Save the information in the weather info dictionary
        weather_info[key] = f"{variable_value} {variable_unit}"

    return weather_info


# Create the Command Handler
weather_handler = CommandHandler(
    command="weather",
    callback=weather
)
