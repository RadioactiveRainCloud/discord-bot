import discord
from discord.ext import commands
import logging
import typing


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
            pass #TODO logger.debug("unknown error when running ban command: "+ error)

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def purge(self,ctx,target: typing.Optional[discord.Member] = None, limit: int = 0):
        """
        target: The member who's messages you want to delete (optional)
        limit: the amount of messages to search through
        """
        try:
            # Delete the message that calls this command
            await ctx.message.delete()

            msg = []
            channel = ctx.channel

            if target == None:
                await ctx.channel.purge(limit=limit)
                return await ctx.send(f"Purged {limit} messages", delete_after=3)
            
            if limit == 0: 
                return await ctx.send("You did not specify the amount.", delete_after=5)
            
            async for m in channel.history():
                if len(msg) == limit:
                    # End of loop condition
                    break
                if m.author == target:
                    # Keep adding messages authored by this member until end of loop condition
                    msg.append(m)
            await ctx.channel.delete_messages(msg)
            await ctx.send(f"Deleted {limit} message(s) of {target.mention}", delete_after=3)
            #TODO logger.debug("Successfully deleted {} message(s) from {}".format(len(deleted),target)
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
