import discord
from discord.ext import commands
from discord.ui import Button, View
from main import RoyaltyBot
from utils import MemberOrRoleConverter

# 48h vote
class VoteView(View):
    def __init__(self, bot: RoyaltyBot, description):
        super().__init__()
        self.votes = {"yes": 0, "no": 0}
        self.description = description
        self.bot = bot
        self.bot.pups[self.id] = {}

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        if (self.bot.pups[self.id].get(interaction.user.id) == "yes"):
            await interaction.response.send_message("You have already upvoted!", ephemeral=True)
            return
        elif (self.bot.pups[self.id].get(interaction.user.id) == "no"):
            self.votes["no"] -= 1
        
        self.bot.pups[self.id][interaction.user.id] = "yes"
        self.votes["yes"] += 1
        await interaction.response.edit_message(embed=self.get_vote_embed())

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        if (self.bot.pups[self.id].get(interaction.user.id) == "no"):
            await interaction.response.send_message("You have already downvoted!", ephemeral=True)
            return
        elif (self.bot.pups[self.id].get(interaction.user.id) == "yes"):
            self.votes["yes"] -= 1

        self.bot.pups[self.id][interaction.user.id] = "no"
        self.votes["no"] += 1
        await interaction.response.edit_message(embed=self.get_vote_embed())

    def get_vote_embed(self):
        diff = self.votes["yes"] - self.votes["no"]
        embed = discord.Embed(
            title="Pup Role Vote",
            description=self.description,
            color=discord.Color.blue() if diff == 0 else discord.Color.red() if diff < 0 else discord.Color.green()
        )
        embed.add_field(name="👍 Yes", value=str(self.votes["yes"]), inline=True)
        embed.add_field(name="👎 No", value=str(self.votes["no"]), inline=True)
        return embed


class PupsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pups")
    @commands.has_permissions(administrator = True)
    async def pups(self, ctx: commands.Context, user: MemberOrRoleConverter = None):
        if user is None or not isinstance(user, discord.Member):
            await ctx.send("Please mention a user to create a **Pups** vote")
        else:
            embed = discord.Embed(
                title="Pup Role Vote",
                description=f"Should {user.display_name} have the **Pups** role?",
                color=discord.Color.blue()
            )
            embed.add_field(name="👍 Yes", value="0", inline=True)
            embed.add_field(name="👎 No", value="0", inline=True)
            await ctx.send(embed=embed, view=VoteView(self.bot, f"Should {user.mention} have the **Pups** role?"))
        
        #TODO: add task to event loop

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if "hello bot" in message.content.lower():
            await message.channel.send("Hello! How can I help you?")


async def setup(bot):
    await bot.add_cog(PupsCog(bot))
