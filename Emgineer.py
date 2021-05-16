import discord
import random

from discord import message

TOKEN = 'ODQzMzMwODAxNjY0MTMxMTEy.YKCTAw.RM_FBQNRvTh7LaLHZVh3PrAerOw'


import discord
from discord.ext import commands



bot = commands.Bot(command_prefix='>', description="This is a Helper Bot")


# Events
@bot.event
async def on_ready():
    print('My Ready is Body')


@bot.listen()
async def on_message(message):
    if "hello" == message.content.lower():
        await message.channel.send('hi')
    if "size" == message.content.lower():
        await message.channel.send("8"+random.randint(1, 100)*"="+"D")

bot.run(TOKEN)