import discord
from discord.ext import commands

import requests

from bs4 import BeautifulSoup
import json
import asyncio
from my_utils import default as d



async def get_waifu():
    while 5:
        source = requests.get("https://mywaifulist.moe/random")
        source = requests.get(str(source.url))
        soup = BeautifulSoup(source.text, 'lxml')
        data = str((soup.find('script', type='application/ld+json')))
        strip_data = data[40:-14]
        json_data = json.loads(strip_data)
        if json_data['gender'] == 'female':
            return json_data['name'], json_data['image'], json_data['url']
        else:
            continue
    

class anime(commands.Cog):
    """yes weebs"""
    
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command = True)
    async def anime(self, ctx, *, query):
        url = "https://jikan1.p.rapidapi.com/search/anime"

        querystring = {"q":str(query)}

        headers = {
            'x-rapidapi-host': "jikan1.p.rapidapi.com",
            'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
            }

        response = requests.request("GET", url, headers=headers, params=querystring).json()
        
        async with ctx.channel.typing():
            txt = "**Select an anime from the following results by responding with an integer:**\n"
            max_ind = 0
            for i in range(10):
                try:
                    txt += f"**{i+1}**. {response['results'][i]['title']}\n"
                    max_ind += 1
                except IndexError:
                    break
            if max_ind != 0:
                mes = await ctx.send(txt)
                
                try:
                    def mcheck(message):
                        if message.author == ctx.author and message.channel == ctx.channel:
                            return True
                        return False

                    try:
                        answer = await self.bot.wait_for('message', timeout=20, check=mcheck)

                    except asyncio.TimeoutError:
                        return await ctx.send("You didn't respond in time.")

                    content = answer.content.strip()
                    if not content.isnumeric():
                        return await ctx.send("Respond with an integer")

                    if d.intcheck(content) and int(content) <= max_ind and int(content) > 0:
                        
                        async with ctx.channel.typing():
                                        
                            image = response["results"][int(content)-1]["image_url"]
                            title = response["results"][int(content)-1]["title"]
                            episodes = response["results"][int(content)-1]["episodes"]
                            score = response["results"][int(content)-1]["score"]
                            desc = response["results"][int(content)-1]["synopsis"]
                            url = response["results"][int(content)-1]["url"]

                            embed = discord.Embed(
                                title = title,
                                color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at,
                                url = url,
                                description = desc
                                )       
                            embed.add_field(name="Episodes", value= episodes)
                            embed.add_field(name="Score", value = score)
                            embed.set_footer(text=f"Source MAL | Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                            embed.set_image(url=image)
                            try:
                                await answer.delete()
                            except:
                                pass
                            await mes.edit(embed=embed, content=None)
                    else:
                        return await ctx.send("You are proving me stupid for letting you use my commands")
                            
                except IndexError:
                    await ctx.send("No result found")
            else:
                await ctx.send("No results found")
        
        
    @anime.command(aliases=["sch"])
    async def schedule(self, ctx, query:str):
        try:
            url = f"https://jikan1.p.rapidapi.com/schedule/{query}"

            headers = {
                'x-rapidapi-host': "jikan1.p.rapidapi.com",
                'x-rapidapi-key': "1adab39b32msh3ace9d305db7522p133436jsn292ad15e4db3"
                    }

            response = requests.request("GET", url, headers=headers).json()
        
            result = response[query]
            embed = discord.Embed(
                title=f"Schedule for {query}",
                color = discord.Colour.from_rgb(0,250,141)
            )
            x = len(result) % 3
            for i in range(len(result)):
                embed.add_field(name='\u200b', value = f'• {result[i]["title"]}')

            if x:
                for _ in range(x):
                    embed.add_field(name="\u200b", value = "\n\u200b")

            embed.set_footer(text=f"Source MAL | Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("Invalid day")

    @commands.group(invoke_without_command = True, pass_context = True)
    async def waifu(self, ctx):
        name, image_url, url = await get_waifu()
        
        embed = discord.Embed(
            title=f"{name}",
            color = discord.Colour.from_rgb(0,250,141),
            timestamp=ctx.message.created_at,
            url=url
        )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_image(url=image_url)
        embed_react = await ctx.send(embed=embed)

        await embed_react.add_reaction('⭐')
        reacted = [self.bot.user]
        def rcheck(reaction, user):
            print(reaction.message.embeds[0].to_dict())
            if str(reaction.emoji) == '⭐' and user not in reacted and reaction.message.embeds[0].to_dict()['timestamp'] == embed.to_dict()['timestamp'] and reaction.message.embeds[0].to_dict()['footer']['text'] == embed.to_dict()['footer']['text']:
                reacted.append(user)
                return True
            return False
        
        while 1:
            try:
                _, user = await self.bot.wait_for('reaction_add', timeout=60, check=rcheck)
            except asyncio.TimeoutError:
                try:
                    await embed_react.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                break

            _id = str(user.id)
            profiles = d.retrieve("waifu.json")
            if _id in profiles:
                profiles = d.retrieve("waifu.json")
                profiles[_id].append(f"{name} {image_url}")
                d.save("waifu.json", profiles)

            elif _id not in profiles:
                profiles = d.retrieve("waifu.json")
                profiles[_id] = [f"{name} {image_url}"]
                d.save("waifu.json", profiles)
        
            await ctx.send(f"**{name}** added to <@!{int(user.id)}> favourite list!")

    @waifu.command(aliases=['fav'])
    async def favourite(self, ctx):
        ind = 0
        async def info(index):
            profiles = d.retrieve("waifu.json")
            query = profiles[str(ctx.message.author.id)][index]
            temp = query.split(' ')
            
            image_url = temp[len(temp)-1]
            temp.pop(len(temp)-1) 
            name = ""
            for i in temp:
                name += i+" "
            
            d.save("waifu.json", profiles)
            return name, image_url
            

        async def emoji(message):
            emo = ['◀️','▶️','🗑️']
            for i in emo:
                await message.add_reaction(i)

        async def edit_embed(index):
            try:
                name, image_url = await info(index)
                embed = discord.Embed(
                title=f"{name}",
                color = discord.Colour.from_rgb(0,250,141),
                timestamp=ctx.message.created_at,
                )
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                embed.set_image(url=image_url)
          
                return embed

            except ValueError:
                embed_error = await info(index)
                return embed_error

        def rcheck(reaction, user):
            reacted = [self.bot.user]
            try: 
                if str(reaction.emoji) == '▶️' or str(reaction.emoji) == '◀️' or str(reaction.emoji) == '🗑️' and reaction.message.embeds[0].to_dict()['timestamp'] == embed.to_dict()['timestamp'] and reaction.message.embeds[0].to_dict()['footer']['text'] == embed.to_dict()['footer']['text']:
                    if user not in reacted:
                        reacted.append(user)
                        return True
            except: 
                pass
            return False
        try:
            name, image_url = await info(0)
            embed = discord.Embed(
                title=f"{name}",
                color = discord.Colour.from_rgb(0,250,141),
                timestamp=ctx.message.created_at,
            )
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.set_image(url=image_url)

            embed_react = await ctx.send(embed=embed)
            
            await emoji(embed_react)

        except IndexError:
            embed = discord.Embed(
                    title = "Favourite list is empty ;-;"
                )
            await ctx.send(embed=embed)

        while 1:
            # ind = 0
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=rcheck)
            except asyncio.TimeoutError:
                try:
                    await embed_react.clear_reactions()
                except discord.errors.Forbidden:
                    pass
                break
            if str(reaction.emoji) == '▶️' and user == ctx.author:
                ind += 1
                # name, image_url = await info(ind)
                try:
                    r = await edit_embed(ind)
                    await embed_react.edit(embed=r)
                except IndexError:
                    ind -= 1
                    r = await edit_embed(ind)
                    await embed_react.edit(embed=r)

            elif str(reaction.emoji) == '◀️' and user == ctx.author:
                ind -= 1
                try:
                    r = await edit_embed(ind)
                    await embed_react.edit(embed=r)
                except IndexError:
                    ind += 1
                    r = await edit_embed(ind)
                    await embed_react.edit(embed=r)

            elif str(reaction.emoji) == '🗑️' and user == ctx.author:
                profiles = d.retrieve("waifu.json")
                l_query = profiles[str(ctx.message.author.id)]
                actual_l = len(l_query)
                if actual_l != 0:
                    await ctx.send(f"**{name}** got eliminated from <@!{int(user.id)}> favourite list.")
                    try:    
                        query = profiles[str(ctx.message.author.id)][ind]
                        temp = query.split(' ')
                        name = temp[0] 
                        profiles[str(ctx.message.author.id)].pop(ind)
                        ind -= 1
                    except:
                        profiles[str(ctx.message.author.id)] = []
                    
                    if len(profiles[str(ctx.message.author.id)]) != 0:
                        r = await edit_embed(ind)
                        await embed_react.edit(embed=r)
                    else:
                        embed = discord.Embed(
                        title = "Favourite list is empty  ;-;"
                        )
                        ind += 1
                        d.save("waifu.json", profiles)
                        await embed_react.edit(embed=embed)
                        try:
                            await embed_react.clear_reactions()
                        except:
                            pass
                        break
                else:
                    embed = discord.Embed(
                    title = "Favourite list is empty  ;-;"
                    )
                    await ctx.send(embed=embed)
                d.save("waifu.json", profiles)
def setup(bot):
    bot.add_cog(anime(bot))