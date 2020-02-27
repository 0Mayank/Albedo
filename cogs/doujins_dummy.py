from discord.ext import commands

class doujinshi(commands.Cog):
    """Commands for reading doujinshis straight from nhentai"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases = ['rand'])
    async def random(self, ctx):
        """Get random doujinshi"""
        pass

    @commands.command()
    async def read(self, ctx, ID):
        """Read doujinshi by the Id you provided"""
        pass

    @commands.command(aliases = ['dl'])
    async def download(self, ctx, ID):
        """Download doujinshi by the Id you provided"""
        pass

    @commands.command(aliases = ['lang'])
    async def language(self, ctx, language):
        """Get random doujinshi by the language you provided.
        Example: <chinese/english/japenese> or <ch/en/jp>."""
        pass

    @commands.command(aliases = ['par'])
    async def parody(self, ctx, name, language):
        """Get random doujin with provide name and language"""
        pass


def setup(bot):
    bot.add_cog(doujinshi(bot))