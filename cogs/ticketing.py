import discord
from discord.ext import commands
from discord import ui, app_commands, utils
import config
import asyncio

import traceback
g_id=config.g_id
verified_id = config.verified_id
category_id = 1479252078139408468
EMBED_COLOUR = 0x2e352d

bot_owner = lambda interaction: interaction.user.id == 1313413062723768322

###

class Ticket(ui.Modal, title = "Open a new support ticket"):
      date = ui.Label( 
           text = "Date of Incident",
           description = "If not applicable, type N/A",
           component = ui.TextInput(placeholder = "Please enter a date in DD/MM/YYYY format",
                required = True,
                style = discord.TextStyle.short,
                max_length = 10,
                custom_id = "incident_date"
                )
            )
      type = ui.Label(
          text = "Ticket Type",
          component = ui.Select(
              required = True,
              placeholder = "Select a ticket type...",
              options =[
                  discord.SelectOption(label = "CO Report", description = "Report a Conservation Officer.", emoji="⚠️"),
                  discord.SelectOption(label = "Tip Line", description = "Report the abuse or concerns of natural resources or wildlife.", emoji="🚨"),
                  discord.SelectOption(label = "General Support", description = "Get in touch with a Conservation Officer for any questions you may have.", emoji="🔖")
              ],
              custom_id = "type",
          )
      )
      reason = ui.Label(
            text = "Your questions, concerns or tips",
            component = ui.TextInput(
                placeholder = "Please provide as much detail as possible so we can help you to the best of our ability.",
                required =  True,
                style = discord.TextStyle.paragraph,
                max_length = 250,
                custom_id = "user_reason"
            )
         )
      warning = ui.TextDisplay("Please note, you will not be able to open more than 1 ticket at a time.")
      
      def type_check(self, interaction: discord.Interaction):
          assert isinstance(self.date.component, discord.ui.TextInput)
          assert isinstance(self.type.component, discord.ui.Select)
          assert isinstance(self.reason.component, discord.ui.TextInput)

        
      async def on_submit(self, interaction: discord.Interaction):
        date_input = self.date.component.value #type: ignore
        type_input = self.type.component.values[0] #type: ignore
        reason_input = self.reason.component.value #type: ignore
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "This ticket system can only be used in a server.",
                ephemeral=True
            )
            return

        # Get the category object
        category = guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "Ticket category not found. Please contact staff.",
                ephemeral=True
            )
            return

        # Prevent duplicate tickets
        existing = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name}") or discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name}-claimed")
        if existing:
            await interaction.response.send_message(
                f"You already have a ticket: {existing.mention}",
                ephemeral=True
            )
            return

        # Set channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Create the ticket channel
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            category=category
        )

        # Send initial message in ticket channel
        init_message = await ticket_channel.send(f"{interaction.user.mention} <@&{config.co_role_id}>",embed =
                                  discord.Embed(
                                      title = f"Ticket opened by: {interaction.user.name}",
                                      description = f"**Date of Incident:** {date_input}\n"
                                      f"**Ticket Type:** {type_input}\n"
                                      f"**Ticket Details:** {reason_input}",
                                      color = EMBED_COLOUR
                                  ))
        await init_message.pin()
        
   
        

        # Confirm to the user
        await interaction.response.send_message(
            f"Your ticket has been created: {ticket_channel.mention}",
            ephemeral=True
        )

   


@app_commands.guild_only
@app_commands.guilds(discord.Object(id = g_id))
@app_commands.checks.has_role(verified_id)
class Tickets(commands.GroupCog, group_name="ticket", description="Ticket commands"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='create', description="Create a new ticket")


    async def create(self, interaction: discord.Interaction):
        modal = Ticket()
        await interaction.response.send_modal(modal)

    @staticmethod
    def in_tick_category():
        async def predicate(interaction: discord.Interaction) -> bool:
            if interaction.guild is None:
                return False
            channel = interaction.channel
            if isinstance(channel, discord.TextChannel) and channel.category_id == category_id:
                return True
            if isinstance(channel, discord.TextChannel) and channel.category_id != category_id:
                await interaction.response.send_message(content = "You can't use this command here!", ephemeral = True)
                return False
            return False
        return app_commands.check(predicate)

    
    @app_commands.command(name="close", description="Closes the current ticket.")
    @app_commands.checks.has_role(config.co_role_id)
    @in_tick_category()
    async def ticket_close(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        if guild is None:
            await interaction.followup.send("Cannot be used in DMs!", ephemeral=True)
            return
        
       
        role = guild.get_role(1478219570069246093) ## MNR Employee role ID
        if role is None:
            await interaction.followup.send("Staff role not assigned", ephemeral=True)
            return
       
        ticket_channel = interaction.channel
        if not isinstance(ticket_channel, discord.TextChannel):
            await interaction.followup.send("This command can only be used in a text channel.", ephemeral=True)
            return

        count = 0
        for member in ticket_channel.members:
            if role not in member.roles and not member.bot:
                await ticket_channel.set_permissions(member, read_messages=False)
                count += 1
        
        await interaction.followup.send(f"Ticket has been closed, {count} users removed from ticket.", ephemeral = False)

    
    @app_commands.command(name = "claim", description = "Claims the current ticket")
    @app_commands.checks.has_role(config.co_role_id)
    @in_tick_category()
    async def claim(self, interaction: discord.Interaction):
        if interaction.channel is not None and isinstance(interaction.channel, discord.TextChannel):
            await interaction.channel.edit(name = f"{interaction.channel.name}-claimed")
            await interaction.response.send_message(f"**Ticket claimed by:** {interaction.user.mention}")
            msg = await interaction.original_response()
            await msg.pin()



    @app_commands.command(name = "delete", description = "Delete's the current ticket, cannot be undone.")
    @app_commands.checks.has_role(config.fto_role_id)
    @in_tick_category()
    async def delete(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.TextChannel):
            return await interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)

        await interaction.response.send_message("Are you sure you want to delete the ticket? Type **y** to confirm or **n** to cancel.", ephemeral=True)
        def check(m: discord.Message):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.lower() in ('yes', 'y', 'no', 'n')
        try:
            response_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        
            if response_message.content.lower() in ('yes', 'y'):
                try:
                    await interaction.channel.delete()
                except discord.Forbidden:
                    await interaction.followup.send("Error, please contact system administrator.", ephemeral=True) # Check bot perms if returns with this message
            else:
                await interaction.followup.send("Deletion canceled.", ephemeral=True)

        except asyncio.TimeoutError:
            await interaction.followup.send("Confirmation timed out. No action taken.", ephemeral=True)
    
    @app_commands.command(name = "add", description = "Add a user to the current ticket.")
    @app_commands.checks.has_role(config.co_role_id)
    @in_tick_category()
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.channel, discord.TextChannel):
              return interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)
        await interaction.channel.set_permissions(
            user,
            read_messages=True,
            send_messages=True,
            view_channel=True,
            read_message_history=True
        )
        await interaction.response.send_message(f"{user.mention} has been added to the ticket.")

    @app_commands.command(name = "remove", description = "Remove a user from the current ticket.")
    @app_commands.checks.has_role(config.co_role_id)
    @in_tick_category()
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.channel, discord.TextChannel):
              return interaction.response.send_message("This command can only be used in text channels.", ephemeral=True)
        await interaction.channel.set_permissions(
            user,
            read_messages=False,
            send_messages=False,
            view_channel=False,
            read_message_history=False
        )
        await interaction.response.send_message(f"{user.mention} has been removed from the ticket.")
    
    

   
async def setup(bot: commands.Bot) -> None:
    try:
        await bot.add_cog(Tickets(bot))
    except Exception as e:
        print(f"Failed to load ticketing cog: {e}")



