import random
import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime, timedelta

# Ϣσμ ηαβε βεεν ϖαρνεδ.
class NotifyView(View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.members = []
        self.message: discord.Message = None
    
    @discord.ui.button(label="🏆", style=discord.ButtonStyle.green)
    async def notify_button(self, interaction: discord.Interaction, button: Button):
        self.members.append(interaction.user)
        await interaction.response.send_message("You will get notified 10 Minutes before the tournament starts.", ephemeral=True)

class TournyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tournament")
    @commands.has_permissions(administrator = True)
    async def tournament(self, ctx: commands.Context, tournament_day: str = None, tournament_time: str = None):
        try:
            if (not tournament_time or not tournament_day): 
                raise ValueError("Tournament time is not set.")
            print(tournament_day + " " + tournament_time)

            TOURNAMENT_TIME = datetime.strptime(tournament_day + " " + tournament_time, '%Y-%m-%d %H:%M')
            tournament_timestamp = int(TOURNAMENT_TIME.timestamp())

            embed = discord.Embed(
                title="Upcoming Tournament",
                description="Get notified when the tournament starts!",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Start Time",
                value=f"<t:{tournament_timestamp}:F> (<t:{tournament_timestamp}:R>)"
            )

            view = NotifyView(self.bot)
            msg = await ctx.send(embed=embed, view=view)
            self.bot.add_notification(TOURNAMENT_TIME - timedelta(minutes=10), view, msg)
            view.message = msg

        except ValueError:
            await ctx.send("Please enter the date in the format `YYYY-MM-DD HH:MM`.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TournyCog(bot))
