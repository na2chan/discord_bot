import os
import discord
import requests
import random
import re
import datetime
import calendar

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

'''  
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!inspire':
        response = "DUMMY"
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException
'''

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.command(name='inspire', help="Delivers an inspirational quote just like Dani")
async def quote(ctx):
    # parse http request
    page = requests.get('https://www.insightoftheday.com')
    soup = BeautifulSoup(page.text, 'html.parser')

    # extract info
    daily_post = soup.find('div', class_='daily-post')
    author = daily_post.find('h2', class_='entry-title').find(text=True).rsplit(' by ', 1)[1]
    quote_contents = daily_post.find('div', class_='quote').find('img')
    quote_text = quote_contents.attrs.get('alt').split(': ', 1)[1].rsplit('\xa0', 1)[0]

    # write message
    embed = discord.Embed(title=f'{calendar.day_name[datetime.datetime.today().weekday()]}\'s Inspirational Quote', description="Are you feeling motivated?", color=0x00ff00)
    embed.add_field(name="Quote", value=quote_text)
    embed.set_image(url=quote_contents.attrs.get('src'))
    #embed.set_footer(text='You are out of my LOS', icon_url=quote_contents.attrs.get('src'))
    #embed.set_footer(text='You are out of my LOS')
    embed.set_footer(text=author)
    await ctx.send(embed=embed)


@bot.command(name='roll')
async def roll(ctx, number_of_dice: int=1, number_of_sides: int=6):
    dice = []
    for _ in range(number_of_dice):
        dice.append(str(random.choice(range(1, number_of_sides + 1))))
    
    response = ', '.join(dice)
    if (len(response) >= 2000):
        await ctx.send('DANI cannot comprehend your dice rolls. Discord has a 2000 character limit per message. Stop rolling so many dice.')
    else:
        await ctx.send(response)



@bot.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == 'raise-exception':
        raise discord.DiscordException


# error handling
@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n\n')
        else:
            raise

bot.run(token)