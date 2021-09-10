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

def refresh_token():
    url = "https://myanimelist.net/v1/oauth2/token"

    data = {
        'client_id': 'e2784bdc2205cd151ab3797e54384adc',
        'client_secret': '7d7ea06984fd27c4a02be14d4748b7f9078e0a40055d8eda8872da05d7f6f649',
        'grant_type': 'refresh_token',
        'refresh_token': 'def502009f044ba09bb764ae60b3b5300bbb8c4f9c12c6bbf62d7f6a8292141787bb8c659f1c5b6d442b392051916ee4426e3287e36700ee7d7a4d8ef9cd931be5a15a3d5d79e26e0f60821d013c297e2fd9033094242c5c1353193a02259b6717305ca97644476257ef96ebd2f4887588c22e9fcfe602d431afb6024749c08bb601871e73d3d5aff59885135565cc39bde0ce906328fed22a54943e123f697a221faf9cad0622bebaaf090cb4c9a06d3efb0f315f62a3d98817fac56e66ca11d4a8b1de727970571deb278e6dc36a87f38bd095db4f04c6083b1ce6522294f2de3c8561d6d74d4d60e9f1d290eb7cc55809ddeaca57b511bae22b298ee965696166cffe1acf678652711c1eb2d9226c51ac14d0febd1f8dc8017ef7a77667c6044622df5eb3fb3db6ba38dcb2e1f0b870b531e05b39cdf2c71d1eb6ceef721b7679eea44f2543bc1b802f821ae8c859b46f225bbcc885774a9c3dcf62a8c3f62051cec92e183ec0f845577c4982e6d7d83776a54c04bdfa9be86bfad6a77769ee309d648ee13509'
    }

    response = requests.post(url, data=data)
    return response

class anime(commands.Cog):
    """yes weebs"""
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['te'])
    async def anime(self, ctx, *, query):
        url = f'https://api.myanimelist.net/v2/anime?q={query}'
        headers = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjNjZTg3OWFiN2RlMTk2OTc2N2VlM2FkYjg3MTNlYWExYTVkMDNhMTdiMzBiN2JkMDI3MTQ4YmI1MWJjMjlmN2VjMTI4ODg0OWNiMjc5MDYxIn0.eyJhdWQiOiJlMjc4NGJkYzIyMDVjZDE1MWFiMzc5N2U1NDM4NGFkYyIsImp0aSI6IjNjZTg3OWFiN2RlMTk2OTc2N2VlM2FkYjg3MTNlYWExYTVkMDNhMTdiMzBiN2JkMDI3MTQ4YmI1MWJjMjlmN2VjMTI4ODg0OWNiMjc5MDYxIiwiaWF0IjoxNjMxMjY2NzA2LCJuYmYiOjE2MzEyNjY3MDYsImV4cCI6MTYzMzg1ODcwNiwic3ViIjoiNzI0MDM0OCIsInNjb3BlcyI6W119.J7dikvrBZucWszoyOJvqCHXmLlirrLZ2o8T_S0MnAOsHVtWt_NenjO15C_f6tIy6bez8gaO5QWkJ3GEXUHilZVeoaBjRnA8QvGWCyojEZpHpdRrRPBncBDcogKZDentcqmcdtnfqWZhC6lPLwHDr5fMrk4CuHNGK2XJ-CT9tO1vTUdxDwSnpV3juW6mutKUKnX87vAgQZkIrbw63UunQ5KQ0sBL3I7wKp97VO4KuTAcYpoAygw6ro44IDGX5GVOWDaCrcE3VjHO016k4TBfwsUAngsyg8Avr8AI6cgABRktuKC7k8mO5Imxc_FSTsP572NwCZObekhBc_9rtI92Xlg"
        }

        response = requests.request("GET", url, headers=headers).json()

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
                            new_headers = {
                                        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjNjZTg3OWFiN2RlMTk2OTc2N2VlM2FkYjg3MTNlYWExYTVkMDNhMTdiMzBiN2JkMDI3MTQ4YmI1MWJjMjlmN2VjMTI4ODg0OWNiMjc5MDYxIn0.eyJhdWQiOiJlMjc4NGJkYzIyMDVjZDE1MWFiMzc5N2U1NDM4NGFkYyIsImp0aSI6IjNjZTg3OWFiN2RlMTk2OTc2N2VlM2FkYjg3MTNlYWExYTVkMDNhMTdiMzBiN2JkMDI3MTQ4YmI1MWJjMjlmN2VjMTI4ODg0OWNiMjc5MDYxIiwiaWF0IjoxNjMxMjY2NzA2LCJuYmYiOjE2MzEyNjY3MDYsImV4cCI6MTYzMzg1ODcwNiwic3ViIjoiNzI0MDM0OCIsInNjb3BlcyI6W119.J7dikvrBZucWszoyOJvqCHXmLlirrLZ2o8T_S0MnAOsHVtWt_NenjO15C_f6tIy6bez8gaO5QWkJ3GEXUHilZVeoaBjRnA8QvGWCyojEZpHpdRrRPBncBDcogKZDentcqmcdtnfqWZhC6lPLwHDr5fMrk4CuHNGK2XJ-CT9tO1vTUdxDwSnpV3juW6mutKUKnX87vAgQZkIrbw63UunQ5KQ0sBL3I7wKp97VO4KuTAcYpoAygw6ro44IDGX5GVOWDaCrcE3VjHO016k4TBfwsUAngsyg8Avr8AI6cgABRktuKC7k8mO5Imxc_FSTsP572NwCZObekhBc_9rtI92Xlg"
                                    }

                            new_response = requests.request("GET", new_url, headers=new_headers).json()

                            def ran_out_vars(more_var):
                                try:
                                    var_str = ""
                                    for i in range(len(new_response[more_var])):
                                        var_str += "`"+new_response[more_var][i]['name']+"`" + " "
                                    return var_str
                                except KeyError:
                                    return "`"+"N/A"+"`"

                            def assign(path):
                                dcopy = new_response
                                for key in path:
                                    if key in dcopy:
                                        dcopy = dcopy[key]
                                    else:
                                        return '`'+'N/A'+'`'
                                        
                                return dcopy

                            image = assign(["main_picture", "large"])
                            title = assign(["title"])
                            popularity = "`"+str(assign(["title"]))+"`"
                            ja_title = assign(["alternative_titles", "ja"])
                            status = "`"+assign(["status"])+"`"
                            episodes = "`"+str(assign(["num_episodes"]))+"`"
                            score = "`"+str(assign(["mean"]))+"`"
                            desc = assign(["synopsis"])
                            rating = "`"+str(assign(["rating"]).capitalize())+"`"
                            premiered = "`"+(assign(['start_season', 'season']))[0].upper() + (assign(['start_season', 'season']))[1:] + " " + str(assign(['start_season', 'year']))+"`"
                            rank = "`"+str(assign(['rank']))+"`"
                            genres = ran_out_vars("genres")
                            studios = ran_out_vars("studios")
                            aired = "`"+str(assign(["start_date"]))+"`"
                            end = "`"+str(assign(["end_date"]))+"`"

                            if assign(['broadcast', 'day_of_the_week']) != '`'+'N/A'+'`':
                                broadcast = "`"+assign(['broadcast', 'day_of_the_week']).capitalize()+" "+assign(['broadcast', 'start_time'])+"`"
                            else:
                                broadcast = '`'+'N/A'+'`'

                            embed = discord.Embed(
                                title = title+" "+"("+ja_title+")",
                                color = discord.Colour.from_rgb(0,250,141), timestamp=ctx.message.created_at,
                                description = desc
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