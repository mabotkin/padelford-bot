import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client( intents = intents )

@client.event
async def on_ready():
	print( f'We have logged in as {client.user}' )

@client.event
async def on_message( message ):
	if message.author == client.user:
		return

	if message.content.lower() == '!bot' :
		await message.channel.send( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' )

key = ""
if "API_KEY" in dict(os.environ):
	key = os.environ(["API_KEY"])
else:
	load_dotenv()
	key = os.getenv("API_KEY")

client.run( key )
