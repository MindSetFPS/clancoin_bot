def user_is_mod(ctx):
    user_roles = ctx.user.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name

    return highest_guild_rol == highest_user_rol

def user_time(seconds):
    def return_plural(seconds, unidad):
        return "s" if seconds > unidad * 2 else "" 
    
    second = 1
    minute = 60
    hour = minute * 60
    day = hour * 24
    month = day * 30
    year = month * 12

    if seconds > day:
        return f'{int(seconds/day)} dia{return_plural(seconds, day)}'
    if seconds > hour:
        return f'{int(seconds/hour)} horas{return_plural(seconds, hour)}'
    if seconds > minute:
        return f'{int(seconds/minute)} minuto{return_plural(seconds, minute)}'
    if  seconds < minute:
        return f'{int(seconds)} segundos'


class LeagueRanks:
    def __init__(self, multiplier, reward, name, display_name) -> None:
        self.multiplier = multiplier
        self.reward = reward
        self.name = name
        self.display_name = display_name

iron        = LeagueRanks(name="iron"         , display_name="Hierro",       multiplier=1.0,   reward=100.0)
bronze      = LeagueRanks(name="bronze"       , display_name="Bronce",       multiplier=1.5,   reward=150.0)
silver      = LeagueRanks(name="silver"       , display_name="Plata",        multiplier=1.6,   reward=200.0)
gold        = LeagueRanks(name="gold"         , display_name="Oro",          multiplier=1.7,   reward=250.0)
platinum    = LeagueRanks(name="platinum"     , display_name="Platino",      multiplier=1.8,   reward=300.0)
diamond     = LeagueRanks(name="diamond"      , display_name="Diamante",     multiplier=1.9,   reward=350.0)
master      = LeagueRanks(name="master"       , display_name="Maestro",      multiplier=2.0,   reward=400.0)
grandmaster = LeagueRanks(name="grandmaster"  , display_name="Gran Maestro", multiplier=2.5,   reward=450.0)
challenger  = LeagueRanks(name="challenger"   , display_name="Retador",      multiplier=3.0,   reward=500.0)

divisions = ["0", "i", "ii", "iii", "iv"]