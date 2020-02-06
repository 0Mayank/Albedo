import discord
import os
from itertools import cycle
from discord.ext import commands, tasks
from discord.utils import oauth_url
import utils as u
from guildstate import state_instance

sexy_admins = os.environ.get("SEXY_ADMINS").split()

offByDefault = ['debugmode.py', 'memberlog.py']
command_prefix = u.all_cases("ss ")

def get_prefix(bot, message):
    gstate = state_instance.get_state(message.guild)
    return command_prefix + [gstate.prefix] 

bot = commands.Bot(command_prefix=get_prefix)
#bot.remove_command("help")

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
@bot.command()
async def prefix(ctx, *, prefix = None):
    embed = discord.Embed(color = discord.Colour.from_rgb(0, 0, 0), timestamp = ctx.message.created_at)
    state = state_instance.get_state(ctx.guild)
    if prefix == None:
            embed.add_field(name="Current Prefix", value=f"Current prefix `{state.prefix}`", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    elif prefix != None:
        if str(ctx.message.author.id) in sexy_admins:
            state.prefix = prefix
            embed.add_field(name="Prefix", value=f"Prefix changed to `{state.prefix}`", inline=False)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            print("prefix changed to {} in {}".format(prefix,ctx.guild))
        else:
            embed = discord.Embed(title="You thought you could do that, how gae.", timestamp = ctx.message.created_at)
 
    await ctx.send(embed=embed) 

@bot.command()                                                          #ENABLE command
async def load_cog(ctx, *, extension):
    inpu = extension.split()
    extension = ""
    for i in inpu:
        extension += i
    inpu = ""
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def av(ctx, member: discord.Member = None):
  member = ctx.author if not member else member
  embed = discord.Embed(timestamp=ctx.message.created_at)

  embed.set_author(name=f"Avatar of {member}")
  embed.set_image(url=member.avatar_url)
  embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

  await ctx.send(embed=embed)

@bot.command()                                                          #DISABLE command
async def unload_cog(ctx, *, extension):
    inpu = extension.split()
    extension = ""
    for i in inpu:
        extension += i
    inpu = ""
    bot.unload_extension(f'cogs.{extension}')

@bot.command()
async def ping(ctx):
  embed = discord.Embed(timestamp=ctx.message.created_at)
  embed.add_field(name="Bot ping",value=f"{round(bot.latency*1000)}ms")
  await ctx.send(embed=embed)

# @bot.command()
# async def initiate(ctx):
#     state = gstate.get_state(ctx.guild)
#     await ctx.send(f"{state.server}, Initialization succesful")

# @bot.command()
# async def allstates(ctx):
#     states = gstate.all_states()
#     await ctx.send(states)



@bot.command()
async def botinvite(ctx):
    await ctx.send(oauth_url(bot.user.id, permissions=discord.Permissions(permissions=1580723312), guild=None, redirect_uri=None))

@bot.command(aliases = ['copycat', 'cc', 'copyback'])
async def _copycat(ctx, *, arg = None):
    await ctx.send(arg)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author

    roles = [role for role in member.roles]
    
  
    embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)

    embed.set_author(name=f"User info of {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.add_field(name="ID",value=member.id)
  
    embed.add_field(name="Guild name",value=member.guild)
    embed.add_field(name="Created at",value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Joined at",value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

    embed.add_field(name=f"Roles ({len(roles)-1})",value="\n".join([role.mention for role in roles[1::1]]))
    embed.add_field(name="Top role",value=member.top_role.mention)
  
    await ctx.send(embed=embed)

@bot.command()
async def server(ctx):
    await ctx.send(str(ctx.author.guild))

TOKEN = os.environ.get("DISCORD_BOT_SECRET")                                #Token here
print(TOKEN)
bot.run (TOKEN)