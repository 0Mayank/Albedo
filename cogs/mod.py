import discord
from discord.ext import commands
from discord.utils import get
from guildstate import state_instance
import utils as u
import tracemalloc
import os
tracemalloc.start()

sexy_admins = os.environ.get("SEXY_ADMINS").split()

def role_is_higher(roles, author, member):
    a_role = roles.index(author.top_role)
    m_role = roles.index(member.top_role)
    if a_role > m_role:
        return True
    return False
def check_mute(ctx):
    gstate = state_instance.get_state(ctx.guild)
    roles = gstate.roles
    for role in roles:
        if role.name == "Muted":
            gstate.mute_exists = True
            break
    return True

class mod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['kikc'])
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        roles = state_instance.get_state(ctx.guild).roles
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to kick someone superior to you, futile attempts")
        if str(member.id) in sexy_admins:
            return await ctx.send(f"Sorry, i will not betray my masters at any cost")
        await ctx.send(f">>> just pretended to kick {str(member)}")
        await member.kick(reason = reason)
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(aliases = ['bann'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        roles = state_instance.get_state(ctx.guild).roles
        if ctx.author.id == member.id:
            return await ctx.send("Yamete, here is the suicide prevention helpline: ")
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to ban someone superior to you, futile attempts")
        if str(member.id) in sexy_admins:
            return await ctx.send(f"Sorry, i will not betray my masters at any cost")
        await ctx.send(f">>> banned {str(member)} for ya")
        await member.ban(reason = reason)
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.ban()
        name, discriminator = member.split('#')
        for ban_entry in banned_users():
            user = ban_entry.user
            if (user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f">>> Unbanned {user.name}#{user.discriminator}")
                return
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(aliases = ['silent'])
    @commands.check(check_mute)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member):
        guild_state = state_instance.get_state(ctx.guild)
        roles = guild_state.roles
        text_channels = ctx.guild.text_channels
        mute_role = None
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to mute someone superior to you, futile attempts")
        if guild_state.mute_exists:
            mute_role = get(ctx.guild.roles, name = "Muted")
            await member.add_roles(mute_role)
        else:
            await ctx.guild.create_role(name = "Muted")
            mute_role = get(ctx.guild.roles, name = "Muted")
            for channel in text_channels:
                await channel.set_permissions(mute_role, send_messages=False, manage_permissions=False)
            await member.add_roles(mute_role)
            guild_state.mute_exists = True
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")
    
    @commands.command(aliases = ['unmut'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member):
        guild_state = state_instance.get_state(ctx.guild)
        roles = guild_state.roles
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to mute someone superior to you, futile attempts")
        for role in member.roles[::-1]:
            if role.name == "Muted":
                await member.remove_roles(role)
                break
    @mute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(aliases = ['purge'])                               #CLEAR function
    async def clear(self, ctx, amount, *, someBullshit = None):
        if u.intcheck(amount):
            await ctx.channel.purge(limit = int(amount)+1)
            await ctx.send(f">>> {amount} messages deleted boss.")
        elif amount == "all":
            await ctx.channel.purge(limit = 201)
            await ctx.send(f">>> 200 messages deleted boss.")
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> Enter the amount of mesages to be cleared.")

def setup(bot):
    bot.add_cog(mod(bot))

