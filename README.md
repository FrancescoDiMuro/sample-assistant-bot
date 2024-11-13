# Sample Assistant Bot (a.k.a. Aski)
## Summary
- [Introduction](#introduction)
- [Purpose](#purpose)
- [Before you start the bot](#before-you-start-the-bot)
- [Starting the bot](#starting-the-bot)
- [Commands](#commands)
- [Setup](#setup)
- [Known issues](#known-issues)
- [Ongoing implementations](#ongoing-implementations)
- [Future implementations](#future-implementations)

## Introduction
This project ([@sampleassistantbot](https://t.me/sampleassistantbot)) started as a personal project to experiment and test the several functionalities offered by the [python-telegram-bot](https://python-telegram-bot.org/) wrapper.<br>
After thinking about the functionalities I wanted to develop for myself, I thought that it'd have been fun to develop something that many users could use.<br>
So, I started to develop a general purpose bot, to assist the users during their daily tasks, just like a virtual assistant, but without the support of kind of AI.

That's it.

## Purpose
The purpose of the bot is to provide the user a set of functionalities that it can use to get informed on the local news, or to create a todo, or to get weather information.

The user can interact accomplish these actions thanks to a set of commands, like:
- [`/help`](#help), to guide the user using the bot
- [`/news`](#news), to read the latest local news (based on user's location)
- [`/setlocation`](#setlocation), to let the user set (and save) its location to the database
- [`/todo`](#todo), to create a todo (with optional reminder)
- [`/todos`](#todos), to list, check or remove user's todos
- [`/weather`](#weather), to show the current weather (based on user's location)

## Before you start the bot
If you read the [Purpose](#purpose) section of this document, you've probably noticed that for some commands, their use is dependant on the user's location.<br>
That's because the bot can't give the user information about the local news or about the weather if it doesn't know where the user is located.<br>
Additionally, to let users from all around the world use this bot, I had to take care about different time zones, always based on the user's location.<br>
Therefore, before you start, you need to know that the bot will save the location you'll share with it.<br>
That means that, for testing purposes, you don't have to use your _actual_ location, but you can set any nearby location, so you don't have to deal with different time zones if you want to test the `/todo` command features,
or have a complete different results when using the `/weather` command.

<b>Please note:</b> the bot is currently offline, since I still didn't deploy it somewhere.

## Starting the bot
Once you start the bot, you'll see:
<div align="left">
    <img src="docs/assets/start.png" width="30%" alt="start_image">
    <img src="docs/assets/start_user_agreement.png" width="30%" alt="start_user_agreement_image">
    <img src="docs/assets/start_user_agreement_accepted.png" width="30%" alt="start_user_agreement_accepted_image">
</div>

## Commands
### `/help`
With this command, the user can get help on the various features that the bot provides.<br>
By typing `/help <command>`, the user receives a specific guide on how to use the command provided.

<div align="left">
    <img src="docs/assets/help.png" width="30%" alt="help_image">
    <img src="docs/assets/help_news.png" width="30%" alt="help_news_image">
    <img src="docs/assets/help_unknown_command.png" width="30%" alt="help_unknown_command_image">
</div>

### `/news`
With this command, the user receives a set of local news based on the user's location.<br>
<b>Please note:</b> without setting a location, this command is unable to provide the expected result.

<div align="left">
    <img src="docs/assets/news.png" width="30%" alt="news_image">
</div>

### `/setlocation`
With this command, the user can save and update its location.<br>
<b>Please note:</b> if you try to share your location from Telegram Desktop, you'll see a message like the rightmost one:
<div align="left">
    <img src="docs/assets/setlocation.png" width="30%" alt="set_location_image">
    <img src="docs/assets/setlocation_ok.png" width="30%" alt="set_location_ok_image">
    <img src="docs/assets/setlocation_from_tg_desktop.png" width="30%" alt="setlocation_from_telegram_desktop_image">
</div>

### `/todo`
With this command, the user can create a todo with an optional reminder.
A todo has different attributes, like:
- _details_, or todo's body
- _due date_, or todo's completion date
- _remind at_, or todo's reminder (optional)

<b>Please note:</b> without setting a location, this command is unable to provide the expected result.

<div align="left">
    <img src="docs/assets/todo_input_details.png" width="30%" alt="todo_input_details_image">
    <img src="docs/assets/todo_input_due_date.png" width="30%" alt="todo_input_due_date_image">
    <img src="docs/assets/todo_input_due_time.png" width="30%" alt="todo_input_due_time_image">
</div>

The user can optionally set a reminder:

<div align="left">
    <img src="docs/assets/todo_user_choice.png" width="30%" alt="todo_user_choice_image">
    <img src="docs/assets/todo_input_reminder_time.png" width="30%" alt="todo_input_reminder_time_image">
    <img src="docs/assets/todo_with_reminder_ok.png" width="30%" alt="todo_with_reminder_ok_image">
</div>

Once the to-do reminder is triggered, the user can react with an emoji to the message to mark it as completed:

<div align="left">
    <img src="docs/assets/todo_reminder_triggered.png" width="30%" alt="todo_reminder_triggered_image">
    <img src="docs/assets/todo_reminder_pre-reaction.png" width="30%" alt="todo_reminder_pre-reaction_image">
    <img src="docs/assets/todo_reminder_post-reaction.png" width="30%" alt="todo_reminder_post-reaction_image">
</div>

If the to-do is created without a reminder, the user will be reminded just at the to-do due date/time:

<div align="left">
    <img src="docs/assets/new_todo_input_details.png" width="30%" alt="new_todo_input_details_image">
    <img src="docs/assets/new_todo_input_due_date.png" width="30%" alt="new_todo_input_due_date_image">
    <img src="docs/assets/new_todo_input_due_time.png" width="30%" alt="new_todo_input_due_time_image">
    <img src="docs/assets/new_todo_without_reminder_ok.png" width="30%" alt="new_todo_without_reminder_ok_image">
    <img src="docs/assets/todo_completed_from_details.png" width="30%" alt="todo_completed_from_details_image">
</div>

### `/todos`
With this command, the user can manage the list of its todos.

<div align="left">
    <img src="docs/assets/todos.png" width="30%" alt="todos_image">
    <img src="docs/assets/todos_with_reminder.png" width="30%" alt="todos_with_reminder_image">
    <img src="docs/assets/todos_without_reminder.png" width="30%" alt="todos_without_reminder_image">
</div>

### `/weather`
With this command, the user receives weather information based on its location.<br>
Please note that without setting a location, this command is unable to provide the expected result.

<div align="left">
    <img src="docs/assets/weather.png" width="30%" alt="weather_image">
</div>

## Setup

In this section, you can find the step-by-step guide on how to run this project on your local machine.

First thing first, clone the repository locally with the command

```cmd
git clone https://github.com/FrancescoDiMuro/sample-assistant-bot.git
```

Then, you can proceed in two ways:
1. [using Docker Compose](#using-docker-compose)
2. [using the virtual environment](#using-the-virtual-environment)


### Using Docker Compose
Be sure to have Docker Compose installed on your PC.<br>
Then, once you changed directory to the projet root, all you need to do is execute the command

```cmd
docker compose --env-file ./app/.env up --detach
```
and you're pretty much done.

If you want to remove the app from Docker, together with the app image and the created volume, use the command

```cmd
docker compose down --rmi local --volumes
```

### Using the Virtual Environment
If you don't want or you can't use the Docker Compose solution, you might want to use this one.

First thing first, be sure to have installed [Python](https://www.python.org/downloads/) on your PC.<br>
This application has been developed with Python 3.12.7, but every version equal or above 3.10 should work fine.

If you want to be sure that you've installed Python correctly, or you want to check if you already have it installed on your PC, use the command

```cmd
python --version
```

or

```cmd
py --version
```

Once you managed to install/verify that Python is installed on your PC, you need to create a [virtual environment](https://docs.python.org/3/library/venv.html).

Move to the project root, and run the command

```cmd
python -m venv ./.venv
```

or, if you have already the `virtualenv` package installed

```cmd
python -m virtualenv ./.venv
```

Once the command finishes its execution, you have to activate the _venv_, using the command

```cmd
./.venv/Scripts/activate
```

You can verify that the _venv_ has been correctly activated by checking the prefix `(.venv)` before the path in the terminal.

Moving on, you need to install the required packages, executing the command

```cmd
pip install -r ./app/requirements.txt
```

Once the command finishes its execution, you completed the application setup, and it's time to setup the database.

This step depends mainly on your preferences, but if you want to make it simple, you can use a local [SQLite](https://www.sqlite.org/index.html) database.

All you need to do is to be sure that you're using the SQLite values for the environment variables in the .env file for the SQLAlchemy section (default).

In case you want to use another database, you can set it up and update the environment variables accordingly (following the [official SQLAlchemy documentation](https://docs.sqlalchemy.org/en/20/dialects/)).

Once you've completed this step, use the command
```cmd
python app
```

to start the bot.

## Known issues
### Use of synchronous connections with the database
At the moment, the bot doesn't use an async connections to the database through the SQLAlchemy ORM, so there might be issues related to this implementation.

## Ongoing implementations
- [x] Create a todo with a message

## Future implementations
- [ ] Async connections with the database
- [ ] Add integration tests
- [ ] Encrypt user data
- [ ] Let the user delete its data from the database

[Go to summary](#summary)