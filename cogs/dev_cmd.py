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

    def __reload_extension(self, extension: str) -> str:
        """Helper function that reloads the given extension. Returns a string
        with info about whether the extension reloaded properly or not."""
        try:
            self.bot.reload_extension(extension)
        except (ExtensionNotLoaded, ExtensionNotFound,
                ExtensionFailed, NoEntryPointError) as error:
            msg = f"For {extension}:\n{error}"
        else:
            msg = f"{extension} successfully reloaded."
        return msg

    def __unload_extension(self, extension: str) -> str:
        """Helper function that unloads the given extension. Returns a string
        with info about whether the extension unloaded properly or not."""
        try:
            self.bot.unload_extension(extension)
        except ExtensionNotLoaded as error:
            msg = f"{error}"
        else:
            msg = f"{extension} successfully unloaded."
        return msg

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, arg):
        """Reloads a single extension"""
        self.bot.warning(f"Reloading {arg} extension.")
        # Search extension list for the argument
        for extension in self.bot.extensions.keys():
            if extension.endswith(arg):
                msg = self.__reload_extension(extension)
                break
        else:  # No break statement happened --> arg wasn't in extension list
            msg = f"{arg} was not found in the loaded extension list."
        self.bot.info(msg)
        await ctx.send(msg)
        return

    @commands.command()
    @commands.is_owner()
    async def reload_all(self, ctx):
        """Reloads all currently running extensions"""
        self.bot.warning("Reloading all extensions.")
        msg = ""
        # Iterate through all extensions in bot's extension list and reload them
        extension_list = list(self.bot.extensions.keys())
        for extension in extension_list:
            msg += self.__reload_extension(extension) + "\n"
        msg = msg[:-1]  # get rid of trailing newline
        self.bot.info(msg)
        await ctx.send(msg)
        return

    @commands.command()
    @commands.is_owner()
    async def reset_all(self, ctx):
        """Rebuilds the extension list from scratch"""
        self.bot.warning("Begin reset of all extensions.")
        msg = ""
        while len(self.bot.extensions) > 0:
            msg += self.__unload_extension(next(iter(self.bot.extensions)))
            msg += "\n"
        # Reset the extensions
        self.bot.load_all_extensions()
        for extension in self.bot.extensions.keys():
            msg += f"{extension} loaded.\n"
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
        self.bot.warning("END OF TEST")
        await ctx.send("Test completed. Check the logs.")
        return

    @commands.command()
    @commands.is_owner()
    async def test_message(self, ctx, length=2500):
        """Generates a test message of given length up to 25000 characters"""
        length = min(length, 25000)
        msg = ""
        for character in range(length):
            msg += str(character % 10)
        await self.bot.send_message(ctx, msg)
        return


# setup command for the cog
def setup(bot):
    bot.add_cog(DevCmd(bot))
    return
