import discord
from discord.ext import commands, tasks

class debugmode(commands.Cog):
    """This is only for debugging purposes"""

    def __init__(self, bot):
        self.bot = bot
         
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(">>> Command not found.")
    

def setup(bot):
 bot.add_cog(debugmode(bot))

