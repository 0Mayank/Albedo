import os

import discord
from discord.ext import commands, tasks
from discord.utils import oauth_url

from my_utils import default as d
from my_utils.guildstate import state_instance

config = d.get("config.json")

al_admins = config.almins

class meta(commands.Cog):    
    """Contains the general commands or the commands related to the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def prefix(self, ctx, *, prefix = None):
        """Gets the current prefix or changes the prefix"""

        embed = discord.Embed(color = discord.Colour.from_rgb(0, 0, 0), timestamp = ctx.message.created_at)
        state = state_instance.get_state(ctx.guild)
        if prefix == None:
                embed.add_field(name="Current Prefix", value=f"Current prefix `{state.prefix}`", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        elif prefix != None:
            if ctx.message.author.id in al_admins:
                state.prefix = prefix
                embed.add_field(name="Prefix", value=f"Prefix changed to `{state.prefix}`", inline=False)
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                print("prefix changed to {} in {}".format(prefix,ctx.guild))
            else:
                embed = discord.Embed(title="You thought you could do that, how gae.", timestamp = ctx.message.created_at)
    
        await ctx.send(embed=embed)

    @commands.command()
    async def botinvite(self, ctx):
        """Sends the invite link of the bot"""

        await ctx.send(oauth_url(self.bot.user.id, permissions=discord.Permissions(permissions=8), guild=None, redirect_uri=None))

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at)
        embed.add_field(name="Bot ping",value=f"{round(self.bot.latency*1000)}ms")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(d.check_availabilty)                                                       #Description command
    async def desc(self, ctx, *, random_stuff = None):
        """Description of the bot."""

        await ctx.send(">>> I love Ainz sama")
    @desc.error
    async def desc_error(self, ctx):
        pass

    @commands.command()
    async def enable(self, ctx, command):
        """Enables a given command"""
        try:
            state = state_instance.get_state(ctx.guild)
            state.set_var(command, True)
            await ctx.send(f"enabled {command}")
        except:
            await ctx.send(f"No command {command} found")

    @commands.command()
    async def disable(self, ctx, command):
        """disables a given command"""
        try:
            state = state_instance.get_state(ctx.guild)
            state.set_var(command, False)
            await ctx.send(f"disabled {command}")
        except:
            await ctx.send(f"No command {command} found")

def setup(bot):
    bot.add_cog(meta(bot))
