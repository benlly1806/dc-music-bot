import asyncio

import discord
import yt_dlp

from discord.ext import commands

ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl= yt_dlp.YoutubeDL(ytdl_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
    
class MusicBox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
    
    @commands.command()
    async def join(self, ctx: commands.context.Context) -> None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()

    @commands.command()
    async def leave(self, ctx: commands.context.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx: commands.context.Context, *, url: str) -> None:
        await self.join(ctx)
        
        async with ctx.typing():
            if ctx.voice_client.is_playing():
                await ctx.send("I'm busy")
                return
                # self.song_queue.append(url)
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player)
        await ctx.send(f'Now playing: {player.title}')