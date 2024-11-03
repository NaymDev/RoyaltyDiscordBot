import datetime
from discord import app_commands
import discord
from discord.ext import commands

from utils import Gamemode, Proxy

class ApproveButton(discord.ui.Button):
        def __init__(self, bot, view):
            super().__init__(label="Approve", style=discord.ButtonStyle.primary)
            self.bot = bot
            self.sub_view = view

        async def callback(self, interaction: discord.Interaction):
            if any(role in self.bot.ROLES_STAFF for role in interaction.user.roles):
                await interaction.response.send_message(
                    f"Bounty approved by {interaction.user.mention}."
                )
                # Notify the user of bounty approval
                await self.user.send(f"Your bounty on {self.bounty_channel.name} has been approved.")
                # Delete the channel after approval
                await self.bounty_channel.delete(reason="Bounty approved")

                for item in self.sub_view.children:
                    if isinstance(item, discord.ui.Button):
                            item.disabled = True
                await self.sub_view.message.edit(view=self.sub_view)
                self.sub_view.stop()
            await interaction.response.send_message(
                    "You cannot apporve submissions!",
                    ephemeral=True
                )

class ApprovalView(discord.ui.View):
    def __init__(self, user: discord.Member, bounty_channel: discord.TextChannel, bot, view):
        super().__init__(timeout=None)
        self.user = user
        self.bounty_channel = bounty_channel
        self.add_item(ApproveButton(bot, view))
    
class BountyCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    group = app_commands.Group(name="bounty", description="...")

    @group.command(name="host", description="Host a new bounty")
    @app_commands.describe(
        in_game_name="Targets in-game name",
        proxy="Select the proxy",
        gamemode="Choose the game mode"
    )
    async def bounty_host(self, interaction: discord.Interaction,
                          in_game_name: str,
                          proxy: Proxy,
                          gamemode: Gamemode):
        embed = discord.Embed(title="🎯 New Bounty Posted!", color=discord.Color.red())
        embed.add_field(name="Target In-Game Name", value=in_game_name, inline=False)
        embed.add_field(name="Proxy", value=proxy.value, inline=True)
        embed.add_field(name="Gamemode", value=gamemode.value, inline=True)
        embed.set_footer(text="Press submit once you have eliminated the target.")
        
        class SubmitView(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=None)
                self.button = SubmitButton(bot)
                self.add_item(self.button)
        
        class SubmitButton(discord.ui.Button):
            def __init__(self, bot):
                super().__init__(label="Submit", style=discord.ButtonStyle.success)
                self.bot = bot
                self.om: discord.InteractionMessage = None
            
            async def callback(self, interaction: discord.Interaction):
                # Create a new private channel for the user and staff
                guild = interaction.guild
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True),
                    **{role: discord.PermissionOverwrite(view_channel=True) for role in self.bot.ROLES_STAFF},
                }
                bounty_channel = await guild.create_text_channel(
                    name=f"bounty-{interaction.user.name}",
                    overwrites=overwrites,
                    reason="Bounty submission channel"
                )
                
                # Send a confirmation message in the new private channel
                await bounty_channel.send(
                    content=f"{interaction.user.mention} claims to have eliminated {in_game_name}!\n{self.om.jump_url}\nSubmitted at: <t:{int(datetime.datetime.now().timestamp())}:R>",
                    view=ApprovalView(interaction.user, bounty_channel, self.bot, self.view)
                )
                await interaction.response.send_message(
                    content="A private channel has been created for staff to review your submission.",
                    ephemeral=True
                )
        
        # Respond with the initial message and the submit button view
        v = SubmitView(self.bot)
        await interaction.response.send_message(embed=embed, view=v)
        message: discord.InteractionMessage = await interaction.original_response()
        v.button.om = message

       
    
    @commands.command(name="sync")
    @commands.has_permissions(administrator = True)
    async def sync(self, ctx: commands.Context):
        synced = await self.bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        


async def setup(bot):
    try:
        await bot.add_cog(BountyCog(bot))
    except Exception:
        pass
