import asyncio
import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl
import random
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReg, Request
import smtplib
from pymitter import EventEmitter
from googlesearch import search
import requests
from discord.utils import get
from youtubesearchpython import VideosSearch,Video
import pafy 

ee = EventEmitter()

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
EMAIL_PASS = os.getenv("email_pass")
# COVID_KEY = os.getenv("covid_api_key")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="bc ")

songque=[]

islooped=True
#covid api
# url = "https://corona-virus-world-and-india-data.p.rapidapi.com/api_india"

# headers = {
#     'x-rapidapi-key': COVID_KEY,
#     'x-rapidapi-host': "corona-virus-world-and-india-data.p.rapidapi.com"
#     }

# response = requests.request("GET", url, headers=headers)
# response1 = response.json()
# print(response1)
#covid api

ytdl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

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

@bot.command(name='play', help='to search something')
async def play(ctx, url):
    voiceChannel = ctx.message.author.voice.channel
    voice_client = get(ctx.bot.voice_clients, guild=ctx.guild)
    if(voice_client!=None):
        print("connected previously")
    else:
        await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        try:
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            messege = ctx.message.content.split('bc play ')[1]
            print(messege)
            print(ctx.message.content)
            videosSearch = VideosSearch(messege, limit=1)
            video1 =videosSearch.result()
            url = video1['result'][0]['link']
            name=video1['result'][0]['title']
            duration=video1['result'][0]['duration']
            dura=duration.split(":")
            dura.reverse()
            durasecounds=int(dura[0])
            for i in range(1,len(dura)):
                durasecounds=durasecounds+int(dura[i])*60
            print(durasecounds)
            
            

            songque.append({
                "name": name,
                "stream":url,
                "duration":durasecounds
            })
            await afterplay(ctx)
        except:
            print("some error")
    else:
        try:
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            messege = ctx.message.content.split('bc play ')[1]
            print(messege)
            print(ctx.message.content)
            videosSearch = VideosSearch(messege, limit=1)
            video1 =videosSearch.result()
            url = video1['result'][0]['link']
            name=video1['result'][0]['title']
            duration=video1['result'][0]['duration']
            dura=duration.split(":")
            dura.reverse()
            durasecounds=int(dura[0])
            for i in range(1,len(dura)):
                durasecounds=durasecounds+int(dura[i])*60
            
            

            songque.append({
                "name": name,
                "stream":url,
                "duration":durasecounds
            })
            print(songque)
            await ctx.send(f"added to que {name}")
        except:
            await ctx.send("something went wrong")


@bot.command(name='queue', help='to search something')
async def queue(ctx):
    for i in range(0, len(songque)):
        await ctx.send(f"{i} {songque[i]['name']}")

@bot.command(name='clear', help='to search something')
async def clear(ctx):
    if len(songque)>0:
        songque.clear()
        await ctx.send("song queue cleared")
    else:
        await ctx.send("There is no song in queue to clear")

@bot.command(name='skip', help='to search something')
async def skip(ctx):
    if len(songque)>1:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()
        songque.pop(0)
        print(len(songque))
        print("runned")
        print(ctx)
        await afterplay(ctx)
    else:
        await ctx.send("there is no next song in the queue")

@bot.command(name='leave', help='to search something')
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        songque.clear()
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='to search something')
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        global islooped
        islooped=False
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@bot.command(name='resume', help='to search something')
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        global islooped
        islooped=True
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@bot.command(name='stop', help='to search something')
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


async def afterplay(ctx):
    print("afterplay")
    if(len(songque)!=0):
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        video = pafy.new(songque[0]['stream']) 
        streams = video.allstreams
        stream = streams[0]
        value = stream.url_https
        await ctx.send(f"playing {songque[0]['name']} \n {songque[0]['stream']}")
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        source = await discord.FFmpegOpusAudio.from_probe(str(value), **FFMPEG_OPTIONS)
        voice.play(source)
        await queueafter(ctx)
        # t = Timer(int(songque[0]['duration']), queueafter,[ctx])
        # t.start()



async def queueafter(ctx):
    await asyncio.sleep(int(songque[0]['duration']))
    if(islooped==True):
        try:
            songque.pop(0)
            print(len(songque))
            print("runned")
            print(ctx)
            await afterplay(ctx)
        except:
            print("queue ended")

# @bot.command(name='stop', help='Stops the song')
# async def stop(ctx):
#     voice_client = ctx.message.guild.voice_client
#     if voice_client.is_playing():
#         await voice_client.stop()
#     else:
#         await ctx.send("The bot is not playing anything at the moment.")





@bot.command(name='mail', help='to send email')
async def mail(ctx):
    try:
        title = ctx.message.content[8:]
        credentials = title.split(" ")
        mail = credentials[0]
        msg = title.replace(credentials[0],"")

        server = smtplib.SMTP_SSL("smtp.gmail.com",465)
        server.login("lastbenchdevs@gmail.com", EMAIL_PASS)
        server.sendmail("lastbenchdevs@gmail.com",mail,msg)
        server.quit()
        await ctx.send("Email send succesfully to "+mail)
    except:
        await ctx.send("Messege Not Send")

@bot.command(name='search', help='to search something')
async def mail(ctx):
    try:
        title = ctx.message.content[10:]
        for i in search(title):
                    finalReply = str(i)
                    await ctx.send(finalReply)
    except:
        await ctx.send("Not Found Any Result")

@bot.command(name='meme', help='to search something')
async def mail(ctx):
    try:
        r = requests.get('https://meme-api.herokuapp.com/gimme/wholesomememes')
        pic_url = r.json()['preview'][2]
        await ctx.send(pic_url)
        
    except:
        await ctx.send("No meme found")

# @bot.command(name='cs', help='to search something')
# async def mail(ctx):
#     try:
#         title = ctx.message.content[6:]
        
#         string = title.split()
                
#         for i in range(len(string)):
#             string[i] = string[i].replace(string[i], string[i].capitalize())

#         listToStr = ' '.join([str(elem) for elem in string])
#         await ctx.send(listToStr)
#         if(listToStr == "India"):
#                     try:
#                         for each in response1['total_values']:
#                             finalReply = each + ' : '+ response1['total_values'][each]
#                             await ctx.send(finalReply)
                            
#                     except KeyError:
#                             finalReply = "i have not found any data of this country " + str(listToStr)
#                             await ctx.send(finalReply)
                            
                        
#         else:
#             try:
#                 for each in response1['state_wise'][str(listToStr)]:
#                     finalReply = each + ' : ' + response1['state_wise'][str(listToStr)][each]
#                     await ctx.send(finalReply)
#                     if(each == 'statenotes'):
#                         break
                            
#             except KeyError:
#                     finalReply = "i have not found any state with the name of " + str(listToStr)
#                     await ctx.send(finalReply)
                        

#     except:
#         await ctx.send("No state Found")

@bot.command(name='weather', help='to search something')
async def mail(ctx):
    try:
        ciry = ctx.message.content[11:]
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={ciry}&appid=6fed6f20c4335444cc1258a52b955765').json()
        try:
            wind = "wind speed:s "+ str(response['wind']['speed']) + " km/h"
            temprature = "temp: "+ str(response['main']['temp'])+" F"
            description = "it might be "+str(response['weather'][0]['description'])+" outside"
            humidity = "humidity is "+ str(response['main']['humidity'])+"%"
            atm = "atm pressure "+str(response['main']['pressure'])
            finalReply = str(temprature)+"\n"+str(wind)+"\n"+str(humidity)+"\n"+str(atm)+"\n"+str(description)
            await ctx.send(finalReply)
            
        except:
            finalReply = "i cant find the data of" + ciry
            await ctx.send(finalReply)

        
    except:
        await ctx.send("No meme found")

@bot.command(name='joke', help='for joke')
async def mail(ctx):
    try:
        r = requests.get('https://icanhazdadjoke.com/slack')
        joke = r.json()['attachments'][0]['text']
        finalReply = joke
        await ctx.send(finalReply)
        
    except:
        await ctx.send("At this time i dont remember a joke sorry")
        
        
bot.run(DISCORD_TOKEN)