import discord
import os

bot = discord.Bot()

GUILD_IDS = [
	int( os.environ[ "GUILD_ID" ] )
]

@bot.event
async def on_ready():
	print( f'We have logged in as {bot.user}' )

@bot.event
async def on_message( message ):
	if message.author == bot.user:
		return

@bot.slash_command( name = "about" , description = "Shows an About Me message." , guild_ids = GUILD_IDS )
async def about( ctx ):
	await ctx.respond( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' )

bot.run( os.environ[ "API_KEY" ] )
