import json
import os
import time
import traceback
from collections import namedtuple
from io import BytesIO

import discord
import timeago as timesince

from my_utils.guildstate import state_instance


def get(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def traceback_maker(err, advance: bool = True):
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = ('```py\n{1}{0}: {2}\n```').format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


def timetext(name):
    return f"{name}_{int(time.time())}.txt"


def timeago(target):
    return timesince.format(target)


def date(target, clock=True):
    if clock is False:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason):
    responsible = f"[ {target} ]"
    if reason is None:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, mass=False):
    output = f"**{case}** the user"

    if mass is True:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def prettyResults(ctx, filename: str = "Results", resultmsg: str = "Here's the results:", loop=None):
    if not loop:
        return await ctx.send("The result was empty...")

    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) < 15:
        return await ctx.send(f"{resultmsg}```ini\n{pretty}```")

    data = BytesIO(pretty.encode('utf-8'))
    await ctx.send(
        content=resultmsg,
        file=discord.File(data, filename=timetext(filename.title()))
    )

def intcheck(it):                                                       #Interger checker
    isit = True
    try:
        int(it)
    except:
        isit = False

    return isit

def all_cases(za_word):
    if len(za_word) == 1:
        if za_word.isalnum():
            return [za_word.lower(), za_word.upper()]
        else:
            return[za_word]
    else:
        output = []
        f = za_word[0]
        l = za_word[1:]
        for st in all_cases(l):
            if f.isalnum():
                output.append(f.lower() + st)
                output.append(f.upper() + st)
            else:
                output.append(f+st)
        return output

def save(jsonfile, data):
    with open(f"json/{jsonfile}", "w") as f:
      json.dump(data, f, indent=4)

def retrieve(jsonfile):
    with open(f"json/{jsonfile}", "r") as f:
       data = json.load(f)
    return data

def delete(file, jsonFile, keyName):
    os.remove(file)
    data = retrieve(jsonFile)
    data[keyName].remove(file)
    save(jsonFile, data)

def format_seconds(time_seconds):
    """Formats some number of seconds into a string of format d days, x hours, y minutes, z seconds"""
    seconds = time_seconds
    hours = 0
    minutes = 0
    days = 0
    while seconds >= 60:
        if seconds >= 60 * 60 * 24:
            seconds -= 60 * 60 * 24
            days += 1
        elif seconds >= 60 * 60:
            seconds -= 60 * 60
            hours += 1
        elif seconds >= 60:
            seconds -= 60
            minutes += 1

    return f"{days}d {hours}h {minutes}m {seconds}s"

def check_availabilty(ctx):
    state = state_instance.get_state(ctx.guild)
    availability = state.get_var(ctx.command.name)
    return availability
