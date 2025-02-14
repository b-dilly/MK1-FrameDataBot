# MK1-FrameDataBot
## Overview

Main.py handles listening for an @mention for activation, as well as managing Discord embeds, thumbnails, and formatting responses. Responses.py contains the main query logic, ~~including web scraping from MK1.KombatAkademy.com~~, formatting, query normalization, and alias handling.

Update: The MK1.KombatAkademy.com has been discontinued. The owner of the project has given me the necessary files to continue this bot's functionality. Main.py and responses.py have been updated to accomodate this change

## Functionality

After being @mentioned, the bot expects two additional words: the character name and the input you want to search for. If "ALL" is used instead of the input, the bot will return a list of all inputs found on Kombat Akademy for that character. Due to the way the data is structured, some data may display inaccurately.

The script has some leniency with misspelling character names. As of this commit, you are allowed 2 mispellings.
If no match for the character's name or input is found, the help message will be returned.

## Instructions for Use

1. @mention the bot.
2. Provide the character's name, followed by either a specific input or the word "ALL."

Note: To search for Kameo characters, prefix the character name with "k."

Examples: 

@MK1-FrameDataBot reptile b2

@MK1-FrameDataBot k.scorpion all
    

## Link to add bot to server
https://discord.com/oauth2/authorize?client_id=1263851539429199872&permissions=67584&integration_type=0&scope=bot
