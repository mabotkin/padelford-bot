import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

# client = discord.Client( intents = intents )
bot = discord.Bot(debug_guilds = [997949327974604911])

@bot.event
async def on_ready():
	print( f'We have logged in as {bot.user}' )

@bot.slash_command(name = "bot")
async def bot_command(ctx):
	await ctx.respond( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' )

key = ""
if "API_KEY" in dict(os.environ):
	key = os.environ(["API_KEY"])
else:
	load_dotenv()
	key = os.getenv("API_KEY")

bot.run( key )
