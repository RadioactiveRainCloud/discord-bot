import discord
from discord.ext import commands
import logging

# Contains commands useful to server administration
class AdminCmd(commands.Cog):
    # Initializes the cog
    def __init__(self, bot):
        self.bot = bot;

    @commands.command()
    async def ban(self,ctx):
        await ctx.send("Haha, you're banned")
        logging.debug("One less retard")

# setup command for the cog
def setup(bot):
    bot.add_cog(AdminCmd(bot));
