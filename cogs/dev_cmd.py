import discord
from discord.ext import commands

# Cog used for reloading updated cogs while bot is running
class DevCmd(commands.Cog):
    # Initializes the cog.
    def __init__(self, bot):
        self.bot = bot;

    # Command used to trigger a reload. The argument list should include the
    # names of the extensions to reload.
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *args):
        # Generate a message to be sent after completion
        message = "Reload called. . .\n";
        # Iterate through arguments and reload them if they exist
        for arg in args:
            # Generate the extension name from the argument
            ext = f"cogs.{arg}";
            # Add the extension reload attempt to the message
            message += f"Reloading {ext}. . .\n"
            # Try to reload the extension; add result to message
            if ext in self.bot._extension_list:
                try:
                    self.bot.reload_extension(ext);
                except commands.errors.ExtensionNotLoaded:
                    message += f"{ext} not loaded.\n";
                except commands.errors.ExtensionNotFound:
                    message += f"{ext} not found.\n";
                except commands.errors.ExtensionFailed:
                    message += f"{ext} failed; execution error.\n";
                except commands.errors.NoEntryPointError:
                    message += f"{ext} has no setup function.\n";
                else:
                    message += f"{ext} reloaded.\n";
            else:
                message += f"{ext} is not in the extension list.\n";
            message += "\n"; # Separate individual attempts for easier reading

        # Notify the user of the results
        print(message);
        await ctx.send(message);

    # Reloads all extensions in bot's extension list.
    @commands.command()
    @commands.is_owner()
    async def reload_all(self, ctx):
        # Generate a message to be sent after completion
        message = "Reloading all extensions. . .\n";
        # Iterate through all extensions in bot's extension list and reload them
        for ext in self.bot._extension_list:
            try:
                self.bot.reload_extension(ext);
            except commands.errors.ExtensionNotLoaded:
                message += f"{ext} not loaded.\n";
            except commands.errors.ExtensionNotFound:
                message += f"{ext} not found.\n";
            except commands.errors.ExtensionFailed:
                message += f"{ext} failed; execution error.\n";
            except commands.errors.NoEntryPointError:
                message += f"{ext} has no setup function.\n";
            else:
                message += f"{ext} reloaded.\n";
        message += "\n"; # Give me space to read

        # Notify the user
        await ctx.send(message);
        print(message);

    # Resets all extensions, rebuilding the extension list from scratch
    @commands.command()
    @commands.is_owner()
    async def reset_all(self, ctx):
        message = """Begin reset of all extensions.
        Unload extensions. . .
        """;
        for ext in self.bot._extension_list:
            try:
                self.bot.unload_extension(ext);
            except commands.errors.ExtensionNotLoaded:
                message += f"{ext} was not loaded\n";
            else:
                message += f"{ext} unloaded successfully\n";
        # Rebuild the extension list from scratch and load the extensions from
        # the generated extension list.

        message += "Rebuilding extension list from scratch. . .\n";
        message += self.bot._build_extensions();

        # Notify the user
        print(message);
        await ctx.send(message);

# setup command for the cog
def setup(bot):
    bot.add_cog(DevCmd(bot));
