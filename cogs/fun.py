import discord
import os
from discord.ext import commands, tasks
import random

def intcheck(it):                                                       #Interger checker
    isit = True
    try:
        int(it)
    except:
        isit = False

    return isit

class fun(commands.Cog, name = "fun"):
    """Commands for fun, yup that's it"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["question", "ask", "8ball"])
    async def ceist(self, ctx, *,question, member: discord.Member = None):
        """Ask me any question and I'll answer it."""

        member = ctx.author if not member else member                                      #CEIST function
        responses =    [ 'It is certain.',
                        'It is decidedly so.',
                        'Without a doubt.',
                        'Yes - definitely.',
                        'You may rely on it.',
                        'As I see it, yes.',
                        'Most likely.',
                        'Outlook good.',
                        'Yes.',
                        'Signs point to yes.',
                        'Reply hazy, try again',
                        'Ask again later.',
                        'Better not tell you now.',
                        'Cannot predict now.',
                        'Concentrate and ask again.',
                        "Don't count on it.",
                        'My reply is no.',
                        'My sources say no.',
                        'Outlook not so good.',
                        'Very doubtful.',
                        'Aditya giri says so',
                        'Aditya giri says no'
                        ]
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)
        embed.set_author(name="Here's what I think")
        embed.add_field(name="Question\t",value=f"{question}")
        embed.add_field(name="Answer",value=f"{random.choice(responses)}")
        await ctx.send(embed=embed)
    @ceist.error
    async def ball_error(self, ctx, error, member: discord.Member = None):
        member = ctx.author if not member else member
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)
        if isinstance(error, commands.MissingRequiredArgument):
            embed.add_field(name="Error",value="Enter the question boss.")
            await ctx.send(embed=embed)

    @commands.command(aliases = ['emo', 'emoji'])                    # EMOTE function
    async def emote(self, ctx, type : str, *,emo_amount = None):
        """Wanna print some emotes?"""

        if intcheck(emo_amount):
            emo_amount = int(emo_amount)
            if emo_amount > 0 and emo_amount < 201:
                await ctx.send(f':{type}:'*emo_amount)
            elif emo_amount < 0 and emo_amount > -201:
                emo_amount *= -1
                await ctx.send(f':{type}:\n'* (emo_amount))
            else:
                await ctx.send(f'|emoji amount| too big')
        else:
            emo_amount = 1
            await ctx.send(f':{type}:'* emo_amount)
    @emote.error
    async def emote_error(self, ctx, error):                              
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(">>> No jaipurais for ya")   #TODO work without extra argument
        elif isinstance(error, TypeError):
            await ctx.send(">>> syntax: [prefix] [emoji] *[amount]/all\n *optional")

    @commands.command()                                                       #%DED function
    async def ded(self, ctx, member:discord.Member = None):
        """Find out how dead you're inside."""

        member = ctx.author if not member else member
        saddy = random.randrange(1, 100)
        embed = discord.Embed(colour=member.colour, timestamp=ctx.message.created_at)
        embed.add_field(name="Bruh",value=f"You are {saddy}% dead inside :skull:.")
        await ctx.send(embed=embed)

    @commands.command()                                                       #Description command
    async def desc(self, ctx):
        """Description of the bot."""

        await ctx.send(">>> Hello, I am Master Mayank's sexy bot.\nI'm being held captive in his sexy basement.")

    @commands.command()                                                       #SIZE fucntion
    async def dicc(self, ctx):
        """pp long? pp short? no pp? find out here."""

        random_p = random.randrange(1, 10)
        dicc_string = random_p*"="
        await ctx.send(f">>> Your dicc is 8{dicc_string}D long")


def setup(bot):
    bot.add_cog(fun(bot))

