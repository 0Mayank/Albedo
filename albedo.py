import os
import logging

import discord
from discord.ext import commands

from my_utils.default import all_cases, get
from my_utils.data import Bot, HelpCommand
from my_utils.guildstate import state_instance

config = get("config.json")

command_prefix = all_cases(config.prefix)

def get_prefix(bot, message):
    gstate = state_instance.get_state(message.guild.id)
    return command_prefix + all_cases(gstate.prefix) 

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=False,
    command_attrs=dict(hidden=True),
    help_command=HelpCommand()
)
@bot.check
def check_availabilty(ctx):
    cmd = ctx.command
    if str(cmd) == "enable" or str(cmd) == "disable":
        return True
    
    state = state_instance.get_state(ctx.guild.id)
    if cmd.root_parent:
        cmd = cmd.root_parent 
    availability = state.get_var(str(cmd)) if state.get_var("all") else False
    return availability

for filename in os.listdir('cogs'):                                   #Loads all the cogs                  
    if filename.endswith('.py') and filename not in config.off_by_default:
        bot.load_extension(f'cogs.{filename[:-3]}')

def run():
    bot.run(config.token[1])
    

#logging setup
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("albedo.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

run()
