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
	"Sean" : 741470146706800660
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

@bot.slash_command( name = "set_birthday", description = "Tell us your birthday!")
async def set_birthday( ctx, *, month: int, day: int):
	try:
		bday = datetime.date(2000, month, day) # hardcode 2000 because it's a leap year, just in case
		await ctx.respond(f'Setting {ctx.author.mention}\'s birthday to {month}/{day}')
	except ValueError:
		await ctx.respond('Please provide a valid date.')
	else:
		sheet = spreadsheet.worksheet("Birthdays")
		cur_cell = sheet.find(ctx.author.name, in_column=1)
		if cur_cell == None:
			sheet.append_row([ctx.author.name, ctx.author.id, month, day])
		else:
			sheet.update_cell(cur_cell.row, 2, str(ctx.author.id))
			sheet.update_cell(cur_cell.row, 3, month)
			sheet.update_cell(cur_cell.row, 4, day)

@bot.slash_command( name = "upcoming_bdays", description = "Start planning your parties now.")
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


@bot.slash_command( name = "getmath" , description = "Gives you the \"math\" role, which allows you to add interest roles." , guild_ids = GUILD_IDS )
async def interest_role( ctx ):
	member = ctx.author
	role = discord.utils.get( ctx.guild.roles , name = "math" )
	await member.add_roles( role )
	await ctx.respond( f"Gave math role to { member.mention }." )

@bot.slash_command( name = "faq" , description = "Displays FAQ messages." , guild_ids = GUILD_IDS )
@option( "searchterm" , descrption = "Enter a search term to filter FAQ messages." , default = "" )
async def faq( ctx , searchterm : str ):
	sheet = spreadsheet.worksheet( "FAQ" )
	faqs = sheet.col_values( 1 )
	if searchterm != "":
		faqs = [ x for x in faqs if searchterm in x ]
	reply = "\n".join( [ "`" + x + "`" for x in faqs ] )
	await ctx.respond( reply )

@tasks.loop( time = time( 7 , 0 , tzinfo = timezone.utc ) )
async def birthday():
	channel = discord.utils.get(bot.get_all_channels(), name="general")
	today = datetime.date.today()
	today_month = today.month
	today_day = today.day
	birthday_people = [
		row["userid"] for row in spreadsheet.worksheet("Birthdays").get_all_records()
		if row["month"] == today_month and row["day"] == today_day
	]
	if len(birthday_people) == 0:
		await channel.send( "Happy Birthday Albert!" )
	elif len(birthday_people) == 1:
		await channel.send(f'Happy Birthday <@{birthday_people[0]}> and Albert!')
	else:
		all_mentions = [f'<@{person}>' for person in birthday_people]
		await channel.send("Happy Birthday " + ', '.join(all_mentions) + ", and Albert!")

bot.run( os.getenv( "API_KEY" ) )
