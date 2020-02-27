import discord

from utils_folder import permissions
from discord.ext.commands import AutoShardedBot, DefaultHelpCommand
import os

class Bot(AutoShardedBot):
    def __init__(self, *args, prefix=None, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_message(self, msg):
        if not self.is_ready() or msg.author.bot or not permissions.can_send(msg):
            return

        await self.process_commands(msg)


class HelpCommand(DefaultHelpCommand):
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title = "ALBEDO COMMAND LIST", 
        description = "Albedo has a huge variety of commands. You can use the help command to navigate through them. ",
        color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
        
        for cog in mapping.keys():
            if cog != None :    
                if cog.qualified_name != "debugmode":
                    commands = ''
                    for command in mapping[cog]:
                        commands += f"_{str(command)}_|"
                    embed.add_field(name = "**{}**".format(cog.qualified_name.upper()), value = f"`{self.clean_prefix}help {cog.qualified_name}`\n", inline= False)
            elif cog == None:
                pass

        await ctx.send(embed = embed)

    async def send_command_help(self, command):
        ctx = self.context

        embed = discord.Embed(
            title = f"{self.clean_prefix} {str(command)} info", 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        signature = self.get_command_signature(command)
        embed.add_field(name = "Usage", value = "`{}`".format(signature), inline=False)

        try:
            embed.add_field(name = "Description", value = command.help if command.help else "Gonna write dis shit later boya")
        except RuntimeError:
            for line in command.help.splitlines():
                embed.add_field(name = command, value = line)

        await ctx.send(embed = embed)

    async def send_group_help(self, group):
        ctx = self.context
        signature = self.get_command_signature(group)
        if group.help != None:
            description = group.help + "\n`{}`".format(signature)
        else:
            description = "`{}`".format(signature)
        embed = discord.Embed(
            title = str(group).upper(),
            description = description if group.help else "`{}`".format(signature), 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        for command in filtered:
            embed.add_field(name = f"**{command.name}**", value = "_{}_".format(command.help if command.help else "Crap, forgot to write this shit"), inline=False)

        await ctx.send(embed = embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        
        # if cog.qualified_name.lower() in admin_only:
        #     if ctx.bot.is_owner(ctx.author):
        #         pass
        #     else:
        #         return
        
        embed = discord.Embed(
            title = cog.qualified_name.upper(),
            description = cog.description if cog.description else "", 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        for command in filtered:
            embed.add_field(name = f"**{command.name}**", value = "_{}_".format(command.help if command.help else "Crap, forgot to write this shit"), inline=False)

        await ctx.send(embed = embed)

class HelpFormat(DefaultHelpCommand):
    def get_destination(self, no_pm: bool = False):
        if no_pm:
            return self.context.channel
        else:
            return self.context.author

    async def send_error_message(self, error):
        destination = self.get_destination(no_pm=True)
        await destination.send(error)

    async def send_command_help(self, command):
        self.add_command_formatting(command)
        self.paginator.close_page()
        await self.send_pages(no_pm=True)

    async def send_pages(self, no_pm: bool = False):
        try:
            if permissions.can_react(self.context):
                await self.context.message.add_reaction(chr(0x2709))
        except discord.Forbidden:
            pass

        try:
            destination = self.get_destination(no_pm=no_pm)
            for page in self.paginator.pages:
                await destination.send(page)
        except discord.Forbidden:
            destination = self.get_destination(no_pm=True)
            await destination.send("Couldn't send help to you due to blocked DMs...")

class _states:
    ''' contains the states for an instance of bot '''
    __slots__ = ('states')
    def __init__(self):
        self.states = {}

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState(guild)
            return self.states[guild.id]

    def delete_state(self, guild):
        """Delete the state of a guild"""
        del self.states[guild.id]
        
    def all_states(self):
        return self.states

class GuildState:
    ''' This class manages per-guild states '''
    __slots__ = ('server', 'roles', 'volume', 'playlist', 'skip_votes', 'now_playing', 'loop', 'temp', 'loopall', 'prefix', 'mute_exists', 'debugmode', 'desc')
    def __init__(self, server):
        self.server = server
        self.roles = server.roles
        self.volume = 1
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None
        self.loop = False
        self.temp = False
        self.loopall = False 
        self.prefix = "/"
        self.mute_exists = False
        self.debugmode = False
        self.desc = True

    def is_requester(self, user):
        return self.now_playing.requested_by == user
    
    def is_song_requester(self, user, index):
        return self.playlist[index].requested_by == user

    def get_var(self, variable):
        var = getattr(self, variable)
        return var
    
    def set_var(self, variable, value):
        setattr(self, variable, value)
        return

state_instance = _states()