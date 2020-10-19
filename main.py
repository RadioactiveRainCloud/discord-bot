import discord
import logging
import os
import sys
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands.errors import (
    ExtensionNotFound,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    NoEntryPointError)
from pathlib import Path


# Error: base class
class DiscordBotError(Exception):
    pass


# Error: Can't find the token.
class TokenError(DiscordBotError):
    def __init__(self):
        super().__init__("No DISCORD_TOKEN defined in .env file.")


# Error: Can't find the .env file
class DotEnvError(DiscordBotError):
    def __init__(self):
        super().__init__(
            ".env file not detected. Look in README.md for instructions on "
            "setting up the environment variables for this discord bot."
        )


# The bot's class definition
class DiscordBot(commands.Bot):
    def __init__(self, command_prefix="$", embed_color=0x3498db,
                 log_file="discord_bot.log"):
        # Make the logger first.
        self.logger = None
        self._make_logger(log_file)
        self.debug("Discord bot initializing.")
        super().__init__(command_prefix)
        self.embed_color = embed_color
        self._load_extensions()
        return

    # Builds the bot's extension list from the files in /cogs subdirectory.
    def _load_extensions(self) -> None:
        folder_path = Path("cogs")
        if folder_path.exists():
            # for files ending in .py, format their names and add to the list.
            for item in folder_path.glob("**/*"):
                if item.suffix == ".py":
                    path = item.relative_to(folder_path.parent)
                    ext = str(path).replace("\\", ".")[:-3]
                    try:
                        self.load_extension(ext)
                    except (ExtensionNotFound, ExtensionAlreadyLoaded,
                            ExtensionFailed, NoEntryPointError) as e:
                        self.exception(f"In {ext}:\n{e}")
                    else:
                        self.info(f"{ext} loaded successfully.")
        else:
            self.warning("No cogs folder exists.")
        # Warn us if there were no cogs; bot will be useless.
        if not self.extensions:
            self.warning("No extensions were loaded.")
        return

    # Loads environment variables and returns the discord token.
    def _load_token(self) -> str:
        # Load token from .env file. Raise error if no token in .env file.
        try:
            if not load_dotenv():
                raise DotEnvError
            token = os.getenv("DISCORD_TOKEN")
            self.info("Loaded environment variable(s) from .env")
            if token is None:
                raise TokenError
            self.info("Discord token found in environment variables.")
            return token
        except (TokenError, DotEnvError) as e:
            self.exception(e)
            sys.exit()

    # Creates a logger object for the bot to log itself
    def _make_logger(self, log_file: str, verbose=False) -> None:
        # Create the logger object
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Set stream handler for console output
        streamHandler = logging.StreamHandler()
        if not verbose:
            streamHandler.setLevel(logging.WARNING)
        format_str = ">>%(levelname)s:\t%(message)s"
        formatter = logging.Formatter(format_str)
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)
        # Set file handler for .log file
        fileHandler = logging.FileHandler(log_file)
        format_str = "%(asctime)s:%(name)s:%(levelname)s:\n\t%(message)s\n"
        formatter = logging.Formatter(format_str)
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
        return

    # Command to run the bot.
    def run(self) -> None:
        super().run(self._load_token())
        return

    # Used to generate logger debug message
    def debug(self, msg: str) -> None:
        self.logger.debug(msg)
        return

    # Used to generate logger info message
    def info(self, msg: str) -> None:
        self.logger.info(msg)
        return

    # Used to generate logger warning message
    def warning(self, msg: str) -> None:
        self.logger.warning(msg)
        return

    # Used to generate logger error message
    def error(self, msg: str) -> None:
        self.logger.error(msg)
        return

    # Used to generate logger critical message
    def critical(self, msg: str) -> None:
        self.logger.critical(msg)
        return

    # Used to generate logger exception message
    def exception(self, msg: str) -> None:
        self.logger.exception(msg)
        return

    # Reports connection to discord.
    async def on_connect(self):
        self.info("Successfully connected to discord.")
        return

    # Reports that bot made it online.
    async def on_ready(self):
        msg = f"Logged in as {self.user}."
        self.info(msg)
        print(msg)
        return


# Program entry point
def main() -> None:
    OpenBot = DiscordBot()
    OpenBot.run()
    return


if __name__ == "__main__":
    main()
