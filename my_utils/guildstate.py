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
            self.states[guild.id] = GuildState(guild)
            return self.states[guild.id]

    def delete_state(self, guild):
        """Delete the state of a guild"""
        del self.states[guild.id]
        
    def all_states(self):
        return self.states

class GuildState:
    ''' This class manages per-guild states '''
    __slots__ = ('server', 'roles', 'prefix', 'mute_exists', 'debugmode', 'desc')
    def __init__(self, server):
        self.server = server
        self.roles = server.roles 
        self.prefix = "/"
        self.mute_exists = False
        self.debugmode = False
        self.desc = True

    def get_var(self, variable):
        try:    
            var = getattr(self, variable)
            return var
        except:
            return True
    
    def set_var(self, variable, value):
        setattr(self, variable, value)
        return

state_instance = _states()