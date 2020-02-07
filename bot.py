import discord
import os
from itertools import cycle
from discord.ext import commands, tasks
from discord.utils import oauth_url
import utils as u
from guildstate import state_instance
from HelpSubclass import HelpCommand

sexy_admins = os.environ.get("SEXY_ADMINS").split()

offByDefault = ['debugmode.py', 'memberlog.py']
command_prefix = u.all_cases("ss ")

def get_prefix(bot, message):
    gstate = state_instance.get_state(message.guild)
    return command_prefix + [gstate.prefix] 

bot = commands.Bot(command_prefix=get_prefix)
bot.help_command = HelpCommand(verify_checks=False)

status = cycle(['Thank You','for coming','to my','Ted Talk'])                                     #Shows bot status
@tasks.loop(seconds=1)
async def change_status():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(next(status)))

for filename in os.listdir('./cogs'):                                   #Loads all the cogs                  
    if filename in offByDefault:
        pass
    elif filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# Events
@bot.event
async def on_ready():
    change_status.start()
    print('Bot is ready!')


@bot.event
async def on_guild_join(guild):
    state_instance.get_state(guild)   

@bot.event
async def on_guild_remove(guild):
    state_instance.delete_state(guild)

# Commands

@bot.command(hidden = True)                                                       #ENABLE command
async def load_cog(ctx, *, extension):
    inpu = extension.split()
    extension = ""
    for i in inpu:
        extension += i
    inpu = ""
    bot.load_extension(f'cogs.{extension}')

@bot.command(hidden = True)                                                          #DISABLE command
async def unload_cog(ctx, *, extension):
    inpu = extension.split()
    extension = ""
    for i in inpu:
        extension += i
    inpu = ""
    bot.unload_extension(f'cogs.{extension}')

# @bot.command()
# async def initiate(ctx):
#     state = gstate.get_state(ctx.guild)
#     await ctx.send(f"{state.server}, Initialization succesful")

# @bot.command()
# async def allstates(ctx):
#     states = gstate.all_states()
#     await ctx.send(states)

TOKEN = os.environ.get("DISCORD_BOT_SECRET")                                #Token here
print(TOKEN)
bot.run (TOKEN)