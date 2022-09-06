def user_is_mod(ctx):
    user_roles = ctx.user.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name

    return highest_guild_rol == highest_user_rol


class LeagueRanks:
    def __init__(self, multiplier, reward, name, diplay_name) -> None:
        self.multiplier = multiplier
        self.reward = reward
        self.name = name
        self.diplay_name = diplay_name

iron        = LeagueRanks(name="iron"         , diplay_name="Hierro",       multiplier=1.0,   reward=100)
bronze      = LeagueRanks(name="bronze"       , diplay_name="Bronce",       multiplier=1.5,   reward=150)
silver      = LeagueRanks(name="silver"       , diplay_name="Plata",        multiplier=1.6,   reward=200)
gold        = LeagueRanks(name="gold"         , diplay_name="Oro",          multiplier=1.7,   reward=250)
platinum    = LeagueRanks(name="platinum"     , diplay_name="Platino",      multiplier=1.8,   reward=300)
diamond     = LeagueRanks(name="diamond"      , diplay_name="Diamante",     multiplier=1.9,   reward=350)
master      = LeagueRanks(name="master"       , diplay_name="Maestro",      multiplier=2.0,   reward=400)
grandmaster = LeagueRanks(name="grandmaster"  , diplay_name="Gran Maestro", multiplier=2.5,   reward=450)
challenger  = LeagueRanks(name="challenger"   , diplay_name="Retador",      multiplier=3.0,   reward=500)

divisions = ["0", "i", "ii", "iii", "iv"]