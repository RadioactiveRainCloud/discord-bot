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

    @commands.command()
    async def tod_join(self, ctx, *args):
        """ Join a game of Truth or Dare. """
        channel_names = [c.name for c in ctx.guild.channels]
        role_names = [r.name for r in ctx.guild.roles]

        # Check to see if the roles exist
        if "tod_Player" not in role_names:
            message = "Something is wrong...\n" \
                      "Make sure there is a `tod_Player` role!"
            await ctx.send(message)
            return

        # Creates the channels if they don't exist
        if "truth-or-dare" not in channel_names:
            default = ctx.guild.default_role
            player = discord.utils.get(ctx.guild.roles, name="tod_Player")
            bots = self.bot.user
            overwrites = {
                default: discord.PermissionOverwrite(read_messages=False,
                                                     send_messages=False),
                bots: discord.PermissionOverwrite(read_messages=True,
                                                  send_messages=True),
                player: discord.PermissionOverwrite(read_messages=True,
                                                    send_messages=True,
                                                    connect=True, speak=True)
            }
            await ctx.guild.create_text_channel('truth-or-dare',
                                                overwrites=overwrites)
            await ctx.guild.create_voice_channel('secret-voice',
                                                 overwrites=overwrites)

        # Makes the first player the Game Master
        if not self.players.get(ctx.guild.id):
            self.players[ctx.guild.id] = []
            global GAME_MASTER
            GAME_MASTER[ctx.guild.id] = ctx.author.id

        # Adds the tod_Player role
        role = discord.utils.get(ctx.guild.roles, name="tod_Player")
        await ctx.author.add_roles(role)

        if ctx.author not in self.players.get(ctx.guild.id, []):
            self.players[ctx.guild.id].append(ctx.author)
            message = f"{ctx.author.mention} has been added to the game!"
            await ctx.send(message)
        else:
            message = f"{ctx.author.mention} has already joined!"
            await ctx.send(message)

    @tod_join.error
    async def tod_join_error(self, ctx, *args):
        message = "Something is wrong...\n" \
                  "Make sure I have permission to create channels and " \
                  "manage roles."
        await ctx.send(message)

    @commands.command()
    @commands.has_role("tod_Player")
    async def tod_leave(self, ctx, *args):
        """ Leave a game of Truth or Dare. """
        role = discord.utils.get(ctx.guild.roles, name="tod_Player")
        await ctx.author.remove_roles(role)

        try:
            self.players[ctx.guild.id].remove(ctx.author)
        except ValueError:
            pass

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

        if "all" in args:
            await self._clean_up(ctx)
            return

        for name in args:
            message = ""
            size = len(self.players.get(ctx.guild.id, []))
            author = ctx.author.mention
            if author.replace("!", "") == name.replace("!", "") and size == 1:
                await self._clean_up(ctx)
                return
            elif author.replace("!", "") == name.replace("!", ""):
                self.players[ctx.guild.id].remove(ctx.author)
                await self._assign_new_game_master(ctx)
            else:
                to_remove = None
                for user in self.players[ctx.guild.id]:
                    if name == user.mention:
                        to_remove = user
                        role = discord.utils.get(ctx.guild.roles,
                                                 name="tod_Player")
                        await user.remove_roles(role)
                        message = f"{name} has been removed from the game!"
                        break
                if to_remove is None:
                    message = f"{name} is not in the game!"
                else:
                    self.players[ctx.guild.id].remove(to_remove)
                await ctx.send(message)

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
        for user in self.players.get(ctx.guild.id, []):
            role = discord.utils.get(ctx.guild.roles, name="tod_Player")
            await user.remove_roles(role)
        for channel in ctx.guild.channels:
            if channel.name.startswith("truth-or-dare"):
                await channel.delete()
                break
        for channel in ctx.guild.channels:
            if channel.name.startswith("secret-voice"):
                await channel.delete()
                break
        self.players[ctx.guild.id] = []
        global GAME_MASTER
        GAME_MASTER[ctx.guild.id] = None
        try:
            message = "The game is over!"
            await ctx.send(message)
        except discord.errors.NotFound:
            pass

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
