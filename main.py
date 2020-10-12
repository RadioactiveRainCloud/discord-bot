import discord
import logging
import os
from dotenv import load_dotenv
from discord.ext import commands

# The bot's class definition
class DiscordBot(commands.Bot):
    def __init__(self):
        print("Initializing Discord bot. . .");
        # Set up list of cogs. Is there a way to load a list from .env?
        # TODO: find cleaner way to load this list instead of keeping it
        # hard coded
        self.extension_list = [
        "cogs.admin_cmd",
        "cogs.crypto_cmd",
        "cogs.dev_cmd"
        ];

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

        # Iterate through extension list and load each extension
        for extension in self.extension_list:
            self.load_extension(extension);

    # Loads the token from .env and runs the bot. Use this method vice run()
    # TODO: figure out how to properly override the run() method.
    def start_up(self):
        print("Running the bot. . .");
        # Load token from .env
        token = os.getenv("DISCORD_TOKEN", default = None);
        # Ensure token exists and run the bot. If token does not exist,bot will
        # not enter the event loop and program will continue.
        if token != None:
            self.run(token);
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

discord_bot.start_up();
