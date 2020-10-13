import cbpro
import discord
from discord.ext import commands

# Cryptocurrency cog
class CryptoCmd(commands.Cog):
    # Initializes the cog and sets a client for grabbing coinbase pro data
    def __init__(self, bot):
        self.bot = bot;
        self.coinbase_client = cbpro.PublicClient();

    # Command for grabbing a crypto's USD price stats.
    # arg should be a ticker symbol for the desired cryptocurrency.
    @commands.command()
    async def stats(self, ctx, arg = "BTC"):
        # Sets the argument string to send to coinbase. Also used as the title
        # for the embed sent to discord.
        title = f"{arg.upper()}-USD";
        # Requests data from coinbase and stores it in a dictionary
        data = self.coinbase_client.get_product_24hr_stats(title);
        # Prints raw data to console.
        print(data);

        # Generates an embed object
        embed_message = discord.Embed(
        title = title,
        type = "rich",
        colour = self.bot._embed_color
        );

        # Iterates through the data dictionary returned from coinbase to
        # create fields for the embed object
        for key in data:
            embed_message.add_field(
            name = f"**{key}**",
            value = f"{data[key]}");

        # Send the embed to discord
        await ctx.send(embed = embed_message);

# setup command for the cog
def setup(bot):
    bot.add_cog(CryptoCmd(bot));
