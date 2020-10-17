import discord
from discord.ext import commands
from random import shuffle


GAME_MASTER = {}


def is_game_master(ctx):
    return ctx.message.author.id == GAME_MASTER.get(ctx.guild.id)


class TruthOrDareCmd(commands.Cog):
    """ Command list for playing a Truth or Dare game with server members. """
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.revenge = {}
        self.last_roll = {}
        self.text_channel = {}
        self.voice_channel = {}

    @commands.command()
    async def tod_join(self, ctx, *args):
        """ Join a game of Truth or Dare. """
        text_names = [c.name for c in ctx.guild.text_channels]
        voice_names = [c.name for c in ctx.guild.voice_channels]
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False, send_messages=False
            ),
            self.bot.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
            ctx.author: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, connect=True,
                speak=True
            )
        }

        # Deletes the channels if they exist
        if not self.players.get(ctx.guild.id):
            if "truth-or-dare" in text_names:
                text = ctx.guild.text_channels[text_names.index(
                    "truth-or-dare"
                )]
                await text.delete()
            if "secret-voice" in voice_names:
                voice = ctx.guild.voice_channels[voice_names.index(
                    "secret-voice"
                )]
                await voice.delete()

        # Creates the channels
        self.text_channel[ctx.guild.id] = await ctx.guild.create_text_channel(
            'truth-or-dare', overwrites=overwrites
        )
        self.voice_channel[ctx.guild.id] = await ctx.guild.create_voice_channel(
            'secret-voice', overwrites=overwrites
        )

        # Makes the first player the Game Master
        if not self.players.get(ctx.guild.id):
            self.players[ctx.guild.id] = []
            global GAME_MASTER
            GAME_MASTER[ctx.guild.id] = ctx.author.id

        if ctx.author not in self.players.get(ctx.guild.id, []):
            self.players[ctx.guild.id].append(ctx.author)
            message = f"{ctx.author.mention} has been added to the game!"
            await self.text_channel[ctx.guild.id].send(message)
        else:
            message = f"{ctx.author.mention} has already joined!"
            await ctx.send(message)

    @tod_join.error
    async def tod_join_error(self, ctx, *args):
        message = "Something is wrong...\n" \
                  "Make sure I have permission to manage channels."
        await ctx.send(message)

    @commands.command()
    async def tod_leave(self, ctx, *args):
        """ Leave a game of Truth or Dare. """
        await self.text_channel[ctx.guild.id].set_permissions(
            ctx.author, read_messages=False, send_messages=False
        )
        await self.voice_channel[ctx.guild.id].set_permissions(
            ctx.author, connect=False, speak=False
        )

        try:
            self.players[ctx.guild.id].remove(ctx.author)
        except ValueError:
            await ctx.send(f"{ctx.author.mention}, you're not playing!")

        global GAME_MASTER
        if ctx.author.id == GAME_MASTER.get(ctx.guild.id) and \
                self.players.get(ctx.guild.id):
            await self._assign_new_game_master(ctx)
        elif ctx.author.id == GAME_MASTER.get(ctx.guild.id):
            await self._clean_up(ctx)

    @commands.command()
    @commands.check(is_game_master)
    async def tod_remove(self, ctx, *args):
        """ Forcefully removes someone from the Truth or Dare game. """
        if not self.players.get(ctx.guild.id):
            await ctx.send("There are currently no users playing.")
            return
        elif not args:
            message = "Either mention the players to remove or specify `all`."
            await ctx.send(message)
            return

        if "all" in args:
            await self._clean_up(ctx)
            return

        to_remove = []
        for arg in args:
            for player in self.players[ctx.guild.id]:
                if str(player.id) in arg:
                    to_remove.append(player)
                    break

        if not to_remove:
            await ctx.send("No one was removed.")
            return

        for player in to_remove:
            await self.text_channel[ctx.guild.id].set_permissions(
                player, read_messages=False, send_messages=False
            )
            await self.voice_channel[ctx.guild.id].set_permissions(
                player, connect=False, speak=False
            )
            self.players[ctx.guild.id].remove(player)
            global GAME_MASTER
            if player.id == GAME_MASTER[ctx.guild.id]:
                try:
                    await self._assign_new_game_master(ctx)
                except IndexError:
                    await ctx.send("Cleaning up...")
            else:
                message = f"{player.mention} has been removed from the game!"
                await ctx.send(message)

        if not self.players[ctx.guild.id]:
            await ctx.send("Cleaning up...")
            await self._clean_up(ctx)

    @tod_remove.error
    async def tod_remove_error(self, ctx, *args):
        await ctx.send("You need to be the Game Master to use this command.")

    @commands.command()
    async def tod_players(self, ctx, *args):
        """ Shows the list of players in the Truth or Dare game. """
        message = "__Currently Playing__\n"
        if not self.players.get(ctx.guild.id):
            message = "There are currently no users playing."
            await ctx.send(message)
        else:
            global GAME_MASTER
            for player in self.players[ctx.guild.id]:
                if player.id == GAME_MASTER.get(ctx.guild.id):
                    player = str(player)[:-5] + " (Game Master)"
                else:
                    player = str(player)[:-5]
                message += f">  {player}\n"
            await ctx.send(message)

    @commands.command()
    @commands.check(is_game_master)
    async def tod_revenge(self, ctx, *args):
        """ Toggles revenge mode (players can roll each other). """
        self.revenge[ctx.guild.id] = not bool(self.revenge.get(ctx.guild.id))
        if self.revenge[ctx.guild.id]:
            message = "Revenge mode is now __on__."
        else:
            message = "Revenge mode is now __off__."
        await ctx.channel.send(message)

    @tod_revenge.error
    async def tod_revenge_error(self, ctx, *args):
        await ctx.send("You need to be the Game Master to use this command.")

    @commands.command()
    async def tod_status(self, ctx, *args):
        """ Checks to see whether a Truth or Dare game is in progress. """
        n = 0 if not self.players.get(ctx.guild.id) \
            else len(self.players[ctx.guild.id])
        if n > 0:
            s = "person" if n == 1 else "people"
            message = f"A Truth or Dare game is currently taking place " \
                      f"with {n} {s}!"
        else:
            message = "No Truth or Dare game is currently taking place."
        await ctx.send(message)

    @commands.command()
    @commands.has_role("tod_Player")
    async def tod_roll(self, ctx, *args):
        """ Roll for someone to ask: \"Truth or Dare?\" """
        if not ctx.message.channel.name == "truth-or-dare":
            raise ValueError
        elif len(self.players[ctx.guild.id]) < \
                3 - int(self.revenge.get(ctx.guild.id, 0)):
            await ctx.send("Not enough players!")
        else:
            shuffle(self.players[ctx.guild.id])
            if not self.revenge.get(ctx.guild.id):
                while self.players[ctx.guild.id][0] == ctx.author or \
                        self.players[ctx.guild.id][0] == \
                        self.last_roll.get(ctx.guild.id):
                    shuffle(self.players[ctx.guild.id])
            else:
                while self.players[ctx.guild.id][0] == ctx.author:
                    shuffle(self.players[ctx.guild.id])
            self.last_roll[ctx.guild.id] = ctx.author
            message = f"{self.players[0].mention}, truth or dare?"
            await ctx.send(message)

    @tod_roll.error
    async def tod_roll_error(self, ctx, *args):
        if not self.players.get(ctx.guild.id):
            await ctx.send("No Truth or Dare game is currently taking place.")
        elif not ctx.message.channel.name == "truth-or-dare":
            ID = [c.id for c in ctx.guild.channels if c.name == "truth-or-dare"]
            await ctx.send(f"Roll in <#{ID[0]}>!")
        else:
            await ctx.send(f"{ctx.author.mention}, you're not playing!")

    async def _clean_up(self, ctx):
        await self.text_channel[ctx.guild.id].delete()
        self.text_channel[ctx.guild.id] = None
        await self.voice_channel[ctx.guild.id].delete()
        self.voice_channel[ctx.guild.id] = None
        self.players[ctx.guild.id] = []
        global GAME_MASTER
        GAME_MASTER[ctx.guild.id] = None

    async def _assign_new_game_master(self, ctx):
        global GAME_MASTER
        player = self.players[ctx.guild.id][0]
        GAME_MASTER[ctx.guild.id] = player.id
        message = f"{ctx.author.mention} has been removed from the game!"
        message += f"\n{player.mention} is the new Game Master."
        await ctx.send(message)


def setup(bot):
    """ The setup command for the Cog. """
    bot.add_cog(TruthOrDareCmd(bot))
