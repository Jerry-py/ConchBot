import asyncio
import os
from itertools import cycle
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime
from bot.cogs.tags import Tags
from bot.cogs.Currency import Currency
import asyncio
import time
import aiohttp
from bot.cogs.utils.embed import Embeds
import logging

def get_prefix(client, message):
    prefixes = ['cb ', 'cb!', 'cB ', 'CB ', 'Cb ']
    return commands.when_mentioned_or(*prefixes)(client, message)

load_env = load_dotenv()

initial_extensions = [
    "bot.cogs.BotConfig",
    "bot.cogs.Currency",
    "bot.cogs.Fun",
    "bot.cogs.Help",
    "bot.cogs.Image",
    "bot.cogs.Misc",
    "bot.cogs.nsfw",
    "bot.cogs.Secret",
    "bot.cogs.Support",
    "bot.cogs.tags",
    "bot.cogs.Utility"
]

utils_extensions = [
    "bot.cogs.utils.handler"
]

class ConchBot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents.all()
        prefix = get_prefix
        super().__init__(command_prefix=prefix, intents=intents, allowed_mentions=allowed_mentions, case_insensitive=True, strip_after_prefix=True, help_command=None)
        self.launch_time = datetime.utcnow()
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ['JISHAKU_RETAIN'] = "True"
        for cog in initial_extensions:
            self.load_extension(cog)
        if os.getenv("DEBUG") == "True":      
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('discord')
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
            handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
            logger.addHandler(handler)
        self.load_extension('bot.cogs.utils.handler')

    @tasks.loop(seconds=15.0)
    async def status_loop(self):
        statuses = cycle([f"{len(set(self.get_all_members()))} "
            f"users and {len(self.guilds)} servers.", "cb help"])
        while True:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(statuses)))
            await asyncio.sleep(20)

    async def on_ready(self):
        print("------")
        print("ConchBot is online!")
        await self.status_loop()

    async def create_aiohttp_session(self):
        self.aiohttp = aiohttp.ClientSession()
        print("AIOHTTP connection established.")
    
    async def shutdown(self):
        print("------")
        print("Conch Bot Closing connection to Discord...")
        print("------")

    async def close(self):
        print("------")
        print("Conch Bot Closing on keyboard interrupt...\n")
        print("------")

    async def on_connect(self):
        print("------")
        print(f"Conch Bot Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("------")
        print("Conch Bot resumed.")

    async def on_disconnect(self):
        print("------")
        print("Conch Bot disconnected.")

    async def before_command(self, ctx):
        if ctx.command.cog.qualified_name == "NSFW" and not ctx.channel.is_nsfw():
            embed = Embeds().OnError(ctx.command.qualified_name, self.time, "The command can only be used in NSFW channels!")
            await ctx.send(embed=embed)
        await Tags.create_table(self, ctx.guild.id)
        await Currency.open_account(self, ctx.author) 


    def run(self):
        time.sleep(2)
        print("Running bot...")

        TOKEN = os.getenv("TOKEN")
        
        super().run(TOKEN, reconnect=True)
