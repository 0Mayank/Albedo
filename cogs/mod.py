import discord
from discord.ext import commands
from discord.utils import get
from utils_folder.data import state_instance
from utils_folder.default import intcheck, get as default_get
import tracemalloc
import os
tracemalloc.start()

config = default_get("config.json")

al_admins = config.almins

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
    """Bot commands for moderation"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['kikc'], hidden = False)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kick the mentioned user, requires you to have kick members permission"""
        
        member_name = member.name
        roles = state_instance.get_state(ctx.guild).roles
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to kick someone superior to you, futile attempts")
        if member.id in al_admins:
            return await ctx.send(f"Sorry, i will not betray my masters at any cost")
        await ctx.send(f">>> Kicked {member_name}")
        await member.kick(reason = reason)
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(aliases = ['bann'], hidden = False)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        """Ban the mentioned user, requires you to have ban members permission"""
        
        member_name = member.name
        roles = state_instance.get_state(ctx.guild).roles
        if ctx.author.id == member.id:
            return await ctx.send("Yamete, here is the suicide prevention helpline: ")
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to ban someone superior to you, futile attempts")
        if member.id in al_admins:
            return await ctx.send(f"Sorry, i will not betray my masters at any cost")
        await ctx.send(f">>> banned {member_name}")
        await member.ban(reason = reason)
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(hidden = False)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member):
        """Unban the user(provide the complete username and discriminator), requires you to have ban members permission"""
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

    @commands.command(aliases = ['silent'], hidden = False)
    @commands.check(check_mute)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member):
        """Server mute the mentioned user(only text channels), requires you to have administrator"""

        guild_state = state_instance.get_state(ctx.guild)
        roles = guild_state.roles
        text_channels = ctx.guild.text_channels
        mute_role = None
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to mute someone superior to you, futile attempts")
        if guild_state.mute_exists:
            mute_role = get(ctx.guild.roles, name = "Muted")
        else:
            await ctx.guild.create_role(name = "Muted")
            mute_role = get(ctx.guild.roles, name = "Muted")
            for channel in text_channels:
                await channel.set_permissions(mute_role, send_messages=False, manage_permissions=False, manage_channels=False, manage_webhooks=False)
            guild_state.mute_exists = True

        await member.add_roles(mute_role)
        await ctx.send(f"Muted {member.name}")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")
    
    @commands.command(aliases = ['unmut'], hidden = False)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member):
        """Unmute the mentioned user, requires you to have administrator"""

        guild_state = state_instance.get_state(ctx.guild)
        roles = guild_state.roles
        if not role_is_higher(roles, ctx.author, member):
            return await ctx.send(f"Ara Ara, f{ctx.author.name} looks like you are trying to mute someone superior to you, futile attempts")
        for role in member.roles[::-1]:
            if role.name == "Muted":
               await ctx.send(f">>> Unmuted f{member.name}")
               return await member.remove_roles(role)
        return await ctx.send(f">>> {member.name} was not even muted")

    @mute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(">>> Heck, looks like you are missing some permissions.")

    @commands.command(aliases = ['purge'], hidden = False)   
    @commands.has_permissions(manage_messages = True)                            #CLEAR function
    async def clear(self, ctx, amount, *, someBullshit = None):
        """Clear the given amount of messages(all for deleting 200 messages)"""
        
        if intcheck(amount):
            await ctx.channel.purge(limit = int(amount)+1)
            await ctx.send(f">>> {amount} messages deleted boss.", delete_after = 5)
        elif amount == "all":
            await ctx.channel.purge(limit = 201)
            await ctx.send(f">>> 200 messages deleted boss.", delete_after = 5)
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send(">>> Heck, looks like you are missing some permissions.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> Enter the amount of mesages to be cleared.")

def setup(bot):
    bot.add_cog(mod(bot))

