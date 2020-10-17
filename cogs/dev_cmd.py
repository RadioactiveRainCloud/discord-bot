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

    # Command used to reload an extension from discord.
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, arg):
        """Reloads a single extension"""
        print(f"Reloading {arg} extension.")
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
        print(msg)
        await ctx.send(msg)

    # Reloads all extensions in bot's extension list.
    @commands.command()
    @commands.is_owner()
    async def reload_all(self, ctx):
        """Reloads all current extensions"""
        print("Reloading all extensions.")
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
        print(msg)
        await ctx.send(msg)

    # Resets all extensions, rebuilding the extension list from scratch
    @commands.command()
    @commands.is_owner()
    async def reset_all(self, ctx):
        """Rebuilds the extension list from scratch"""
        print("Begin reset of all extensions.\nUnloading extensions.\n")
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
        print(msg[:-1])  # The following commands already log messages
        self.bot._build_extension_list()
        self.bot._load_extensions()
        for ext in self.bot.extension_list:
            msg += f"{ext}\n"
        await ctx.send(msg[:-1])


# setup command for the cog
def setup(bot):
    bot.add_cog(DevCmd(bot))
