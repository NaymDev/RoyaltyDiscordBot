import asyncio
import os
from typing import List
import discord
from discord.ext import commands
import datetime
from random import choice, choices

from utils import NOTIFICATION_TEMPLATES, schedule


class RoyaltyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix = command_prefix, intents = intents)
        self.pups = {}
        self.tasks = []

    async def on_ready(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                print("Loading cog " + filename[:-3])
                await self.load_extension(f"cogs.{filename[:-3]}")
    

    def add_notification(self, ra: datetime, view, omsg: discord.Message):
        self.loop.create_task(schedule(lambda: self.notify(view, omsg.jump_url), ra))

    def add_giveaway(self, ra: datetime, view):
        self.loop.create_task(schedule(lambda: self.announce(view), ra))
    

    async def notify(self, view: discord.ui.View, omessage):
        tournament_timestamp = int((datetime.datetime.now() + datetime.timedelta(minutes=10)).timestamp())

        for member in view.members:
            await member.send(choice(NOTIFICATION_TEMPLATES).replace("{time_left}", f"<t:{tournament_timestamp}:R>"))
            await member.send(omessage)
        
        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await view.message.edit(view=view)
        view.stop()
    
    async def announce(self, view: discord.ui.View):
        await view.message.channel.send(f"{(await view.get_winner()).mention} won the giveaway")
        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await view.message.edit(view=view)
        view.stop()

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = RoyaltyBot(command_prefix="!", intents=intents)

    bot.run("") # TOKEN