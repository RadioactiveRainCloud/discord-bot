import discord
from discord.ext import commands

# Contains commands useful to server administration
class AdminCmd(commands.Cog):
    # Initializes the cog
    def __init__(self, bot):
        self.bot = bot;
        print("Loading server administration commands. . .");

# setup command for the cog
def setup(bot):
    bot.add_cog(AdminCmd(bot));
