import discord
import os
from discord.ext import commands, tasks
from guildstate import state_instance
from discord.utils import oauth_url

sexy_admins = os.environ.get("SEXY_ADMINS").split()

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
            if str(ctx.message.author.id) in sexy_admins:
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


def setup(bot):
    bot.add_cog(meta(bot))