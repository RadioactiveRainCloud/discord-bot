import discord
from discord.ext import commands
from random import shuffle


class TruthOrDareCmd(commands.Cog):
    """ Command list for playing a Truth or Dare game with server members. """
    def __init__(self, bot):
        self.bot = bot
        self.players = []
        self.revenge = False
        self.last_roll = None

    @commands.command()
    async def tod_join(self, ctx, *args):
        """ Join a game of Truth or Dare. """
        if ctx.author not in self.players:
            self.players.append(ctx.author)
            message = f"{ctx.author.mention} has been added to the game!"
            await ctx.send(message)
        else:
            message = f"{ctx.author.mention} has already joined!"
            await ctx.send(message)

        # Updates the role if channel exists
        for channel in ctx.guild.channels:
            if channel.name.startswith("truth-or-dare"):
                role = discord.utils.get(ctx.guild.roles, name="Player")
                await ctx.author.add_roles(role)
                return

        # Creates the channel if it doesn't exist
        role = discord.utils.get(ctx.guild.roles, name="Player")
        bots = discord.utils.get(ctx.guild.roles, name="Bots")
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            bots: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            role: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=True, speak=True)
        }
        await ctx.guild.create_text_channel('truth-or-dare', overwrites=overwrites)
        await ctx.guild.create_voice_channel('secret-voice', overwrites=overwrites)

        # Adds the role
        role = discord.utils.get(ctx.guild.roles, name="Player")
        await ctx.author.add_roles(role)

    @commands.command()
    async def tod_leave(self, ctx, *args):
        """ Leave a game of Truth or Dare. """
        try:
            self.players.remove(ctx.author)
            role = discord.utils.get(ctx.guild.roles, name="Player")
            await ctx.author.remove_roles(role)
        except ValueError:
            pass
        message = f"{ctx.author.mention} has been removed from the game!"
        await ctx.send(message)

    @commands.command()
    @commands.has_role("GameMaster")
    async def tod_remove(self, ctx, *args):
        """ Forcefully removes someone from the Truth or Dare game. """
        if "all" in args:
            for user in self.players:
                role = discord.utils.get(ctx.guild.roles, name="Player")
                await user.remove_roles(role)
            for channel in ctx.guild.channels:
                if channel.name.startswith("truth-or-dare"):
                    await channel.delete()
                    break
            for channel in ctx.guild.channels:
                if channel.name.startswith("secret-voice"):
                    await channel.delete()
                    break
            self.players = []
            message = "All players removed from the game!"
            await ctx.send(message)
            return

        for name in args:
            message = ""
            size = len(self.players)
            for user in self.players:
                if name == user.mention:
                    self.players.remove(user)
                    role = discord.utils.get(ctx.guild.roles, name="Player")
                    await user.remove_roles(role)
                    message = f"{name} removed from the game!"
                if size == len(self.players):
                    message = "Player not in the game! Check command syntax."
                await ctx.send(message)

    @commands.command()
    async def tod_list(self, ctx, *args):
        """ Shows the list of players in the Truth or Dare game. """
        message = "__Currently Playing__\n"
        if len(self.players) == 0:
            message = "There are currently no users playing."
        for player in self.players:
            message += f">  {str(player)[:-5]}\n"
        await ctx.send(message)

    @commands.command()
    @commands.has_role("GameMaster")
    async def tod_revenge(self, ctx, *args):
        """ Toggles revenge mode (someone can roll the person who just rolled them). """
        roles = [y.name.lower() for y in ctx.author.roles]
        self.revenge = not self.revenge
        if self.revenge:
            message = "Revenges are now __on__."
        else:
            message = "Revenges are now __off__."
        await ctx.channel.send(message)

    @commands.command()
    async def tod_status(self, ctx, *args):
        """ Checks to see whether a Truth or Dare game is in progress. """
        n = len(self.players)
        if n > 0:
            if n == 1:
                s = "person"
            else:
                s = "people"
            message = f"A Truth or Dare game is currently taking place with {n} {s}!"
        else:
            message = "No Truth or Dare game is currently taking place."
        await ctx.send(message)

    @commands.command()
    async def tod_roll(self, ctx, *args):
        if ctx.author not in self.players:
            message = f"{ctx.author.mention}, you're not playing!"
            await ctx.send(message)
        elif len(self.players) < 3 - int(self.revenge):
            await ctx.send("Not enough players!")
        else:
            shuffle(self.players)
            if not self.revenge:
                while self.players[0] == ctx.author or self.players[0] == self.last_roll:
                    shuffle(self.players)
            else:
                while self.players[0] == ctx.author:
                    shuffle(self.players)
            self.last_roll = ctx.author
            message = f"{self.players[0].mention}, truth or dare?"
            await ctx.send(message)


def setup(bot):
    """ The setup command for the Cog. """
    bot.add_cog(TruthOrDareCmd(bot))
