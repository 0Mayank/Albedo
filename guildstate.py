import os

class _states:
    ''' contains the states for an instance of bot '''
    __slots__ = ('states')
    def __init__(self):
        self.states = {}

    def get_state(self, guild):
            """Gets the state for `guild`, creating it if it does not exist."""
            if guild.id in self.states:
                return self.states[guild.id]
            else:
                self.states[guild.id] = GuildState(guild.id)
                return self.states[guild.id]
    def all_states(self):
        return self.states

class GuildState:
    ''' This class manages per-guild states '''
    __slots__ = ('server', 'volume', 'playlist', 'skip_votes', 'now_playing', 'loop', 'temp', 'loopall', 'prefix')
    def __init__(self, server):
        self.server = server
        self.volume = 1
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None
        self.loop = False
        self.temp = False
        self.loopall = False 
        self.prefix = "-"

    def is_requester(self, user):
        return self.now_playing.requested_by == user
    
    def is_song_requester(self, user, index):
        return self.playlist[index].requested_by == user

state_instance = _states()