# Sample Assistant Bot

## Introduction

This project started as a personal project to experiment and test the several functionalities offered by the [python-telegram-bot](https://python-telegram-bot.org/) wrapper.

After thinking about the functionalities I wanted to develop for myself, I thought that it'd have been fun to develop something that many users could use.

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

## Commands

### `/help`
With this command, the user can get help on the various features that the bot provides.<br>
By typing `/help <command>`, the user receives a specific guide on how to use the command provided.

[INSERT IMAGES HERE]

### `/news`
With this command, the user receives a set of local news based on the user's location.<br>
Please note that without setting a location, this command is unable to provide the expected result.

[INSERT IMAGES HERE]

### `/setlocation`
With this command, the user can save its location to the database.

[INSERT IMAGES HERE]

### `/todo`
With this command, the user can create a todo with an optional reminder.
A todo has different attributes, like:
- _details_, or todo's body
- _due date_, or todo's completion date
- _remind at_, or todo's reminder (optional)

Please note that without setting a location, this command is unable to provide the expected result.

[INSERT IMAGES HERE]

### `/todos`
With this command, the user can manage the list of its todos.

[INSERT IMAGES HERE]

### `/weather`
With this command, the user receives weather information based on its location.<br>
Please note that without setting a location, this command is unable to provide the expected result.

[INSERT IMAGES HERE]



