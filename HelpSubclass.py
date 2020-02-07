import discord
from discord.ext import commands
import itertools

class HelpCommand(commands.DefaultHelpCommand):
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title = "BOT COMMAND LIST", 
        description = "This is the help command of this bot. This bot has a huge variety of commands. You can use this help command to navigate through them. ",
        color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)
        
        for cog in mapping.keys():
            if cog != None :    
                if cog.qualified_name != "debugmode":
                    commands = ''
                    for command in mapping[cog]:
                        commands += f"_{str(command)}_|"
                    embed.add_field(name = "**{}**".format(cog.qualified_name.upper()), value = f"`ss help {cog.qualified_name}`\n", inline= False)
            elif cog == None:
                pass

        await ctx.send(embed = embed)

    async def send_command_help(self, command):
        ctx = self.context

        embed = discord.Embed(
            title = str(command).upper(), 
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
        # self.add_command_formatting(group)

        # filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        # self.add_indented_commands(filtered, heading=self.commands_heading)

        # if filtered:
        #     note = self.get_ending_note()
        #     if note:
        #         self.paginator.add_line()
        #         self.paginator.add_line(note)

        # await self.send_pages()
        pass

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = discord.Embed(
            title = cog.qualified_name.upper(),
            description = cog.description if cog.description else "", 
            color = discord.Colour.from_rgb(0,250,141), timestamp = ctx.message.created_at)

        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        for command in filtered:
            embed.add_field(name = f"**{command.name}**", value = "_{}_".format(command.help if command.help else "Crap, forgot to write this shit"), inline=False)

        await ctx.send(embed = embed)
