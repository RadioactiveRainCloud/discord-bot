import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from atexit import register
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext.commands.errors import (
    ExtensionNotFound,
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    NoEntryPointError
)


class DiscordBot(commands.Bot):
    def __init__(self, command_prefix="$"):
        self.__make_logger(verbose=True)
        self.info("Initializing the DiscordBot.")
        super().__init__(command_prefix)
        self.__load_database()
        # embed color handling will be changed when send_embed() is implemented
        self.embed_color = discord.Color.blue()
        self.load_all_extensions()
        return

    def __make_logger(self, filename="bot.log", verbose=False) -> None:
        """Creates a logger with a queue handler and a queue listener. Other
        handlers are added as desired. This allows the addition of blocking
        handlers to be handled in their own thread."""
        # Set logging level based on whether verbose is set or not
        logging_level = logging.DEBUG if verbose else logging.WARNING
        # Create the logger instance
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging_level)
        # Create the queue and add a queue handler to the logger
        que = Queue(-1)  # -1 means no size limit
        self._logger.addHandler(QueueHandler(que))
        # Set the format for logs
        formatter = logging.Formatter(
            "%(asctime)s:%(name)s:%(levelname)s:\n\t%(message)s\n"
        )
        # Build a list of output handlers.
        handlers = list()
        handlers.append(logging.StreamHandler())
        handlers.append(logging.FileHandler(filename))
        # Add more handlers as necessary. . .
        # Format the handlers
        for handler in handlers:
            handler.setFormatter(formatter)
        # Build the queue listener with the output handlers, start
        # the listener, and atexit.register the listener's stop function
        listener = QueueListener(que, *handlers)
        listener.start()
        register(listener.stop)
        self.info(f"Logger successfully built with handlers: {handlers}")
        return

    def __load_database(self) -> None:
        """Not yet implemented"""
        self.warning("Database is not yet implemented.")
        return

    def __load_token(self) -> str:
        """Loads the bot token from the .env file."""
        self.info("Retrieving DISCORD_TOKEN from .env file.")
        if not load_dotenv():
            self.critical("No .env file exists. Cannot run bot.")
            sys.exit()
        token = os.getenv("DISCORD_TOKEN")
        if token is None:
            self.critical("No DISCORD_TOKEN found in .env. Cannot run bot.")
            sys.exit()
        self.info("DISCORD_TOKEN found.")
        return token

    def load_all_extensions(self) -> None:
        """Finds all .py files within the cogs folder tree and loads them as
        extensions."""
        self.info("Loading all extensions from cogs folder.")
        folder_path = Path("cogs")
        if folder_path.exists():
            self.debug("Path to cogs folder found.")
        else:
            self.warning("No cogs folder exists.")
            return
        for item in folder_path.glob("**/*.py"):
            # Generate the extension name in the proper format and load it
            path = item.relative_to(folder_path.parent)
            extension = str(path).replace("\\", ".")[:-3]  # [:-3] strips ".py"
            self.load_extension(extension)
        if not self.extensions:
            self.warning("No extensions are loaded.")
        self.info("Loading extensions is complete.")
        return

    def load_extension(self, extension: str) -> None:
        """Loads the given extension while handling errors by providing
        feedback to the logger and ignoring invalid extension names"""
        try:
            super().load_extension(extension)
        except (ExtensionNotFound, ExtensionAlreadyLoaded,
                ExtensionFailed, NoEntryPointError) as error:
            self.exception(f"In {extension}:\n{error}")
        else:
            self.info(f"{extension} loaded successfully.")
        return

    def run(self) -> None:
        """Runs the bot with the loaded discord token."""
        self.info("Running the bot.")
        super().run(self.__load_token())
        return

    async def on_connect(self):
        """Logs successful discord connection"""
        self.info("Successfully connected to discord.")
        return

    async def on_ready(self):
        """Logs that bot has logged in."""
        self.info(f"Logged in to discord as {self.user}.")
        return

    async def send_message(self, ctx, msg) -> None:
        """Sends a message to discord. If the message is too long, it breaks it
        up into several smaller messages. This should be used in place of
        ctx.send() whenever the length of the message may be greater than 2000
        characters long."""
        if len(msg) <= 2000:
            await ctx.send(msg)
            return
        message_slices = [msg[i:i+2000] for i in range(0, len(msg), 2000)]
        for message in message_slices:
            await ctx.send(message)
        return

    async def send_embed(self, ctx, embed) -> None:
        """Sends an embed in a standardized way so that all cogs produce
        embeds with a consistent style."""
        # Not yet implemented
        pass

    def debug(self, msg: str) -> None:
        """Generates a logger debug message."""
        self._logger.debug(msg)
        return

    def info(self, msg: str) -> None:
        """Generates a logger info message."""
        self._logger.info(msg)
        return

    def warning(self, msg: str) -> None:
        """Generates a logger warning message."""
        self._logger.warning(msg)
        return

    def error(self, msg: str) -> None:
        """Generates a logger error message."""
        self._logger.error(msg)
        return

    def critical(self, msg: str) -> None:
        """Generates a logger critical message."""
        self._logger.critical(msg)
        return

    def exception(self, msg: str) -> None:
        """Generates a logger exception message."""
        self._logger.exception(msg)
        return

# TODO: Implement send_embed()
