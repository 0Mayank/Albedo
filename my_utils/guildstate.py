from my_utils.dataIO import recover_states
class _states:
    ''' contains the states for an instance of bot '''
    def __init__(self):
        self.states = {}

    def get_state(self, guild_id):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild_id in self.states:
            return self.states[guild_id]
        else:
            self.states[guild_id] = GuildState()
            return self.states[guild_id]

    def delete_state(self, guild_id):
        """Delete the state of a guild"""
        del self.states[guild_id]
        
    def all_states(self):
        return self.states

class GuildState:
    ''' This class manages per-guild states '''
    def __init__(self):
        self.prefix = "/"
        self.mute_exists = False
        self.debugmode = False
        self.desc = True
        self.ping = False

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
recover_states(state_instance)