import discord
import random
import os
from dotenv import load_dotenv
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
bot = discord.Bot(intents = intents)

# connect gsheets
scopes = [ 'https://spreadsheets.google.com/feeds' ]
json_creds = os.getenv( "GOOGLE_SHEETS_CREDS_JSON" )

creds_dict = json.loads( json_creds , strict = False )
creds_dict[ "private_key" ] = creds_dict[ "private_key" ].replace( "\\\\n" , "\n" )
creds = ServiceAccountCredentials.from_json_keyfile_dict( creds_dict , scopes )
client = gspread.authorize( creds )
spreadsheet = client.open_by_url( os.getenv( "SPREADSHEET_URL" ) )

GUILD_IDS = [
	int( os.getenv( "GUILD_ID" ) )
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
	if "ism" in message.content.lower():
		emoji = "💩"
		await message.add_reaction(emoji)


@bot.slash_command( name = "about" , description = "Shows an About Me message." , guild_ids = GUILD_IDS )
async def about( ctx ):
	await ctx.respond( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' )

@bot.slash_command( name = "add_role", description = "Give yourself a fun new identity.", guild_ids = GUILD_IDS)
async def add_role( ctx, *, role: discord.Role):
	member = ctx.author
	await member.add_roles(role)
	await ctx.respond(f'Added role {role} to {member.mention}')

@bot.slash_command( name = "getmath" , description = "Gives you the \"math\" role, which allows you to add interest roles." , guild_ids = GUILD_IDS )
async def interest_role( ctx ):
	member = ctx.author
	role = discord.utils.get( ctx.guild.roles , name = "math" )
	await member.add_roles( role )
	await ctx.respond( f"Gave math role to { member.mention }." )

@bot.slash_command( name = "faq" , description = "Displays FAQ messages." , guild_ids = GUILD_IDS )
async def faq( ctx ):
	sheet = spreadsheet.worksheet( "FAQ" )
	await ctx.respond( str( sheet.get_all_records() ) )

bot.run( os.getenv("API_KEY") )
