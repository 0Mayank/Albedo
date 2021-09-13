import discord
from discord.ext import commands

import requests

from bs4 import BeautifulSoup
import json
import asyncio
from my_utils import default as d
from my_utils.default import get

# bearer_token = get("config.json").token[2]
# refresh_token = get("config.json").token[3]
client_id = get("config.json").client[0]
client_secret = get("config.json").client[1]

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

def update_token():
    data = d.retrieve("token.json")

    refresh_token = data["refresh"]
    param = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    url = f"https://myanimelist.net/v1/oauth2/token?"
    response = requests.post(url, param).json()

    data["bearer"] = response["access_token"]
    data["refresh"] = response["refresh_token"]
    d.save("token.json", data)

class anime(commands.Cog):
    """yes weebs"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def anime(self, ctx, *, query):

        async def anime_exec(self, ctx, response):
            async with ctx.channel.typing():
                txt = "**Select an anime from the following results by responding with an integer:**\n"
                max_ind = 0
                for i in range(10):
                    try:
                        txt += f"**{i+1}**. {response['data'][i]['node']['title']}\n"
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
                                anime_id = response['data'][int(content)-1]['node']['id']
                                new_url = f'https://api.myanimelist.net/v2/anime/{anime_id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics'
                                bearer_token = get("json/token.json").bearer
                                new_headers = {
                                            "Authorization": f"Bearer {get('json/token.json').bearer}"
                                        }

                                new_response = requests.request("GET", new_url, headers=new_headers).json()

                                def ran_out_vars(more_var):
                                    this = assign([more_var])
                                    if this != "`"+"N/A"+"`":
                                        try:
                                            var_str = ""
                                            for i in range(len(this)):
                                                var_str += "`"+this[i]['name']+"`" + " "
                                            return var_str
                                        except KeyError:
                                            return "`"+"N/A"+"`"
                                    return "`"+"N/A"+"`"

                                def assign(path):
                                    dcopy = new_response
                                    for key in path:
                                        if key in dcopy:
                                            if dcopy[key]:
                                                dcopy = dcopy[key]
                                            else:
                                                return '`'+'N/A'+'`'  
                                        else:
                                            return '`'+'N/A'+'`'  
                                    return dcopy

                                image = assign(["main_picture", "large"])
                                title = assign(["title"])
                                popularity = "`"+str(assign(["popularity"]))+"`"
                                ja_title = assign(["alternative_titles", "ja"])
                                status = "`"+assign(["status"])+"`"
                                episodes = "`"+str(assign(["num_episodes"]))+"`"
                                score = "`"+str(assign(["mean"]))+"`"
                                desc = assign(["synopsis"])
                                rating = "`"+str(assign(["rating"])).capitalize()+"`"
                                rank = "`"+str(assign(['rank']))+"`"
                                genres = ran_out_vars("genres")
                                studios = ran_out_vars("studios")
                                aired = "`"+str(assign(["start_date"]))+"`"
                                end = "`"+str(assign(["end_date"]))+"`"

                                if (assign(['start_season', 'season'])) != '`'+'N/A'+'`':
                                    premiered = "`"+(assign(['start_season', 'season']))[0].upper() + (assign(['start_season', 'season']))[1:] + " " + str(assign(['start_season', 'year']))+"`"
                                else:
                                    premiered = '`'+'N/A'+'`'

                                if assign(['broadcast', 'day_of_the_week']) != '`'+'N/A'+'`':
                                    broadcast = "`"+assign(['broadcast', 'day_of_the_week']).capitalize()+" "+assign(['broadcast', 'start_time'])+"`"
                                else:
                                    broadcast = '`'+'N/A'+'`'

                                embed = discord.Embed(
                                    title = title+" "+"("+ja_title+")",
                                    color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at,
                                    description = f"**Synopsis**\n\n{desc}"
                                    )       
                                embed.add_field(name="Episodes", value= episodes)
                                embed.add_field(name="Score", value = score)
                                embed.add_field(name="Status", value=status)
                                embed.add_field(name="Popularity", value=popularity)
                                embed.add_field(name="Aired", value=aired)
                                embed.add_field(name="End", value=end)
                                embed.add_field(name="Broadcast", value=broadcast)
                                embed.add_field(name="Genre", value=genres)
                                embed.add_field(name="Studio", value=studios)
                                embed.add_field(name="Rank", value=rank)
                                embed.add_field(name="Premiered", value=premiered)
                                embed.add_field(name="Age rating", value=rating)
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
        
        url = f'https://api.myanimelist.net/v2/anime?q={query}'
        headers = {
            "Authorization": f"Bearer {get('json/token.json').bearer}"
        }
        old_response = requests.request("GET", url, headers=headers).json()
        if "error" in old_response:
            update_token()

            url = f'https://api.myanimelist.net/v2/anime?q={query}'
            headers = {
                "Authorization": f"Bearer {get('json/token.json').bearer}"
            }
            response = requests.request("GET", url, headers=headers).json()

            await anime_exec(self, ctx, response)
        else:
            url = f'https://api.myanimelist.net/v2/anime?q={query}'
            headers = {
                "Authorization": f"Bearer {get('json/token.json').bearer}"
            }
            response = requests.request("GET", url, headers=headers).json()
            await anime_exec(self, ctx, response)


    @commands.command()
    async def manga(self, ctx, *, query):
        async def manga_exec(self, ctx, response):
            async with ctx.channel.typing():
                txt = "**Select an anime from the following results by responding with an integer:**\n"
                max_ind = 0
                for i in range(10):
                    try:
                        txt += f"**{i+1}**. {response['data'][i]['node']['title']}\n"
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
                                manga_id = response['data'][int(content)-1]['node']['id']
                                new_url = f'https://api.myanimelist.net/v2/manga/{manga_id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_volumes,num_chapters,authors{{first_name,last_name}},pictures,background,related_anime,related_manga,recommendations,serialization{{name}}'

                                new_headers = {
                                            "Authorization": f"Bearer {get('json/token.json').bearer}"
                                        }

                                new_response = requests.request("GET", new_url, headers=new_headers).json()

                                def ran_out_vars(more_var):
                                    this = assign([more_var])
                                    if this != '`'+'N/A'+'`':
                                        try:
                                            var_str = ""
                                            for i in range(len(this)):
                                                var_str += "`"+this[i]['name']+"`" + " "
                                            return var_str
                                        except KeyError:
                                            return "`"+"N/A"+"`"
                                    return "`"+"N/A"+"`"

                                def assign(path):
                                    dcopy = new_response
                                    for key in path:
                                        if key in dcopy:
                                            if dcopy[key]:
                                                dcopy = dcopy[key]
                                            else:
                                                return '`'+'N/A'+'`'
                                        else:
                                            return '`'+'N/A'+'`'
                                    return dcopy

                                image = assign(["main_picture", "large"])
                                title = assign(["title"])
                                popularity = "`"+str(assign(["popularity"]))+"`"
                                ja_title = assign(["alternative_titles", "ja"])
                                status = "`"+assign(["status"])+"`"
                                num_volumes = "`"+str(assign(["num_volumes"]))+"`"
                                num_chapters = "`"+str(assign(["num_chapters"]))+"`"
                                score = "`"+str(assign(["mean"]))+"`"
                                desc = assign(["synopsis"])
                                rank = "`"+str(assign(['rank']))+"`"
                                genres = ran_out_vars("genres")
                                aired = "`"+str(assign(["start_date"]))+"`"
                                end = "`"+str(assign(["end_date"]))+"`"

                                embed = discord.Embed(
                                    title = title+" "+"("+ja_title+")",
                                    color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at,
                                    description = f"**Synopsis**\n\n{desc}"
                                    )       
                                embed.add_field(name="Volumes", value= num_volumes)
                                embed.add_field(name="Chapters", value= num_chapters)
                                embed.add_field(name="Score", value = score)
                                embed.add_field(name="Status", value=status)
                                embed.add_field(name="Popularity", value=popularity)
                                embed.add_field(name="Aired", value=aired)
                                embed.add_field(name="End", value=end)
                                embed.add_field(name="Genre", value=genres)
                                embed.add_field(name="Rank", value=rank)
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

        url = f'https://api.myanimelist.net/v2/manga?q={query}'
        headers = {
            "Authorization": f"Bearer {get('json/token.json').bearer}"
        }
        old_response = requests.request("GET", url, headers=headers).json()
        if "error" in old_response:
            update_token()
            url = f'https://api.myanimelist.net/v2/manga?q={query}'
            headers = {
                "Authorization": f"Bearer {get('json/token.json').bearer}"
            }
            response = requests.request("GET", url, headers=headers).json()
            await manga_exec(self, ctx, response)
        else:
            url = f'https://api.myanimelist.net/v2/manga?q={query}'
            headers = {
                "Authorization": f"Bearer {get('json/token.json').bearer}"
            }
            response = requests.request("GET", url, headers=headers).json()
            await manga_exec(self, ctx, response)

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
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=rcheck)
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