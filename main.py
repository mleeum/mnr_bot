import discord
from discord import message
from discord import guild
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
import config

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

if token is None:
    raise ValueError("DISCORD_TOKEN environment variable not set")
handler = logging.FileHandler(
    filename='discord.log', 
    encoding='utf-8', 
    mode='w'
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Client(commands.Bot):
    async def setup_hook(self):
        cogs_to_load = ["utils", "automsg", "ticketing"]

        for cog in cogs_to_load:
            await self.load_extension(f"cogs.{cog}")

        guild = discord.Object(id=config.g_id)
        synced = await self.tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to guild {guild.id}.")

    async def on_ready(self):
        print(f'Logged in as {self.user}') 



client = Client(command_prefix="m!", intents=intents)

@client.command(name="sync")
@commands.is_owner() # Ensures only the bot owner can use this command
async def sync(ctx: commands.Context) -> None:
    """Syncs all global application commands to Discord."""
    await client.tree.sync()
    await ctx.send("Application commands synchronized globally!", ephemeral = True)

client.run(token, log_handler=handler, log_level=logging.INFO)
