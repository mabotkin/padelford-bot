import datetime
import discord
from discord import option
from discord.ext import tasks
import random
import os
from dotenv import load_dotenv
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import time, timezone

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
bot = discord.Bot( intents = intents )

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
	"Jackson" : 358271740285026306 ,
	"Sean" : 741470146706800660 ,
}

@bot.event
async def on_ready():
	birthday.start()
	print( f'We have logged in as {bot.user}' )

@bot.event
async def on_message( message ):
	if message.author == bot.user:
		return
	if message.author.id == USER_IDS[ "Sean" ] :
		if random.random() < 0.05:
			await message.reply( "That is a good point!" )
	if message.author.id == USER_IDS[ "Jackson" ] :
		if random.random() < 0.05:
			reply = "".join( [ ( x.lower() if ( i % 2 == 0 ) else x.upper() ) for i , x in enumerate( message.content.lower() ) ] )
			await message.reply( reply )
	if "ism" in message.content.lower():
		emoji = "💩"
		await message.add_reaction(emoji)

class ContributeView( discord.ui.View ):
	def __init__( self ):
		super().__init__()
		button = discord.ui.Button( label = "Github" , style = discord.ButtonStyle.link , url = "https://github.com/mabotkin/padelford-bot" )
		self.add_item( button )

@bot.slash_command( name = "about" , description = "Shows an About Me message." , guild_ids = GUILD_IDS )
async def about( ctx ):
	await ctx.respond( 'Hello! I am a friendly bot here to help facilitate activities on the In-Came Autumn 2021 Math Grad Students Discord Server.  Any resemblance to Jackson Morris is purely coincidental.' , view = ContributeView() )

class RoleSelect( discord.ui.Select ):
	def __init__( self , interests ):
		self.interests = interests
		super().__init__(
			placeholder = "Choose your interests!" ,
			min_values = 1,
			max_values = len( interests ) ,
			options = [
				discord.SelectOption( label = role ) for role in interests[::-1]
			] ,
		)

	async def callback( self , interaction ):
		member = interaction.user
		response_text = "Adding roles: " + ( ", ".join( [ "\"" + x + "\"" for x in self.values ] ) ) + "...";
		await interaction.response.edit_message( content = response_text , view = None )
		# remove all interest roles first
		remove_roles = []
		for role_name in self.interests:
			remove_roles.append( discord.utils.get( interaction.guild.roles , name = role_name ) )
		await member.remove_roles( *remove_roles )
		# add back new roles
		add_roles = []
		for role_name in self.values:
			add_roles.append( discord.utils.get( interaction.guild.roles , name = role_name ) )
		await member.add_roles( *add_roles )

class RoleSelectView( discord.ui.View ):
	def __init__( self , interests ):
		super().__init__( timeout = None )
		self.interests = interests
		self.add_item( RoleSelect( interests = interests ) )

@bot.slash_command( name = "getrole" , description = "Select your interest roles." , guild_ids = GUILD_IDS )
async def get_roles( ctx ):
	interests = [ role.name for role in ctx.guild.roles if role <= discord.utils.get( ctx.guild.roles , name = "combinatorics" ) and role.name != "@everyone" ]
	await ctx.respond( view = RoleSelectView( interests = interests ) , ephemeral = True )

class FAQView( discord.ui.View ):
	def __init__( self ):
		super().__init__()
		button = discord.ui.Button( label = "FAQ" , style = discord.ButtonStyle.link , url = "https://docs.google.com/document/d/1TQtQ48WrYaHLAe3eruJi7blMlKQfbu8_a6hWHr2UhrQ/edit" )
		self.add_item( button )

@bot.slash_command( name = "faq" , description = "Displays the FAQ document." , guild_ids = GUILD_IDS )
async def faq( ctx ):
	await ctx.respond( view = FAQView() , ephemeral = True )

@bot.slash_command( name = "setbirthday", description = "Tell us your birthday!")
async def set_birthday( ctx, *, month: int, day: int):
	try:
		bday = datetime.date(2000, month, day) # hardcode 2000 because it's a leap year, just in case
		await ctx.respond(f'Setting {ctx.author.mention}\'s birthday to {month}/{day}.' , ephemeral = True )
	except ValueError:
		await ctx.respond('Please provide a valid date.' , ephemeral = True )
	else:
		sheet = spreadsheet.worksheet("Birthdays")
		cur_cell = sheet.find(ctx.author.name, in_column=1)
		if cur_cell == None:
			sheet.append_row([ctx.author.name, str(ctx.author.id), month, day])
		else:
			sheet.update_cell(cur_cell.row, 2, str(ctx.author.id))
			sheet.update_cell(cur_cell.row, 3, month)
			sheet.update_cell(cur_cell.row, 4, day)

@bot.slash_command( name = "birthdays", description = "Start planning your parties now.")
async def upcoming_bdays(ctx):
	days_in_advance = 7
	today = datetime.date.today()
	next_dates = [today + datetime.timedelta(days = i) for i in range(days_in_advance)]
	next_dates_no_year = [(d.month, d.day) for d in next_dates]

	sheet = spreadsheet.worksheet("Birthdays")
	all_bdays = sheet.get_all_records()
	upcoming_bdays = {
		row['userid'] : str(row['month']) + "/" + str(row['day'])
		for row in all_bdays if (row['month'], row['day']) in next_dates_no_year
	}
	if not upcoming_bdays:
		await ctx.respond(f'No birthdays in the next week :/')
	else:
		resp = "Birthdays in the next week:\n"
		for userid in upcoming_bdays:
			resp += f'<@{userid}> - {upcoming_bdays[userid]}\n'
		await ctx.respond(resp)

@tasks.loop( time = time( 8 , 0 , tzinfo = timezone.utc ) )
async def birthday():
	channel = discord.utils.get(bot.get_all_channels(), name="general")
	today = datetime.date.today()
	today_month = today.month
	today_day = today.day
	birthday_people = [
		row["userid"] for row in spreadsheet.worksheet("Birthdays").get_all_records()
		if row["month"] == today_month and row["day"] == today_day
	]
	is_alberts_birthday = not ( today_month == 5 and today_day == 27 )
	if is_alberts_birthday:
		if len(birthday_people) == 0:
			pass
		elif len(birthday_people) == 1:
			await channel.send(f'Happy Birthday <@{birthday_people[0]}> and Albert!')
		else:
			all_mentions = [f'<@{person}>' for person in birthday_people]
			await channel.send("Happy Birthday " + ', '.join(all_mentions) + ", and Albert!")
	else: # important edge case
		if len(birthday_people) == 0:
			pass
		elif len(birthday_people) == 1:
			await channel.send(f'Happy Birthday <@{birthday_people[0]}>!')
		else:
			all_mentions = [f'<@{person}>' for person in birthday_people]
			await channel.send("Happy Birthday " + ', '.join(all_mentions[:-1]) + ", and " + all_mentions[-1] + "!")

bot.run( os.getenv( "API_KEY" ) )
