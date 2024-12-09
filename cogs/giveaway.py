import datetime
import discord
from discord.ext import commands
from discord.ui import Button, View
from main import RoyaltyBot
from random import choice


class GiveawayView(View):
    def __init__(self, bot: RoyaltyBot):
        super().__init__()
        self.members = []
        self.bot = bot
        self.message: discord.Message = None
        self.winner = None

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.members:
            await interaction.response.send_message("You already joined the giveaway!", ephemeral=True)
            return
        
        await interaction.response.send_message("You joined the giveaway!", ephemeral=True)
        self.members.append(interaction.user.id)
    
    async def get_winner(self):
        if self.winner is None:
            self.winner = choice(self.members)
        return await self.message.guild.fetch_member(self.winner)
    
class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveaway")
    async def giveaway(self, ctx: commands.Context, duration: str, *args):
        if not self.bot.has_perms(ctx.author):
            await ctx.send(f"No permissions, you need to be {self.bot.min_role.mention} or higher")
            return
        
        winner_count = 1
        price = ' '.join(args)
        duration_in_seconds = None
        if duration.isdigit():
            duration_in_seconds = int(duration)  
        elif duration.endswith("m") or duration.endswith("M"):
            duration_in_seconds = int(duration[:-1]) * 60
        elif duration.endswith("d") or duration.endswith("D"):
            duration_in_seconds = int(duration[:-1]) * 60 * 60
        
        await ctx.reply(f"The giveaway will last {duration_in_seconds} seconds and have {winner_count} winner(s) and {price} as it's price.", ephemeral=True)
        await ctx.message.delete()
        end = datetime.datetime.now() + datetime.timedelta(seconds=duration_in_seconds)

        embed = discord.Embed(
                title=price,
                description=f"Press  🎉  to enter!\nEnds  <t:{int(end.timestamp())}:R>\nHosted by:  {ctx.author.mention}",
                color=discord.Color.blue(),
                timestamp=end
            )
        embed.set_footer(text="Ends at")

        view = GiveawayView(self.bot)
        msg = await ctx.channel.send("**🎉   GIVEAWAY   🎉**", embed=embed, view=view)
        view.message = msg

        self.bot.add_giveaway(end, view)


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
