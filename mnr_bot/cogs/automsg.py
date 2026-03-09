import discord
from discord.ext import commands
from config import gen_id, tick_id

EMBED_COLOR = 0x2e352d

class Automsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        general_channel = guild.get_channel(gen_id)
        if general_channel is None:
            print("General channel not found")
            return
        
        help_channel = guild.get_channel(tick_id)
        if help_channel is None:
            print("Help channel not found")
            return
        
        welcome_embed = discord.Embed(
            title=f"Welcome {member.display_name}!",
            description=f"Welcome to the Ministry of Natural resources, {member}. If you require assistance, please open a ticket by running ``/ticket create``.",
            color=EMBED_COLOR)
        await general_channel.send(member.mention, embed=welcome_embed) 

        

async def setup(bot):
    await bot.add_cog(Automsg(bot))