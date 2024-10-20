from calendar import Calendar, day_abbr, MONDAY, month_abbr
from datetime import datetime
from itertools import batched
from re import search

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


def get_formatted_month_weeks(year: int | None = None, month: int | None= None):

    WEEK_DAYS: int = 7

    # Create the calendar, specifying that the first day of the week is Monday
    calendar: Calendar = Calendar(firstweekday=MONDAY)

    # Get the month days, considering that every 0 is a placeholder
    # starting from Monday.
    # Example:
    # If monday is not the 1st day of the month, a 0 will appear
    # Same applies for the remaining days after the last day of the month
    month_days = list(calendar.itermonthdays(year=year, month=month))

    # Divide the weeks in arrays of seven days, including placeholders
    formatted_month_weeks = list(batched(month_days, WEEK_DAYS))

    return formatted_month_weeks


def create_calendar(year: int | None = None, month: int | None= None):

    # Get the current date
    current_date: datetime = datetime.now()
    
    # If the function parameters are not valorized,
    # then use the current year and month
    year = year or current_date.year
    month = month or current_date.month

    # Save current date information
    current_year =  current_date.year
    current_month = current_date.month
    current_day = current_date.day
    
    # Get the formatted month weeks
    formatted_month_weeks = get_formatted_month_weeks(year=year, month=month)

    # Set the previous month callback data based on the current month
    previous_month_callback_data: str = f"<{year - 1}-12" if month == 1 else f"<{year}-{month - 1}"

    # Set the next month callback data based on the current month
    next_month_callback_data = f">{year + 1}-1" if month == 12 else f">{year}-{month + 1}"

    # Set the calendar header row
    calendar_header_row = [
        # Previous Month
        InlineKeyboardButton(text="<", callback_data=previous_month_callback_data),

        # Current Month Year
        InlineKeyboardButton(text=f"{month_abbr[month]} {year}", callback_data="placeholder"),
        
        # Next Month
        InlineKeyboardButton(text=">", callback_data=next_month_callback_data)
    ]
    
    # Unpack the list of months short names for the days header row
    calendar_days_header_row = [
        *[InlineKeyboardButton(text=day, callback_data="placeholder") for day in day_abbr],
    ]

    # Add these headers to the calendar keyboard
    calendar_keyboard = [
        calendar_header_row,
        calendar_days_header_row
    ]

    # For every week in the formatted month weeks
    for week in formatted_month_weeks:

        # Create an emtpy week row
        week_row = []
        
        # For each day in the current week
        for day in week:

            # If day is 0 (a placeholder),
            # or the day is less than the current day for the current month and year,
            #  then create an empty inline keyboard button
            if day == 0 or (
                day < current_day and 
                month == current_month and 
                year == current_year
            ):

                day_button = InlineKeyboardButton(
                    text=" ",
                    callback_data="placeholder"
                )

            # Otherwise
            else:

                # Create the full date for the day
                date = datetime(year=year, month=month, day=day).strftime("%Y-%m-%d")
                
                # Create the inline keyboard button with the specified info
                day_button = InlineKeyboardButton(
                    text=str(day),
                    callback_data=date
                )

            # Append the day button to the row
            week_row.append(day_button)

        # Append the week row to the calendar keyboard
        calendar_keyboard.append(week_row)

    return InlineKeyboardMarkup(inline_keyboard=calendar_keyboard)
