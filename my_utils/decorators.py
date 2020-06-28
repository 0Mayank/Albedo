from discord.ext import commands

def shared_cooldown(rate, per, type=commands.BucketType.default):
    cooldown = commands.Cooldown(rate, per, type=type)
    def decorator(func):
        if isinstance(func, commands.Command):
            func._buckets = commands.CooldownMapping(cooldown)
        else:
            func.__commands_cooldown__ = cooldown
        return func
    return decorator