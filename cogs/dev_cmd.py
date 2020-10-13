import discord
from discord.ext import commands

# Cog used for reloading updated cogs while bot is running
# TODO: must set so only developers can call these commands
class DevCmd(commands.Cog):
    # Initializes the cog.
    def __init__(self, bot):
        self.bot = bot;
        print("Loading developer commands. . .");

    # Command used to trigger a reload. The argument list should include the
    # names of the extensions to reload.
    @commands.command()
    async def reload(self, ctx, *args):
        # Print to the console that a reload was called
        print("Reload called.");
        # Iterate through arguments and reload them if they exist
        for arg in args:
            # Log the arguments in the console
            print(f"Checking if {arg} is present.");
            # Generate the extension name from the argument
            ext = f"cogs.{arg}";
            # Check if the extension is in the bot's extension list
            # Reload if extension exists. Log the result in console
            if ext in self.bot.extension_list:
                self.bot.reload_extension(ext);
                print(f"{ext} reloaded.");
                await ctx.send(f"{ext} reloaded.");
            else:
                print(f"{ext} not found.");

    # Reloads all extensions in bot's extension list.
    @commands.command()
    async def reload_all(self, ctx):
        # Print that all extensions are being reloaded
        print("Reloading all extensions.");
        message = "Reloading. . .\n";
        # Iterate through all extensions in bot's extension list and reload them
        for ext in self.bot.extension_list:
            self.bot.reload_extension(ext);
            print(f"{ext} reloaded.");
            message += f"{ext} reloaded.\n";
        await ctx.send(message);

        #TODO: Set up an exception in event that the extension cannot be found


# setup command for the cog
def setup(bot):
    bot.add_cog(DevCmd(bot));
