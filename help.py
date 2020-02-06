import discord
from discord.ext import commands
import utils as u
from guildstate import state_instance

f = u.retrieve("commands.json")

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *, argument = None):
        embed = discord.Embed(timestamp = ctx.message.created_at)
        if argument != None and len(argument.split()) > 1:    
            shit = argument.split()
            argument, argument22 = shit[0], shit[1:]
            argument3 = ""
            for i in argument22:
                argument3 += i + " "
            argument2 = argument3[0:len(argument3)-1]
        elif argument != None:
            argument2 = None
        if argument == None:
            embed = discord.Embed(title="SEXYBOT COMMAND LIST", description = f"Prefixes --> `sexy` or `{state_instance.get_state(ctx.guild).prefix}`\nUse `sexy help [category name]` for more info about the categories.")
            for key in f.keys():
                # embed.set_author(name="SEXYBOT COMMAND LIST")
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                embed.add_field(name=f'**{f[key]["name"]}**', value = '_{}_'.format(f[key]["description"]), inline=False)

        elif argument in f and argument2 == None:
            embed = discord.Embed(title = f"{argument.upper()} COMMANDS", description = "Use `sexy help [category name] [sub-category name]` for more info about the categories.", timestamp = ctx.message.created_at)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            for key in f[argument]["fields"].keys():
                embed.add_field(name='**{}**'.format(f[argument]["fields"][key]["name"]), value ='{}'.format(f[argument]["fields"][key]["value"], inline=True))
                
        elif argument in f and argument2 in f[argument]["fields"]:
            embed = discord.Embed(title ='**{}**'.format(argument2.upper()), timestamp = ctx.message.created_at)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)    
            embed.add_field(name="Description\n", value ='{}'.format(f[argument]["fields"][argument2]["value"]), inline=False)
            embed.add_field(name="Usage\n",value = '`{}`'.format(f[argument]["fields"][argument2]["usage"]), inline=False)


        elif argument in f and argument2 not in f[argument]["fields"]:
            embed = discord.Embed(timestamp = ctx.message.created_at)
            embed.add_field(name=f"Error",value=f"No sub-category named '{argument2}'")

        elif argument not in f:
            embed = discord.Embed(timestamp = ctx.message.created_at)
            embed.add_field(name=f"Error",value=f"No category named '{argument}'")

        await ctx.send(embed = embed)
def setup(bot):
    bot.add_cog(help(bot))