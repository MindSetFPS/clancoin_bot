def user_is_mod(ctx):
    user_roles = ctx.user.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name

    return highest_guild_rol == highest_user_rol

league_ranks = (
    "iron_iv",
    "iron_iii",
    "iron_ii",
    "iron_i",
    "bronze_iv",
    "bronze_iii",
    "bronze_ii",
    "bronze_i",
    "silver_iv",
    "silver_iii",
    "silver_ii",
    "silver_i",
    "gold_iv",
    "gold_iii",
    "gold_ii",
    "gold_i",
    "platinum_iv",
    "platinum_iii",
    "platinum_ii",
    "platinum_i",
    "diamond_iv",
    "diamond_iii",
    "diamond_ii",
    "diamond_i",
    "master",
    "grandmaster",
    "challenger",
)