import discord
from discord.ext import commands
import os
from utils_folder import default, utils as u
from utils_folder.data import Bot, HelpCommand, state_instance

config = default.get("config.json")
print(type(config))
print(config)

offByDefault = ['debugmode.py', 'memberlog.py']
command_prefix = u.all_cases(config.prefix)

def get_prefix(bot, message):
    gstate = state_instance.get_state(message.guild)
    return command_prefix + u.all_cases(gstate.prefix) 

bot = Bot(
    command_prefix=get_prefix,
    prefix=get_prefix,
    command_attrs=dict(hidden=True),
    help_command=HelpCommand()
)

for filename in os.listdir('cogs'):                                   #Loads all the cogs                  
    if filename.endswith('.py') and filename not in offByDefault:
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run (config.token[1])