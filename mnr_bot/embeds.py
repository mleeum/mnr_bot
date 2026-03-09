import discord

EMBED_COLOUR = 0x2e352d
# pager 
class Pager:
     
     @staticmethod
     def sent():
         return discord.Embed(
        title = "Page has been sent!",
        description = "Your page has been sent to conservation officers, one will respond shortly.",
        color = EMBED_COLOUR,
        )
     
     @staticmethod
     def received(user, reason):
      return discord.Embed(
          title = "Urgent page recieved!",
          description = (
              f"{user.mention} has paged for a conservation officer response.\n"
              f"Reason: {reason}"
              ),
          colour = EMBED_COLOUR
          )
     
# Ridealong
class Ridealong:

    @staticmethod
    def sent():
        return discord.Embed(
            title = f"Ridealong Request Sent!",
            description = f"Your ridealong request has been sent to an FTO,\n if one is available, you will be contacted shortly.",
            color = EMBED_COLOUR)
    
    
    @staticmethod
    def received(user):
     return discord.Embed(
          title = "Ridealong Request Recieved!",
          description = f"{user.mention} has requested a ridealong with an FTO.",
          colour = EMBED_COLOUR,
     )
