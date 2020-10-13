import discord
import logging
import os
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path

# The bot's class definition
class DiscordBot(commands.Bot):
    def __init__(self):
        print("Initializing Discord bot. . .");
        # Prompts user to look up information on setting up .env file in README
        dotenv_errormessage = """
        Initialization Error:
        .env file not detected. Look in README.md for instructions on setting up
        the environment variables for this discord bot.
        """;
        # Set up environment variables
        assert load_dotenv() == True, dotenv_errormessage;
        command_prefix = os.getenv("COMMAND_PREFIX", default = "$");
        log_file = os.getenv("LOG_FILE", default = "discord_bot.log");
        # Set bot's embed color. Default value is discord.Colour.blue()
        embed_color = os.getenv("EMBED_COLOR", default = "0x3498db");
        self._embed_color = int(embed_color, 0); # Hex string to int value

        # Set up the logger. Can I move this into a cog later?
        # TODO: figure out how logging works
        self.logger = logging.getLogger("discord_bot");
        self.logger.setLevel(logging.DEBUG);
        handler = logging.FileHandler(
        filename = log_file,
        encoding = "utf-8",
        mode = "w");
        format = "%(asctime)s:%(levelname)s:%(name)s: %(message)s";
        handler.setFormatter(logging.Formatter(format));
        self.logger.addHandler(handler);

        # Initialize the base class. Must be done BEFORE trying to load
        # extensions. load_extension() won't work without base class initialized
        super().__init__(command_prefix);

        # Create self._extension_list and load extensions from the list
        msg = self._build_extensions();
        print(msg);

    # Builds the bot's extension list.
    def _build_extensions(self) -> str:
        # Generate a message for the logs
        message = "";
        # Create/clear out the extension list
        self._extension_list = [];
        # Create a folder path to the cogs folder
        folder_path = Path("cogs");
        # Verify the cogs folder exists. Issue warning otherwise
        if folder_path.exists() == True:
            # Add each item name in the cogs folder to the list if it is a file
            for item in folder_path.glob("**/*"):
                if item.suffix == ".py":
                    path = item.relative_to(item.parents[1]);
                    ext = str(path).replace("\\", ".")[:-3];
                    self._extension_list.append(ext);
                    message += f"added {ext} to cog list.\n";
        else:
            message += "Warning: No cogs folder exists.\n";
        # Warn us if there were no cogs; bot will be useless
        if not self._extension_list:
            message += "Warning: Cogs folder has no extensions inside of it.\n";
        # Extension list should be created
        # Iterate through each extension in extension list.
        for ext in self._extension_list:
            try:
                self.load_extension(ext);
            except commands.errors.ExtensionNotFound:
                message += f"{ext} not found.\n";
            except commands.errors.ExtensionAlreadyLoaded:
                message += f"{ext} already loaded.\n";
            except commands.errors.ExtensionFailed:
                message += f"{ext} failed; execution error.\n";
            except commands.errors.NoEntryPointError:
                message += f"{ext} has not setup function.\n";
            else:
                message += f"{ext} loaded successfully.\n";
        # Return the generated message
        return message;

    # Loads the token from .env and runs the bot. Use this method vice run()
    def run(self):
        print("Running the bot. . .");
        # Load token from .env
        token = os.getenv("DISCORD_TOKEN", default = None);
        # Ensure token exists and run the bot. If token does not exist,bot will
        # not enter the event loop and program will continue.
        if token != None:
            super().run(token);
        else:
            print("StartUp Error: DISCORD_TOKEN not found in .env file.");

    # Reports connection to discord.
    async def on_connect(self):
        # Report successful connection.
        print("Successfully connected to discord.");

    # Reports that Mercury made it online.
    async def on_ready(self):
        print(f"Logged in as {self.user}.");

discord_bot = DiscordBot();

discord_bot.run();
