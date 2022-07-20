import discord
import random
import os

bot = discord.Bot()

GUILD_IDS = [
	int( os.environ[ "GUILD_ID" ] )
]

USER_IDS = {
	"Sean" : 741470146706800660
}

@bot.event
async def on_ready():
	print( f'We have logged in as {bot.user}' )

@bot.event
async def on_message( message ):
	if message.author == bot.user:
		return
	if message.author.id == USER_IDS[ "Sean" ] :
		if random.random() < 0.05:
			await message.reply( "That is a good point!" )


@bot.slash_command( name = "about" , description = "Shows an About Me message." , guild_ids = GUILD_IDS )
async def about( ctx ):
	await ctx.respond( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' )

bot.run( os.environ[ "API_KEY" ] )
