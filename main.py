from typing import Final
import os
import discord
import sys
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response, normalize_name, HelpMessage, get_best_match, levenshtein_distance

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled)')
        return
    
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    user_message = user_message.lower()
    try:
        response: str = get_response(user_message)
        request = user_message.split(" ")
        if len(request) > 3:
            request[1] = '-'.join(request[1:3])
            del request[2]
        request[1] = normalize_name(request[1])
        normalizedName = normalize_name(request[1])
        foundCharacterName = get_best_match(normalizedName, 2)
        request[1] = foundCharacterName
                
        if ("all" in user_message) or (len(request) == 2):
            embed = discord.Embed(
                color=discord.Color.dark_gold(),
                title="INPUTS FOR "+request[1].replace("k.","").upper(),
            )
            
            inputArray = response.split("&")
            if "k." in request[1]:
                newArray = inputArray[0]
                newArray = newArray.split("\n")
                n = len(newArray) // 2
                part1 = newArray[:n+1]
                part2 = newArray[n+1:]
                embed.add_field(name="__Normals__", value="\n".join(part1), inline=True)
                embed.add_field(name="\u200B", value="\n".join(part2), inline=True)
                embed.add_field(name="\u200B", value="\u200B", inline=True)
                embed.add_field(name="__Finishers__", value=inputArray[1], inline=True)
                
            else:
                #embed.add_field(name="Normals", value=inputArray[0], inline=True)
                newArray = inputArray[0]
                newArray = newArray.split("\n")
                n = len(newArray) // 3
                print(n)
                # Split the array into 3 equal parts
                part1 = newArray[:n+1]
                part2 = newArray[n+1:2*n+2]
                part3 = newArray[2*n+2:]
                embed.add_field(name="__Normals__", value="\n".join(part1), inline=True)
                embed.add_field(name="\u200B", value="\n".join(part2), inline=True)
                embed.add_field(name="\u200B", value="\n".join(part3), inline=True)
                newArray = inputArray[1]
                newArray = newArray.split("\n")
                n = len(newArray) // 2
                # Split the array into 3 equal parts
                part1 = newArray[:n+1]
                part2 = newArray[n+1:]
                embed.add_field(name="__Specials__", value="\n".join(part1), inline=True)
                embed.add_field(name="\u200B", value="\n".join(part2), inline=True)
                embed.add_field(name="__Finishers__", value=inputArray[2], inline=True)
                
        else:
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=request[1].replace("k.","").upper(),
                description="*Results for: "+request[2]+"*"
            )
            inputArray = response.split("---")

            for i in range(len(inputArray)):
                embed.add_field(name='\u200B', value=inputArray[i], inline=True)
        embed.set_footer(text="Kombat Akademy", icon_url="https://mk1.kombatakademy.com/images/site/avatar.png")
        
        if "k." in request[1]:
            request[1] = request[1].replace("k.","")
            embed.set_thumbnail(url=f"https://mk1.kombatakademy.com/images/kameos/portraits/{request[1]}.png")
            embed.url=f'https://mk1.kombatakademy.com/move-list/?kameo={request[1].replace("k.","")}'
        else:
            #NORMALIZING NAMES FOR CORRECT WEB LINKS
            if "noob" in request[1]:
                request[1] = "noob-saibot"
            embed.set_thumbnail(url=f"https://mk1.kombatakademy.com/images/characters/portraits/{request[1]}.jpg")
            embed.url=f'https://mk1.kombatakademy.com/move-list/?character={request[1]}'
        
        await message.author.send(embed=embed) if is_private else await message.channel.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            color=discord.Color.blue(),
            description=HelpMessage()
        )
        await message.author.send(response) if is_private else await message.channel.send(embed=embed)
        print(f"main.py error {e}")


@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

@client.event
async def on_message(message: Message) -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    if client.user.mentioned_in(message) and not message.author.bot:
        await send_message(message, user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()
