import discord
from discord.ext import commands
import logging


# Contains commands useful to server administration
class AdminCmd(commands.Cog):
    # Initializes the cog
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, target: commands.MemberConverter, *words):
        try:
            reason = " ".join(words)
            deleteMsgDays = 0
            guild = ctx.message.guild
            await guild.ban(target, reason=reason, delete_message_days=deleteMsgDays)
            await ctx.send(str(target) + " banned" + ", Reason: " + reason)
            # TODO logger.debug(str(target)+" banned"+", Reason: "+reason)
        except discord.Forbidden as Forbidden:
            await ctx.send("You do not have permissions to do the actions required.")
        except discord.HTTPException as HTTPException:
            await ctx.send("Banning failed.")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("You did not pass all the required arguments for this command.")
        else:
            pass  # TODO logger.debug("unknown error when running ban command: "+ error)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, target: commands.MemberConverter, amount: int):
        try:
            channel = ctx.message.channel

            def is_target(m):
                return m.author == target

            deleted = await channel.purge(limit=amount, check=is_target)
            await channel.send("Deleted {} message(s)".format(len(deleted)))
            # TODO logger.debug("Successfully deleted {} message(s) from {}".format(len(deleted),target)
        except discord.Forbidden as Forbidden:
            await ctx.send("You do not have permissions to do the actions required.")
        except discord.HTTPException as HTTPException:
            await ctx.send("Purge failed.")

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("You did not pass all the required arguments for this command.")
        else:
            pass  # TODO logger.debug("unknown error when running ban command: "+ error)\


# setup command for the cog
def setup(bot):
    bot.add_cog(AdminCmd(bot))
