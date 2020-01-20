import discord
from discord.ext import commands, tasks

class administrative(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['kick'])                                     #KICK function
    async def _kick(self, ctx, member: discord.Member, *, reason = None):
        await member.kick(reason = reason)

    @commands.command(aliases = ['ban'])                                      #BAN function
    async def _ban(self, ctx, member: discord.Member, *, reason = None):
        await member.ban(reason = reason)

    @commands.command()
    async def unban(self, ctx, *, member):                                        #UNBAN function
        banned_users = await ctx.guild.ban()
        name, discriminator = member.split('#')
        for ban_entry in banned_users():
            user = ban_entry.user
            if (user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f">>> Unbanned {user.name}#{user.discriminator}")
                return

def setup(bot):
    bot.add_cog(administrative(bot))

