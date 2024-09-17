# MK1-FrameDataBot
## Overview

This code could be streamlined further but is structured well enough to be readable.

Main.py handles listening for an @mention for activation, as well as managing Discord embeds, thumbnails, and formatting responses. Responses.py contains the main query logic, including web scraping from MK1.KombatAkademy.com, formatting, query normalization, and alias handling.

## Functionality

After being @mentioned, the bot expects two additional words: the character name and the input you want to search for. If "ALL" is used instead of the input, the bot will return a list of all inputs found on Kombat Akademy for that character. Due to the way the data is structured, some data may display inaccurately. For example, Kitana’s "2412" string only has startup and recovery information, as there’s limited data for that move.
The script has some leniency with misspelling. As of this commit, you are allowed 2 mispellings.
If no match for the character's name or input is found, the help message will be returned.

## Instructions for Use

1. @mention the bot.
2. Provide the character's name, followed by either a specific input or the word "ALL."

Note: To search for Kameo characters, prefix the character name with "k."
Examples: 
@MK1-FrameDataBot reptile b2
@MK1-FrameDataBot k.scorpion all
    

