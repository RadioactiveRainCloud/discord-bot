import discord
import logging
import os
import sys
from typing import List
import warnings
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path

class DiscordBotError(Exception):
    pass;
class TokenError(DiscordBotError):
    def __init__(self):
        super().__init__("No DISCORD_TOKEN defined in .env file.");
class DotEnvError(DiscordBotError):
    def __init__(self):
        super().__init__(
            ".env file not detected. Look in README.md for instructions on "
            "setting up the environment variables for this discord bot."
        );

# The bot's class definition
class DiscordBot(commands.Bot):
    def __init__(self, command_prefix = "$", embed_color = 0x3498db):
        print("Initializing Discord bot. . .");
        super().__init__(command_prefix);
        self.embed_color = embed_color;
        self.extension_list = self._build_extension_list();
        self._load_extensions(self.extension_list);
        print("Ready for start.");

    # Builds the bot's extension list from the files in /cogs subdirectory.
    def _build_extension_list(self) -> List[str]:
        extension_list = list();
        folder_path = Path("cogs");
        if folder_path.exists() == True:
            # for files ending in .py, format their names and add to the list.
            for item in folder_path.glob("**/*"):
                if item.suffix == ".py":
                    path = item.relative_to(folder_path.parent);
                    ext = str(path).replace("\\", ".")[:-3];
                    print(ext);
                    extension_list.append(ext);
                    print(f"added {ext} to cog list.");
        else:
            warnings.warn("Warning: No cogs folder exists.", UserWarning);
        # Warn us if there were no cogs; bot will be useless.
        if not extension_list:
            warnings.warn("Cogs folder has no .py extensions.", UserWarning);
        return extension_list;

    # Iterates through each extension in extension list.
    def _load_extensions(self,extension_list: List[str]) -> None:
        for ext in extension_list:
            try:
                self.load_extension(ext);
            except commands.errors.ExtensionNotFound:
                print(f"{ext} not found.");
            except commands.errors.ExtensionAlreadyLoaded:
                print(f"{ext} already loaded.");
            except commands.errors.ExtensionFailed:
                print(f"{ext} failed; execution error.");
            except commands.errors.NoEntryPointError:
                print(f"{ext} has not setup function.");
            else:
                print(f"{ext} loaded successfully.");
        return;

    # Loads environment variables and returns the discord token.
    def _load_token(self) -> str:
        # Load token from .env file. Raise error if no token in .env file.
        try:
            if load_dotenv() == False:
                raise DotEnvError;
            token = os.getenv("DISCORD_TOKEN", default = None);
            print("Loaded environment variables from .env");
            if token == None:
                raise TokenError;
            print("Discord token found in environment variables.");
            return token;
        except (TokenError, DotEnvError) as e:
            print(e);
            sys.exit();

    # Command to run the bot.
    def run(self):
        super().run(self._load_token());

    # Reports connection to discord.
    async def on_connect(self):
        print("Successfully connected to discord.");

    # Reports that bot made it online.
    async def on_ready(self):
        print(f"Logged in as {self.user}.");


discord_bot = DiscordBot();
discord_bot.run();
