import discord
import logging
import os
import sys
from typing import List
import warnings
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
        print("Initializing Discord bot. . .")
        super().__init__(command_prefix)
        self.embed_color = embed_color
        self.extension_list = list()
        self._build_extension_list()
        self._load_extensions()
        return

    # Builds the bot's extension list from the files in /cogs subdirectory.
    def _build_extension_list(self) -> None:
        folder_path = Path("cogs")
        if folder_path.exists():
            # for files ending in .py, format their names and add to the list.
            for item in folder_path.glob("**/*"):
                if item.suffix == ".py":
                    path = item.relative_to(folder_path.parent)
                    ext = str(path).replace("\\", ".")[:-3]
                    print(ext)
                    self.extension_list.append(ext)
                    print(f"added {ext} to extension list.")
        else:
            warnings.warn("Warning: No cogs folder exists.", UserWarning)
        # Warn us if there were no cogs; bot will be useless.
        if not self.extension_list:
            warnings.warn("Cogs folder has no .py extensions.", UserWarning)
        return

    # Iterates through each extension in extension list.
    def _load_extensions(self) -> None:
        for ext in self.extension_list:
            try:
                self.load_extension(ext)
            except (ExtensionNotFound, ExtensionAlreadyLoaded,
                    ExtensionFailed, NoEntryPointError) as e:
                print(f"In {ext}:\n{e}")
            else:
                print(f"{ext} loaded successfully.")
        return

    # Loads environment variables and returns the discord token.
    def _load_token(self) -> str:
        # Load token from .env file. Raise error if no token in .env file.
        try:
            if not load_dotenv():
                raise DotEnvError
            token = os.getenv("DISCORD_TOKEN")
            print("Loaded environment variables from .env")
            if token is None:
                raise TokenError
            print("Discord token found in environment variables.")
            return token
        except (TokenError, DotEnvError) as e:
            print(e)
            sys.exit()
        return

    def _make_logger(self, log_file: str) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.NOTSET)
        fileHandler = logging.FileHandler(log_file)
        fileHandler.setLevel(logging.DEBUG)
        format_str = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
        formatter = logging.Formatter(format_str)
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)
        return

    # Command to run the bot.
    def run(self) -> None:
        super().run(self._load_token())
        return

    # Reports connection to discord.
    async def on_connect(self):
        print("Successfully connected to discord.")
        return

    # Reports that bot made it online.
    async def on_ready(self):
        print(f"Logged in as {self.user}.")
        return


# Program entry point
def main() -> None:
    OpenBot = DiscordBot()
    OpenBot.run()
    return


if __name__ == "__main__":
    main()
