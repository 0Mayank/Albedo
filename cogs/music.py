import asyncio
import logging
import math
import os
import random
from urllib import request
import requests

import discord
import youtube_dl
from discord.ext import commands
from discord.utils import get

from my_utils import default as u
from my_utils.guildstate import state_instance
from my_utils.video import YTDL_VIDEO_OPTS, Video

config = u.get("config.json")

al_admins = config.almins

YTDL_PLAYLIST_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "playliststart": 1,
    "playlistend": -1,
    #"progress_hooks":[song_status],
}

class Playlist:
    '''Class contais information about some shits, wanna eat??'''           #todo change this comment
    def __init__(self, url, requested_by, client, ctx, bot):
        """Plays audio from (or searches for) a URL."""
        with youtube_dl.YoutubeDL(YTDL_PLAYLIST_OPTS) as ydl:
            self.bot = bot
            self.ctx = ctx
            self.requested_by = requested_by
            #self.za_playlist = self._get_playlist_songs(url, requested_by)
            self.client = client
            self.url_list = self._get_playlist_songs(url, requested_by)

    def _get_playlist_songs(self, playlist_url, author):
        with youtube_dl.YoutubeDL(YTDL_PLAYLIST_OPTS) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            za_playlist = []
            if "_type" in info and info["_type"] == "playlist":
                for i in info["entries"]:
                    za_playlist += [self._get_playlist_songs(i["url"], author)]  # get info for first video
                return za_playlist
            else:
                za_playlist = [playlist_url]
                return za_playlist

    async def feed_url(self):
        play_command = self.bot.get_command("play")
        for url in self.url_list:
            await self.ctx.invoke(play_command, url)
            await asyncio.sleep(1)

async def audio_playing(ctx):
    #Checks that audio is currently playing before continuing.
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        await ctx.send("Not currently playing any audio")
        raise commands.CommandError("Not currently playing any audio.")


async def in_voice_channel(ctx):
    #Checks that the command sender is in the same voice channel as the client.
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if (voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel) or ctx.author.id in al_admins:
        return True
    else:
        return False

async def is_audio_requester(ctx):
    #Checks that the command sender is the song requester.
    music = ctx.bot.get_cog("Music")
    state = music.get_state(ctx.guild)
    permissions = ctx.channel.permissions_for(ctx.author)
    if permissions.administrator or state.is_requester(ctx.author) or ctx.author.id in al_admins:
        return True
    else:
        await ctx.send("You need to be the song requester to do that.")
        raise commands.CommandError(
            "You need to be the song requester to do that.")


class music(commands.Cog):
    """Bot commands to help play music."""

    def __init__(self, bot):
        self.bot = bot
        self.config = {"max_volume" : 250, "vote_skip" : True, "vote_skip_ratio" : 0.5}  # retrieve module name, find config entry
        self.states = {}

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        return state_instance.get_state(guild)
        
    @commands.command(aliases=["stop"])
    @commands.guild_only()
    #@commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        """Leaves the voice channel, if currently in one."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            if ctx.channel.permissions_for(ctx.author).administrator or ctx.author.id in al_admins:    
                state.loop = False
                await client.disconnect()
                dicc = u.retrieve("music.json")
                music_list1 = dicc["song"]
                for song in music_list1:
                    if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                        u.delete(song, "music.json", "song")
                state.playlist = []
                state.now_playing = None
            else:
                await ctx.send("You don't have the perms to do that")
        else:
            await ctx.send("Not in a voice channel")
            raise commands.CommandError("Not in a voice channel.")

    @commands.command(aliases=["repeat"])
    @commands.guild_only()
    async def loop(self, ctx, *, option = None):
        """loops any currently playing audio."""
        reply = self._loop(ctx, option)
        await ctx.send(reply)

    def _loop(self, ctx, option):
        state = self.get_state(ctx.guild)
        reply = ""
        if option == "on":
            state.loop = True
            reply = "Looping current song"
        elif option == "off":
            state.loop = False
            reply = "Loop disabled"
        else:
            reply = "Use loop on/off"
        
        return reply
    
    @commands.command(aliases=["resume", "p"])
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        client = ctx.guild.voice_client
        if await in_voice_channel(ctx) and await is_audio_requester(ctx) and await audio_playing(ctx) or ctx.author.id in al_admins:
            self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    """ @commands.command(aliases=["vol", "v"])
    @commands.guild_only()
    async def volume(self, ctx, volume: int):
        #Change the volume of currently playing audio (values 0-250).
        client = ctx.guild.voice_client
        if await in_voice_channel(ctx) and await is_audio_requester(ctx) and await audio_playing(ctx):    
            if await in_voice_channel(ctx):    
                state = self.get_state(ctx.guild)

                # make sure volume is nonnegative
                if volume < 0:
                    volume = 0

                max_vol = self.config["max_volume"]
                if max_vol > -1:  # check if max volume is set
                    # clamp volume to [0, max_vol]
                    if volume > max_vol:
                        volume = max_vol

                state.volume = float(volume) / 100.0
                client.source.volume = state.volume  # update the AudioSource's volume to match """

    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        if await in_voice_channel(ctx) and await audio_playing(ctx):    
            if state.is_requester(ctx.author) or ctx.author.id in al_admins: #or ctx.channel.permissions_for(ctx.author).administrator
                # immediately skip if requester or admin
                state.loop = False
                client.stop()
                dicc = u.retrieve("music.json")
                music_list1 = dicc["song"]
                for song in music_list1:
                    if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                        await u.delete(song, "music.json", "song")
                        break
            elif self.config["vote_skip"]:
                # vote to skip song
                channel = client.channel
                self._vote_skip(channel, ctx.author)
                # announce vote
                users_in_channel = len([
                    member for member in channel.members if not member.bot
                ])  # don't count bots
                required_votes = math.ceil(
                    self.config["vote_skip_ratio"] * users_in_channel)
                await ctx.send(
                    f"{ctx.author.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)"
                )
            else:
                raise commands.CommandError("Sorry, vote skipping is disabled.")

    def _vote_skip(self, channel, member):
        """Register a vote for `member` to skip the song playing."""
        logging.info(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([
            member for member in channel.members if not member.bot
        ]) + 1  # don't count bots
        if (float(len(state.skip_votes)) /
                users_in_channel) >= self.config["vote_skip_ratio"]:
            # enough members have voted to skip, so skip the song
            state.loop = False
            logging.info(f"Enough votes, skipping...")
            channel.guild.voice_client.stop()
            dicc = u.retrieve("music.json")
            music_list1 = dicc["song"]
            for song in music_list1:
                if f"{str(member.guild)}{hash(member.guild)}" in song:
                    u.delete(song, "music.json", "song")
                    break

    def _play_song(self, client, state, song, ctx):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
        dictt = u.retrieve("music.json")
        music_list2 = dictt["song"]
        for song in music_list2:
            if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song), volume=state.volume)
                break

        def after_playing(err):
            if state.loop == True or state.temp == True:
                state.temp = False
                song = state.now_playing
                self._play_song(client, state, song, ctx)
            elif len(state.playlist) > 0:
                dicc = u.retrieve("music.json")
                music_list1 = dicc["song"]
                for song in music_list1:
                    if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                        u.delete(song, "music.json", "song")
                        break
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song, ctx)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)
                dicc = u.retrieve("music.json")
                music_list1 = dicc["song"]
                for song in music_list1:
                    if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                        u.delete(song, "music.json", "song")

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    async def nowplaying(self, ctx):
        """Displays information about the current song."""
        if await audio_playing(ctx):    
            state = self.get_state(ctx.guild)
            message = await ctx.send("", embed=state.now_playing.get_embed())
            await self._add_reaction_controls(message)

    @commands.command(aliases=["q", "playlist"])
    @commands.guild_only()
    async def queue(self, ctx):
        """Display the current play queue."""
        if await audio_playing(ctx):    
            state = self.get_state(ctx.guild)
            await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        """Returns a block of text describing a given song queue."""
        if len(queue) > 0:
            message = [f"{len(queue)} songs in queue:"]
            message += [
                f"  {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

    @commands.command(aliases=["cq"])
    @commands.guild_only()
    #@commands.has_permissions(administrator=True)
    async def clearqueue(self, ctx):
        """Clears the play queue without leaving the channel."""
        if ctx.channel.permissions_for(ctx.author).administrator and await audio_playing(ctx) or ctx.author.id in al_admins:            #TODO: remove in_voice_client and check for permission
            dicc = u.retrieve("music.json")
            music_list1 = dicc["song"]
            songs_queued = []
            for song in music_list1:
                if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                    songs_queued += [song]
            for index in range(1, len(songs_queued)):    
                u.delete(songs_queued[index], "music.json", "song")
            state = self.get_state(ctx.guild)
            state.playlist = []

    @commands.command(aliases=["r"])
    @commands.guild_only()
    async def remove(self, ctx, song: int):
        """Removes a song in the queue"""
        state = self.get_state(ctx.guild)
        if await in_voice_channel(ctx) and await audio_playing(ctx) and state.is_song_requester(ctx.author, (song - 1)) or ctx.author.id in al_admins:
            if song <= len(state.playlist) and song > 0:
                await ctx.send(f"Removed {state.playlist[song - 1].title}")
                del state.playlist[song - 1]
                dicc = u.retrieve("music.json")
                music_list1 = dicc["song"]
                songs_queued = []
                for songi in music_list1:
                    if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in songi:
                        songs_queued += [songi]    
                u.delete(songs_queued[song], "music.json", "song")
    
    @commands.command(aliases=["jq"])
    @commands.guild_only()
    #@commands.check(audio_playing)
    #@commands.has_permissions(administrator=True)
    async def jumpqueue(self, ctx, song: int, new_index: int):
        """Moves song at an index to new index in queue."""
        if await in_voice_channel(ctx) and await audio_playing(ctx):            #TODO: remove in_voice_client and check for permission
            state = self.get_state(ctx.guild)  # get state for this guild
            if 1 <= song <= len(state.playlist) and 1 <= new_index:             #TODO: make it work
                song = state.playlist.pop(song-1)  # take song at index...
                state.playlist.insert(new_index-1, song)  # and insert it.

                await ctx.send(self._queue_text(state.playlist))
            else:
                raise commands.CommandError("You must use a valid index.")

    @commands.command(hidden = True)
    @commands.guild_only()
    async def play_playlist(self, ctx, *, url):
        """Plays playlist hosted at <url> (or performs a search for <url> and plays the first result)."""
        client = ctx.guild.voice_client
        owo_playlist = Playlist(url, ctx.author, client, ctx, self.bot)
        await owo_playlist.feed_url()
    
    @commands.command(brief="Plays audio from <url>.")
    @commands.guild_only()
    async def play(self, ctx, *, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)  # get the guild's state

        if client and client.channel:
            if ctx.author.voice != None:    
                if await in_voice_channel(ctx):    
                    try:
                        video = Video(url, ctx.author, client)
                    except youtube_dl.DownloadError as e:
                        logging.warn(f"Error downloading video: {e}")
                        await ctx.send(
                        "There was an error downloading your video, sorry.")
                        return
                    state.playlist.append(video)
                    message = await ctx.send(
                        "Added to queue.", embed=video.get_embed())
                    await self._add_reaction_controls(message)
                else:
                    users_in_channel = len([member for member in ctx.guild.voice_client.channel.members if not member.bot]) 
                    if (len(state.playlist)) == 0 or users_in_channel == 0 or ctx.author.id in al_admins:   
                        dicc = u.retrieve("music.json")
                        music_list1 = dicc["song"]
                        songs_queued = []
                        for song in music_list1:
                            if f"{str(ctx.author.guild)}{hash(ctx.author.guild)}" in song:
                                songs_queued += [song]
                                for index in range(1, len(songs_queued)):    
                                    u.delete(songs_queued[index], "music.json", "song")
                        state = self.get_state(ctx.guild)
                        state.playlist = []
                        channel = ctx.author.voice.channel
                        await client.disconnect()
                        try:
                            video = Video(url, ctx.author, client)
                        except youtube_dl.DownloadError as e:
                            await ctx.send(
                                "There was an error downloading your video, sorry.")
                            return
                        client = await channel.connect()
                        self._play_song(client, state, video, ctx)
                        message = await ctx.send("", embed=video.get_embed())
                        await self._add_reaction_controls(message)
                        logging.info(f"Now playing '{video.title}'")
                    else:
                        await ctx.send("Someone else is listening to the bot. Try again later")
            else:
                await ctx.send("You need to be in a voice channel to do that")
                raise commands.CommandError("You need to be in a voice channel to do that.")
        else:
            if ctx.author.voice != None and ctx.author.voice.channel != None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author, client)
                except youtube_dl.DownloadError as e:
                    await ctx.send(
                        "There was an error downloading your video, sorry.")
                    return
                client = await channel.connect()
                self._play_song(client, state, video, ctx)
                message = await ctx.send("", embed=video.get_embed())
                await self._add_reaction_controls(message)
                logging.info(f"Now playing '{video.title}'")
            else:
                await ctx.send("You need to be in a voice channel to do that")
                raise commands.CommandError(
                    "You need to be in a voice channel to do that.")
                
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.reaction, user: discord.user):
        #Respods to reactions added to the client's messages, allowing reactions to control playback.
        message = reaction.message
        if user != self.bot.user and message.author == self.bot.user:
            await message.remove_reaction(reaction, user)
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                permissions = message.channel.permissions_for(user)
                guild = message.guild
                state = self.get_state(guild)
                if permissions.administrator or (user_in_channel and state.is_requester(user)) or user.id in al_admins:
                    client = message.guild.voice_client
                    if reaction.emoji == "⏯":
                        # pause audio
                        self._pause_audio(client)
                    elif reaction.emoji == "⏭":
                        # skip audio
                        state.loop = False
                        if len(state.playlist) > 0:
                            client.stop()
                        else:
                            await client.disconnect()
                            state.now_playing = None
                    elif reaction.emoji == "⏮":
                        #state.playlist.insert(                     #todo: make a better fix to this
                            #0, state.now_playing
                        #)  # insert current song at beginning of playlist
                        state.temp = True
                        client.stop()
                elif reaction.emoji == "⏭" and self.config["vote_skip"] and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                    # ensure that skip was pressed, that vote skipping is enabled, the user is in the channel, and that the client is in a voice channel
                    voice_channel = message.guild.voice_client.channel
                    self._vote_skip(voice_channel, user)
                    # announce vote
                    channel = message.channel
                    users_in_channel = len([
                        member for member in voice_channel.members
                        if not member.client
                    ])  # don't count bots
                    required_votes = math.ceil(
                        self.config["vote_skip_ratio"] * users_in_channel)
                    await channel.send(
                        f"{user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)"
                    )

    async def _add_reaction_controls(self, message):
        """Adds a 'control-panel' of reactions to a message that can be used to control the client."""
        CONTROLS = ["⏮", "⏯", "⏭"]
        for contoller in CONTROLS:
            await message.add_reaction(contoller)

    

def setup(bot):
    bot.add_cog(music(bot))
