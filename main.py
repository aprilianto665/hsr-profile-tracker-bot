import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

BASE_URL = "https://hsr-backend.redfield-e7b65d33.southeastasia.azurecontainerapps.io/profile"

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))