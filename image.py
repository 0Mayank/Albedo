import io
import json
import re
import random
import discord
import requests
from discord.ext import commands, tasks

import utils as u
from utils_folder import http
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk

#NjczNTI0NDMwNDE2Mzc5OTA1.Xj_c9Q.NNAnD6B_0_cnOAZA7A7O7x0vP7w

def _exist(user_id):
    profiles = u.retrieve("profile.json")
    if user_id in profiles["id"]:
        return True
    return False

def _initialise(user_id, force_initialise = False, index = 0):
    if _exist(user_id) is False or force_initialise is True:
        profiles = u.retrieve("profile.json")
        if force_initialise is True:
            for colors in profiles.keys():
                del profiles[colors][index]
        profiles["id"] += [user_id]
        profiles["arc color"] += ["#00adb5"]
        profiles["bg color"] += ["#303841"]
        profiles["text color"] += ["#eeeeee"]
        profiles["banner"] += ["#3a4750"]
        profiles["number color"] += ["#00adb5"]
        profiles["ranker color"] += ["#eeeeee"]
        profiles["arc path color"] += ["#bbbcbd"]
        u.save("profile.json", profiles)


def _get_index(user):
    profiles = u.retrieve("profile.json")
    if _exist(user) is True:
        return profiles["id"].index(user)
    else:
        _initialise(user, True)

def _get_color(index, location):
    profiles = u.retrieve("profile.json")
    return profiles[location][index]

def _change_color(index, color, location):
    profiles = u.retrieve("profile.json")
    profiles[location][index] = color
    u.save("profile.json", profiles)

class imagetesting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(aliases = ["c"], invoke_without_command = True)
    async def customize(self, ctx):
        _initialise(str(ctx.author.id), False)

        await ctx.send("Nope, no category like dat found")

    @customize.command()
    async def arc(self, ctx, color):
        _initialise(str(ctx.author.id), False)
        try:
            background = Image.new("RGB", (700, 1100), color = color)
        except:
            return await ctx.send("Invalid colors, baka")
        ind = _get_index(str(ctx.author.id))
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "arc color")
        await ctx.send(f"Arc color changed to `{color}`")
    
    @customize.command(aliases = ["bg"])
    async def background(self, ctx, color):
        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "bg color")
        await ctx.send(f"Background color changed to `{color}`")

    @customize.command(aliases = ["bn"])
    async def banner(self, ctx, color):
        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "banner")
        await ctx.send(f"Banner color changed to `{color}`")

    @customize.command(aliases = ["tc"])
    async def textcolor(self, ctx, color):
        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "text color")
        await ctx.send(f"Text color changed to `{color}`")
    
    @customize.command(aliases = ["nc"])
    async def numbercolor(self, ctx, color):
        _initialise(str(ctx.author.id))
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "number color")
        await ctx.send(f"Number color changed to `{color}`")

    @customize.command(aliases = ["rc"])
    async def rankercolor(self, ctx, color):
        _initialise(str(ctx.author.id))
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "ranker color")
        await ctx.send(f"Ranker color changed to `{color}`")

    @customize.command(aliases = ["apc"])
    async def arcpathcolor(self, ctx, color):
        _initialise(str(ctx.author.id))
        ind = _get_index(str(ctx.author.id))
        _change_color(ind, color, "arc path color")
        await ctx.send(f"arc path color changed to `{color}`")

    @customize.command()
    async def mode(self, ctx, mode):
        _initialise(str(ctx.author.id), False)
        ind = _get_index(str(ctx.author.id))
        if mode == "light":    
            _change_color(ind, "#7289DA", "arc color")
            _change_color(ind, "#8E9FDD", "bg color")  
            _change_color(ind, "white", "text color")
            _change_color(ind, "#FAFAFA", "banner")
            _change_color(ind, "white", "number color")
            _change_color(ind, "#7289DA", "ranker color")
            _change_color(ind, "white", "arc path color")
            await ctx.send("Light theme active.")

        elif mode == "dark":
            _change_color(ind, "#5c5470", "arc color")
            _change_color(ind, "#2a2438", "bg color")
            _change_color(ind, "#dbd8e3", "text color")
            _change_color(ind, "#352f44", "banner")
            _change_color(ind, "#dbd8e3", "number color")
            await ctx.send("Dark theme active.")

        elif mode == "default":
            _initialise(str(ctx.author.id), True, ind)
            await ctx.send("Default theme active.")

    @customize.command()
    async def show(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        _initialise(str(member.id), False)
        ind = _get_index(str(member.id))
        profiles = u.retrieve("profile.json")

        arc = profiles["arc color"][ind]
        bg = profiles["bg color"][ind]
        text = profiles["text color"][ind]
        number = profiles["number color"][ind]
        banner = profiles["banner"][ind]

        u.save("profile.json", profiles)
        
        await ctx.send(f"Profile colors of **{str(member)[:-5]}**\n\n**Arc color** `{arc}`\n**Background color** `{bg}`\n**Text color** `{text}`\n**Number color** `{number}`\n**Banner color** `{banner}`")

    @commands.command()
    async def img(self, ctx, *, text: str):
        try:
            map_text, map_col = re.split(', |,',text)
        except ValueError:
            await ctx.send("yele default colour bhosdi")
            map_text = text
            map_col = "grey"

        font_size = 25
        font = ImageFont.truetype('Philosopher-Italic.ttf', font_size)
        font_size = font.getsize(map_text)
        img = Image.new('RGB', (font_size[0]+10, 30), color = map_col)

        draw = ImageDraw.Draw(img)
        # text_size = draw.textsize(map_text, font)

        draw.text((5,2), map_text, font=font, fill=(0, 0, 0))
        img.save('pil_text_font.png')

        await ctx.send(file=discord.File('pil_text_font.png'))


    @commands.command(aliases = ["rank"])
    async def profile(self, ctx, member: discord.Member = None, url):
        member = ctx.author if not member else member
        _initialise(str(member.id), False)
        profiles = u.retrieve("profile.json")
        ind = _get_index(str(member.id))

        # VARIABLES
        member_rank = _get_rank(str(ctx.guild.id), str(member.id))
        if member_rank == False:
            return await ctx.send(f"**{member.name}** has not messaged yet, so their profile doesn't exist.")
        member_total_exp = _get_total_exp(str(ctx.guild.id), str(member.id))
        member_current_exp = _get_current_exp(str(ctx.guild.id), str(member.id))
        member_level = _get_level(str(ctx.guild.id), str(member.id)) 
        exp_for_levelup = 50*member_level**2 + 50*member_level + 100
        arc_end = (member_current_exp/exp_for_levelup)*360 - 90
        bgc = _get_color(ind, "bg color")
        bannerc = _get_color(ind, "banner")
        numberc = _get_color(ind, "number color")
        textc = _get_color(ind, "text color")
        arcc = _get_color(ind, "arc color")
        rankerc = _get_color(ind, "ranker color")
        arcpathc = _get_color(ind, "arc path color")

        try:
        # LOADING THE AVATAR            
            response = requests.get(member.avatar_url)
            im = Image.open(io.BytesIO(response.content))

        # MASK FOR AVATAR

            im = im.resize((300, 300))
            bigsize = (im.size[0] * 4, im.size[1] * 4)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)

            output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            output.save('output.png')

            w, h = 350, 350
            shape = [(0, 0), (w, h)]


        # CREATING IMAGES
            #bio = await http.get(url, res_method="read")
            image.retrieve(url,str(ctx.author.id))
                
            background = Image.new("RGB", (700, 1100), color = bannerc)
            small_bg = Image.new("RGB", (700, 820), color=bgc)
            small_circle_img = Image.new("RGB", (w, h))
            small_circle = ImageDraw.Draw(small_circle_img)
            small_circle.ellipse(shape, fill=bgc)

        # MASK FOR SMALL CIRCLE
            im2 = im.resize((350, 350))
            bigsize2 = (im2.size[0] * 4, im2.size[1] * 4)
            mask2 = Image.new('L', bigsize2, 0)
            draw2 = ImageDraw.Draw(mask2) 
            draw2.ellipse((0, 0) + bigsize2, fill=bannerc)
            mask2 = mask2.resize(im2.size, Image.ANTIALIAS)
            small_circle_img.putalpha(mask2)

        # TEXT

            text = str(member)
            font_size = 70
            font = ImageFont.truetype('fonts/monofonto.ttf', font_size)
            text_draw = ImageDraw.Draw(small_bg)
            w1, h1 = font.getsize(text)
            text_draw.text(((700-w1)/2, (230-h1)/2), text, font=font, fill=numberc)
        # RANK, LEVEL, EXP TEXT
            font_size2 = 45
            font2 = ImageFont.truetype('fonts/soloist1.ttf', font_size2)
            rank_draw = ImageDraw.Draw(background)
        # MAIN TEXT
            font_size3 = 100
            font3 = ImageFont.truetype('fonts/Fragmentcore.ttf', font_size3)
            number_draw = ImageDraw.Draw(background)
        # TOP LEFT RANK
            font_size4 = 130
            font4 = ImageFont.truetype('fonts/ROBOTECH_GP.ttf', font_size4)
            ranker = ImageDraw.Draw(background)

        # PASTING

            background.paste(small_circle_img, (175, 5), im2)

            background.paste(small_bg, (0,280))
            background.paste(im, (200, 30), im)

        # ARC
            arc_draw = ImageDraw.Draw(background)
            #             x0  y0  x1   y1      
        # GREY EXP ARC    
            arc_draw.arc((190, 700, 510, 1030), start = -90, end = 270, fill=arcpathc, width = 7)     
            
        # EXP ARC 
            arc_draw.arc((190, 700, 510, 1030), start = -90, end = arc_end, fill = arcc, width = 12)

        # OUTER GREY CIRCLE
            arc_draw.arc((165, 675, 535, 1055), start = -90, end = 270, fill = arcc, width = 1)       

        # TEXT FOR RANK & LEVEL
            rw = font2.getsize("Rank")[0]
            lw = font2.getsize("Level")[0]
            ew = font2.getsize("Exp")[0]
            rank_draw.text(((700-rw)/2, 770), "Rank", font=font2, fill=textc)
            rank_draw.text(((500-lw)/4, 500), "Level", font=font2, fill=textc)
            rank_draw.text((3*(750-ew)/4, 500), "Exp", font=font2, fill=textc)

        # TEXT FOR NUMBER

            rnw = font3.getsize(str(member_rank))[0]
            lnw = font3.getsize(str(member_level))[0]
            enw = font3.getsize(str(member_total_exp))[0]
            number_draw.text(((700-rnw)/2, 840), str(member_rank), font=font3, fill=numberc)
            number_draw.text(((540-lnw)/4, 565), str(member_level), font=font3, fill=numberc)
            number_draw.text((3*(750-enw)/4, 565), str(member_total_exp), font=font3, fill=numberc)

            ranker.text((30,0), f"#{str(member_rank)}", font=font4, fill=rankerc)
            background.save('overlap.png')
            u.save("profile.json", profiles)
            await ctx.send(file=discord.File('overlap.png'))

        except ValueError:
            await ctx.send("Invalid colors, setting to default.")
            _initialise(member.id, True, ind)

    @commands.command(aliases = ["lb"])
    async def leaderboard(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        profiles = u.retrieve("profile.json")
        
        # CREATING BACKGROUND
        background = Image.new("RGB", (1000, 700), color = "#352f44")
        
        # GETTING AVATAR
        response = requests.get(member.avatar_url)
        im = Image.open(io.BytesIO(response.content))    
        
        # MASK FOR AVATAR
        im = im.resize((100, 100))
        bigsize = (im.size[0] * 4, im.size[1] * 4)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)

        # VARIABLES FOR TEXT IN RANK_CIRCLE
        font_size = 80
        font = ImageFont.truetype('Philosopher-Italic.ttf', font_size)
               

        height = 30
        i = 1
        users = 5
        # PASTING

        # LOOP FOR USERS IN LEADERBOARD
        while i <= users:
            if i == 1:
                rank_circle_color = "#DA9E3B"
                pass
            elif i == 2:
                rank_circle_color = "#989898"
                pass
            elif i == 3:
                rank_circle_color = "#AE7441"
                pass
            else:
                rank_circle_color = "#50555A"
                pass

            # RANK CIRCLE
            rank_circle_img = Image.new("RGB", (100, 100))
            rank_circle = ImageDraw.Draw(rank_circle_img)
            rank_circle.ellipse([(0, 0), (100, 100)], fill = rank_circle_color)

            # RANK NUMBER FOR RANK_CIRCLE 
            text_draw = ImageDraw.Draw(rank_circle_img)    
            text_draw.text((30, 30), str(i), font=font, fill="white")

            background.paste(im, (150, height), im)
            background.paste(rank_circle_img, (20, height) ,im)
            height += 700//users
            i += 1
        
        background.save('leaderboard_bg.png')
        u.save("profile.json", profiles)
        await ctx.send(file=discord.File("leaderboard_bg.png"))


    # @commands.command(aliases = ["flb"])
    # async def fakeleaderboard(self, ctx):
    #     embed = discord.Embed(title="Leaderboard")
def setup(bot):
    bot.add_cog(imagetesting(bot))
