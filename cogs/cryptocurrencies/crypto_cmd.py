import aiohttp
import cbpro
import discord
import os
from dotenv import load_dotenv, find_dotenv
from requests import Request, Session
from discord.ext import commands


# Cryptocurrency cog
class CryptoCmd(commands.Cog):
    # Initializes the cog and sets a client for grabbing coinbase pro data
    def __init__(self, bot):
        self.bot = bot
        # Open a coinbase client for grabbing coinbase crypto price
        self.coinbase_client = cbpro.PublicClient()
        # Default coinmarketcap api keys are sandbox keys. They don't work as
        # well as a real key, often returning incorrect data.
        self.cmc_api_key = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"
        self.cmc_api_url = "https://sandbox-api.coinmarketcap.com/v1/\
            cryptocurrency/info"
        # Load optional environment variables.
        if load_dotenv(find_dotenv(filename="crypto.env")):
            self.cmc_api_key = os.getenv("CMC_API_KEY",
                                         default=self.cmc_api_key)
            self.cmc_api_url = os.getenv("CMC_API_URL",
                                         default=self.cmc_api_url)
            self.crypto_down_image = self.crypto_up_image = os.getcwd()
            self.crypto_up_image += "\\cogs\\cryptocurrencies\\"
            self.crypto_down_image = self.crypto_up_image
            self.crypto_up_image += os.getenv("CRYPTO_UP", default=None)
            self.crypto_down_image += os.getenv("CRYPTO_DOWN", default=None)
        else:
            print(".env file not loading???")
        # Create dictionary to store data from coinmarketcap to reduce api calls
        self.logo_url_dict = dict()

    # Command for grabbing a crypto's USD price stats.
    # arg should be a ticker symbol for the desired cryptocurrency.
    @commands.command()
    async def cbpro(self, ctx, arg="BTC"):
        arg = arg.upper()  # Set the argument string for API's.
        title = f"{arg}-USD"  # Set the title for an embed
        file = None  # Set up a file holder in case we use one.
        # Collect data needed to generate embed.
        if arg not in self.logo_url_dict.keys():
            await self._try_cmc_lookup(arg)
        cb_data = self.coinbase_client.get_product_24hr_stats(title)
        # Generate an embed object
        embed_message = discord.Embed(
            title=title,
            type="rich",
            colour=self.bot.embed_color,
        )
        # Dynamically set up "author name" based on price
        if all(keys in cb_data for keys in ("last", "open")):
            percent_gain = round(
                (float(cb_data["last"]) / float(cb_data["open"]) - 1.0)
                * 100.0, 2)  # Round to two places
            emoji = "\U0001f449"
            if percent_gain >= 0.01:
                if percent_gain > 10.0:
                    file = discord.File(self.crypto_up_image)
                percent_gain = f"+{percent_gain}"
                emoji = "\U0001f44d"
            elif percent_gain <= -0.01:
                if percent_gain < -10.0:
                    file = discord.File(self.crypto_down_image)
                percent_gain = str(percent_gain)
                emoji = "\U0001f44e"
            else:
                percent_gain = "0.00"
            icon_url = discord.Embed.Empty
            if file != None:
                icon_url = f"attachment://{file.filename}"
            embed_message.set_author(
                name=f"{emoji} since open: {percent_gain}%",
                icon_url=icon_url
            )
        # Generate embed fields
        for key in cb_data:
            embed_message.add_field(
                name=f"**{key.capitalize()}**",
                value=f"{cb_data[key]}")
        # If an image url was found, use it for the thumbnail
        if arg in self.logo_url_dict.keys():
            embed_message.set_thumbnail(url=self.logo_url_dict[arg])
        # Send the embed to discord
        await ctx.send(file=file, embed=embed_message)

    # Tries to find coinmarketcap data for the argument and put it in dictionary
    async def _try_cmc_lookup(self, arg):
        # Set the headers for the request.
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.cmc_api_key
        }
        # Request data from coinmarketcap. If found, add it to dictionary
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                        url=self.cmc_api_url,
                        headers=headers,
                        params={"symbol": arg}
                ) as response:
                    response = await response.json()
                    try:
                        self.logo_url_dict[arg] = response["data"][arg]["logo"]
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)


# setup command for the cog
def setup(bot):
    bot.add_cog(CryptoCmd(bot))
