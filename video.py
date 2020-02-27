import youtube_dl
import os
import discord
import random
from utils_folder import utils as u

codecs = [".webm", ".m4a"]

YTDL_VIDEO_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
}

class Video:
    """Class containing information about a particular video."""

    def __init__(self, url_or_search, requested_by, client):
        """Plays audio from (or searches for) a URL."""
        with youtube_dl.YoutubeDL(YTDL_VIDEO_OPTS) as ydl:
            self.requested_by = requested_by
            video = self._get_info(url_or_search, requested_by)
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video[
                "thumbnail"] if "thumbnail" in video else None
            self.client = client

    def _get_info(self, video_url, author):
        with youtube_dl.YoutubeDL(YTDL_VIDEO_OPTS) as ydl:
            #ydl.download([video_url])
            info = ydl.extract_info(video_url, download=True)
            for file in os.listdir("./"):
                for i in codecs:    
                    if file.endswith(i):
                        data = u.retrieve("music.json")
                        song_names = data["song"]
                        if file not in song_names:
                            namae = f"{video_url}{author.id}{str(author.guild)}{hash(author.guild)}{random.randint(0, 10000)}{i}"
                            song_names += [namae]
                            u.save("music.json", data)
                            os.rename(file, namae)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"], author)  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=self.title, description=self.uploader, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed