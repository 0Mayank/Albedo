import os
import logging

import discord
from discord.ext import commands

from my_utils import default as u
from my_utils.data import Bot, HelpCommand
from my_utils.guildstate import state_instance

config = u.get("config.json")

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
