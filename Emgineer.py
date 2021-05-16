import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl
import random
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReg, Request
load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='bc ',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}
song_queue = []
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        print(url)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

@bot.command(name='hello')
async def hello(ctx):
    await ctx.message.channel.send("hi")

@bot.command(name='size')
async def size(ctx):
    await ctx.message.channel.send("pennice of "+str(ctx.message.author).split('#')[0]+"\n"+"8"+random.randint(1, 100)*"="+"D")

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', help='To play song')
async def play(ctx):
    server = ctx.message.guild
    voice_channel = ctx.message.guild.voice_client
    title = ctx.message.content[8:]
    print(song_queue)
    async with ctx.typing():
        await ctx.send(f'**Searching:** {title}')
        filename = await YTDLSource.from_url(title, loop=bot.loop)
        os.rename(filename, filename.split(".")[0]+".mp3")
        voice_channel.play(discord.FFmpegPCMAudio(filename.split(".")[0]+".mp3"))
        song_queue.append(title)
        await ctx.send('**Now playing:** {}'.format(filename.split(".")[0]))


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='panu', help='To find Xvideo')
async def xvideos(ctx):
    title = ctx.message.content[8:]
    try:
        my_url = f"https://www.xvideos.com/?k={title}"
        uClient = uReg(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        total = page_soup.find_all('div', {'class': 'thumb-inside'})

        for i in range(0,5):
            await ctx.send("https://www.xvideos.com"+total[i].div.a['href'])
            
    except:
        await ctx.send("No matching panu")

@bot.command(name='show', help='To get porn images')
async def xvideos(ctx):
    try:
        title = ctx.message.content[8:]
        query = ""
        for i in title.split(" "):
            query+=i+"%20"
        my_url = f"https://www.google.com/search?q={query}%20porn&hl=en&tbm=isch"
        req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
        uClient = uReg(req)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")

        total = page_soup.find_all('img')
        #print(total)
        ind = random.randint(1, len(total)-1)
        await ctx.send(total[ind].get('src'))
    except:
        await ctx.send("No matching panu images")


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)
    print("My Ready is Body")