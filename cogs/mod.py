import discord
from discord.ext import commands
from discord.utils import get
from my_utils.guildstate import state_instance
from my_utils.default import intcheck, get as default_get
import os
from my_utils import permissions

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
    @permissions.has_permissions(perms="kick_members")
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kick the mentioned user, requires you to have kick members permission"""
        
        member_name = member.name
        if await permissions.check_priv(ctx, member) != None:
            return
        await ctx.send(f">>> Kicked {member_name}")
        await member.kick(reason = reason)

    @commands.command(aliases = ['bann'], hidden = False)
    @permissions.has_permissions(perms="ban_members")
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        """Ban the mentioned user, requires you to have ban members permission"""
        
        member_name = member.name
        if await permissions.check_priv(ctx, member) != None:
            return
        await ctx.send(f">>> banned {member_name}")
        await member.ban(reason = reason)

    @commands.command(hidden = False)
    @permissions.has_permissions(perms="ban_members")
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

    @commands.command(aliases = ['silent'], hidden = False)
    @commands.check(check_mute)
    @permissions.has_permissions(perms="administrator")
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member):
        """Server mute the mentioned user(only text channels), requires you to have administrator"""

        guild_state = state_instance.get_state(ctx.guild)
        text_channels = ctx.guild.text_channels
        mute_role = None
        if await permissions.check_priv(ctx, member) != None:
            return
        if guild_state.mute_exists:
            mute_role = get(ctx.guild.roles, name = "Muted")
        else:
            mute_role = await ctx.guild.create_role(name = "Muted")
            for channel in text_channels:
                await channel.set_permissions(mute_role, send_messages=False, manage_permissions=False, manage_channels=False, manage_webhooks=False)
            guild_state.mute_exists = True

        await member.add_roles(mute_role)
        await ctx.send(f"Muted {member.name}")
    
    @commands.command(aliases = ['unmut'], hidden = False)
    @permissions.has_permissions(perms="administrator")
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member):
        """Unmute the mentioned user, requires you to have administrator"""
        if await permissions.check_priv(ctx, member) != None:
            return
        for role in member.roles[::-1]:
            if role.name == "Muted":
               await ctx.send(f">>> Unmuted f{member.name}")
               return await member.remove_roles(role)
        return await ctx.send(f">>> {member.name} was not even muted")

    @commands.command(aliases = ['purge'], hidden = False)   
    @permissions.has_permissions(perms="manage_messages")                            #CLEAR function
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
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> Enter the amount of mesages to be cleared.")

def setup(bot):
    bot.add_cog(mod(bot))

