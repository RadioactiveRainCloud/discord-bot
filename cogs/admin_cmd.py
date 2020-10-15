import discord
from discord.ext import commands
import logging

# Contains commands useful to server administration
class AdminCmd(commands.Cog):
    # Initializes the cog
    def __init__(self, bot):
        self.bot = bot
        logger = logging.getLogger(name = "cogs.admin")
        logger.setLevel(logging.DEBUG)

        fileHandler = logging.FileHandler("discord_bot.log")
        fileHandler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)

    @commands.command()
    async def ban(self,ctx,target: commands.MemberConverter,*words):
        
        try:
            reason = " ".join(words)
            deleteMsgDays = 0
            guild = ctx.message.guild
            await guild.ban(target, reason=reason, delete_message_days=deleteMsgDays)
            await ctx.send(str(target)+" banned"+", Reason: "+reason)
            logging.getLogger("cogs.admin").debug(str(target)+" banned"+", Reason: "+reason)
            pass
        except discord.Forbidden as Forbidden:
            await ctx.send("You are not allowed to use this command."+ str(Forbidden))
            pass

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("You forgot one of the required arguments.")
        else: 
            logging.getLogger("cogs.admin").debug("unknown error when running ban command: "+ error)


# setup command for the cog
def setup(bot):
    bot.add_cog(AdminCmd(bot));
