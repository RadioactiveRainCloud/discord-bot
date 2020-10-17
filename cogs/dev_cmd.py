import discord
from discord.ext.commands.errors import (
    ExtensionNotLoaded,
    ExtensionNotFound,
    ExtensionFailed,
    NoEntryPointError
)
from discord.ext import commands


# Cog used for reloading updated cogs while bot is running
class DevCmd(commands.Cog):
    # Initializes the cog.
    def __init__(self, bot):
        self.bot = bot
        return

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, arg):
        """Reloads a single extension"""
        self.bot.warning(f"Reloading {arg} extension.")
        msg = ""
        # Search extension list for the argument
        for ext in self.bot.extension_list:
            if ext.endswith(arg):
                try:
                    self.bot.reload_extension(ext)
                except (ExtensionNotLoaded, ExtensionNotFound,
                        ExtensionFailed, NoEntryPointError) as e:
                    msg = f"In {ext}:\n{e}"
                else:
                    msg = f"{ext} successfully reloaded."
                finally:
                    break
        else:  # No break statement happened --> arg wasn't in extension list
            msg = f"{arg} was not found in the loaded extension list."
        self.bot.info(msg)
        await ctx.send(msg)
        return

    @commands.command()
    @commands.is_owner()
    async def reload_all(self, ctx):
        """Reloads all currentl running extensions"""
        self.bot.warning("Reloading all extensions.")
        msg = ""
        # Iterate through all extensions in bot's extension list and reload them
        for ext in self.bot.extension_list:
            try:
                self.bot.reload_extension(ext)
            except (ExtensionNotLoaded, ExtensionNotFound,
                    ExtensionFailed, NoEntryPointError) as e:
                msg += f"In {ext}:\n{e}\n"
            else:
                msg += f"{ext} reloaded.\n"
        msg = msg[:-1]  # get rid of trailing newline
        self.bot.info(msg)
        await ctx.send(msg)
        return

    @commands.command()
    @commands.is_owner()
    async def reset_all(self, ctx):
        """Rebuilds the extension list from scratch"""
        self.bot.warning(
            "Begin reset of all extensions. Unloading extensions.")
        msg = ""
        for ext in self.bot.extension_list:
            try:
                self.bot.unload_extension(ext)
            except ExtensionNotLoaded as e:
                msg += f"{e}\n"
        self.bot.extension_list.clear()
        # Rebuild the extension list from scratch and load the extensions from
        # the generated extension list.
        msg += "Rebuilding extension list from scratch.\n"
        self.bot.info(msg[:-1])  # The following commands already log messages
        self.bot._build_extension_list()
        self.bot._load_extensions()
        for ext in self.bot.extension_list:
            msg += f"{ext}\n"
        await ctx.send(msg[:-1])
        return

    @commands.command()
    @commands.is_owner()
    async def test_logs(self, ctx):
        """Generates test entries in the logs"""
        self.bot.debug("TESTING TESTING TESTING")
        self.bot.info("This is a test message.")
        self.bot.warning("This is a warning, but we're still fine.")
        self.bot.error("Error, uh it's getting spicy in here.")
        self.bot.critical("Critical, shit has hit all of the fans.")
        try:
            assert False
        except AssertionError as e:
            self.bot.exception(e)
        self.bot.warning("End of test.")
        await ctx.send("Test completed. Check the logs.")
        return


# setup command for the cog
def setup(bot):
    bot.add_cog(DevCmd(bot))
    return
