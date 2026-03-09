import discord
from discord.ext import commands
from discord import app_commands
from dotenv.cli import get
import embeds
import config

g_id=config.g_id
verified_id = config.verified_id

bot_owner = lambda interaction: interaction.user.id == 1313413062723768322 ## y0l0's discord user ID.

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ping', description="Check the bot's latency")
    @app_commands.guilds(discord.Object(id=g_id))
    @app_commands.checks.has_permissions(administrator=True)
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f'Pong! Latency is {latency}ms.', ephemeral=True)

    @app_commands.command(name='urgentpage', description='For urgently paging a conservation officer. Abuse will lead to moderation.')
    @app_commands.guilds(discord.Object(id=g_id))
    @app_commands.checks.has_role(verified_id)
    async def urgentping(self, interaction: discord.Interaction, reason:str):
         await interaction.response.send_message(
              interaction.user.mention,
              embed= embeds.Pager.sent(),
              ephemeral=True
         )
         co_channel = await self.bot.fetch_channel(config.co_id)
         if co_channel:
             await co_channel.send(
                 content = f"<@&{config.co_role_id}>",
                 embed = embeds.Pager.received(interaction.user, reason),
             )

    @app_commands.command(name = "request_ridealong", description = "Request a ridealong with an FTO")
    @app_commands.guilds(discord.Object(id=g_id))
    @app_commands.checks.has_role(1478572817053253824) #REPLACE WITH DCO role
    async def ridealong(self, interaction: discord.Interaction):
         await interaction.response.send_message(
              interaction.user.mention,
              embed = embeds.Ridealong.sent(),
              ephemeral = True
         )
         sup_channel= await self.bot.fetch_channel(config.sup_id)
         if sup_channel:
              await sup_channel.send(
                   content = f"<@&{config.fto_role_id}>",
                   embed = embeds.Ridealong.received(interaction.user),
                )

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )

async def setup(bot):
    try:
        await bot.add_cog(Utils(bot))
    except Exception as e:
        print("Failed to load Cog: ", e)



