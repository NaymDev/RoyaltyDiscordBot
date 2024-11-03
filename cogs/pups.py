import datetime
from os import times
import discord
from discord.ext import commands
from discord.ui import Button, View
from main import RoyaltyBot
from utils import MemberOrRoleConverter, PremiumUltimateViewData

# 48h vote
class VoteView(View):
    def __init__(self, bot: RoyaltyBot, data):
        super().__init__()
        self.data = data
        self.bot = bot
        self.bot.pups[self.id] = {}

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        if (self.bot.pups[self.id].get(interaction.user.id) == "yes"):
            await interaction.response.send_message("You have already upvoted!", ephemeral=True)
            return
        elif (self.bot.pups[self.id].get(interaction.user.id) == "no"):
            self.data.votes["no"] -= 1
        
        self.bot.pups[self.id][interaction.user.id] = "yes"
        self.data.votes["yes"] += 1
        await interaction.response.edit_message(embed=self.get_vote_embed())

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        if (self.bot.pups[self.id].get(interaction.user.id) == "no"):
            await interaction.response.send_message("You have already downvoted!", ephemeral=True)
            return
        elif (self.bot.pups[self.id].get(interaction.user.id) == "yes"):
            self.data.votes["yes"] -= 1

        self.bot.pups[self.id][interaction.user.id] = "no"
        self.data.votes["no"] += 1
        await interaction.response.edit_message(embed=self.get_vote_embed())

    def get_vote_embed(self):
        diff = self.data.votes["yes"] - self.data.votes["no"]
        embed = discord.Embed(
            title=f'{"Premium" if self.data.isPremium else "Ultimate"} Role Vote',
            description=self.data.description,
            color=discord.Color.blue() if diff == 0 else discord.Color.red() if diff < 0 else discord.Color.green(),
            timestamp=self.data.timestamp
        )
        embed.add_field(name="👍 Yes", value=str(self.data.votes["yes"]), inline=True)
        embed.add_field(name="👎 No", value=str(self.data.votes["no"]), inline=True)
        embed.set_footer(text="Ends at")
        return embed


class PupsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="premium")
    @commands.has_permissions(administrator = True)
    async def premium(self, ctx: commands.Context, user: MemberOrRoleConverter = None):
        if user is None or not isinstance(user, discord.Member):
            await ctx.send("Please mention a user to create a **Premium** vote")
        else:
            time = datetime.datetime.now() + datetime.timedelta(hours=48)
            view = VoteView(self.bot, PremiumUltimateViewData(user, time, True))
            self.bot.add_pups(time, view)
            await ctx.send(embed=view.get_vote_embed(), view=view)
    
    @commands.command(name="ultimate")
    @commands.has_permissions(administrator = True)
    async def ultimate(self, ctx: commands.Context, user: MemberOrRoleConverter = None):
        if user is None or not isinstance(user, discord.Member):
            await ctx.send("Please mention a user to create a **Ultimate** vote")
        else:
            time = datetime.datetime.now() + datetime.timedelta(hours=48)
            view = VoteView(self.bot, PremiumUltimateViewData(user, time, True))
            self.bot.add_pups(time, view)
            await ctx.send(embed=view.get_vote_embed(), view=view)
        

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if "hello bot" in message.content.lower():
            await message.channel.send("Hello! How can I help you?")


async def setup(bot):
    await bot.add_cog(PupsCog(bot))
