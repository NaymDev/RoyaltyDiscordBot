import asyncio
import os
import threading
import discord
from discord.ext import commands
import datetime
from random import choice

from utils import NOTIFICATION_TEMPLATES, schedule


from flask import Flask

app = Flask(__name__)

@app.route("/health")
def home():
    return "online", 200, {"Content-Type": "text/plain"}

def run_flask():
    app.run(host="0.0.0.0", port=80)


class RoyaltyBot(commands.Bot):

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix = command_prefix, intents = intents)
        self.pups = {}
        self.tasks = []
        self.ROLES_STAFF = [1244057168626450593, 1266514330913083572, 1238174378814869534, 1302233075513819166, 1298320546123223180, 1215885961511047228]

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                print("Loading cog " + filename[:-3])
                await self.load_extension(f"cogs.{filename[:-3]}")
    

    def add_notification(self, ra: datetime, view, omsg: discord.Message):
        self.loop.create_task(schedule(lambda: self.notify(view, omsg.jump_url), ra))

    def add_giveaway(self, ra: datetime, view):
        self.loop.create_task(schedule(lambda: self.announce(view), ra))
    
    def add_pups(self, ra: datetime, view):
        self.loop.create_task(schedule(lambda: self.final_pups(view), ra))
    

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
    
    async def final_pups(self, view: discord.ui.View):
        diff = view.data.votes["yes"] - view.data.votes["no"]
        if diff == 0:
            view.data.timestamp = datetime.now() + datetime.timedelta(hours=48)
            self.add_pups(view.data.timestamp, view)
            return
        elif diff > 0:
            await view.message.channel.send(f'{await view.data.user.mention} will get the **{"Premium" if view.data.isPremium else "Ultimate"}** role')
            if view.data.isPremium:
                await view.data.user.add_role(1216075428834578463)
            else:
                await view.data.user.add_role(1297941958773309460)
        else:
            await view.message.channel.send(f"{await view.data.user.mention} won't get the **{'Premium' if view.data.isPremium else 'Ultimate'}** role")
            if view.data.isPremium:
                await view.data.user.remove_role(1216075428834578463)
            else:
                await view.data.user.remove_role(1297941958773309460)
        
        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await view.message.edit(view=view)
        view.stop()

if __name__ == "__main__":
    print("----------------------")

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("__-__-__-__-__-__-__-__-__")

    intents = discord.Intents.default()
    intents.message_content = True
    bot = RoyaltyBot(command_prefix="!", intents=intents)

    asyncio.run(bot.run(os.environ["DISCORD_TOKEN"])) # TOKEN