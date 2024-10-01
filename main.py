import asyncio
import json

import discord

from discord.ext import commands
from music_box import MusicBox

config = json.load(open('config.json'))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    intents=intents,
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def main():
    async with bot:
        await bot.add_cog(MusicBox(bot))
        await bot.start(config['token'])

if __name__ == '__main__':
    asyncio.run(main())