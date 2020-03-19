import os
import discord
import requests
import random
import re
import datetime
import calendar
import asyncio
import time
import ffmpeg
import youtube_dl

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands
from tts import tts
from youtube import YTDLSource

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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == 'raise-exception':
        raise discord.DiscordException


# error handling
@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n\n')
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

@bot.command(name='inspire', help="Delivers an inspirational quote just like Dani!")
async def quote(ctx):
    filename = 'quote_tts'
    # parse http request
    page = requests.get('https://www.insightoftheday.com')
    soup = BeautifulSoup(page.text, 'html.parser')

    # extract info
    daily_post = soup.find('div', class_='daily-post')
    author = daily_post.find('h2', class_='entry-title').find(text=True).rsplit(' by ', 1)[1]
    quote_contents = daily_post.find('div', class_='quote').find('img')
    quote_text = quote_contents.attrs.get('alt').split(': ', 1)[1].rsplit('\xa0', 1)[0]

    # create mp3 file from quote_text
    tts(quote_text, filename)

    # write message
    embed = discord.Embed(title=f'{calendar.day_name[datetime.datetime.today().weekday()]}\'s Inspirational Quote', description="Are you feeling motivated?", color=0x00ff00)
    embed.add_field(name="Quote", value=quote_text)
    embed.set_image(url=quote_contents.attrs.get('src'))
    #embed.set_footer(text='You are out of my LOS', icon_url=quote_contents.attrs.get('src'))
    #embed.set_footer(text='You are out of my LOS')
    embed.set_footer(text=author)
    await ctx.send(embed=embed, tts=False)
    #await ctx.voice_client.disconnect()

    # activate text to speech
    channel = ctx.author.voice.channel
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(f'{filename}.mp3'), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()
    await vc.disconnect()
    os.remove(f'{filename}.mp3')


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

@bot.command(name='hello')
async def hello(ctx):
    print('hello!')

# play music from youtube URL
@bot.command(name='play')
async def play(ctx, url):
    async with ctx.typing():
        # set stream to false -> predownloads files (good if internet isn't great)
        player = await YTDLSource.from_url(url, loop=bot.loop)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('Now playing: {}'.format(player.title))

@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

bot.run(token)