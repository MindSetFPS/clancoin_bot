def user_is_mod(ctx):
    user_roles = ctx.user.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name

    return highest_guild_rol == highest_user_rol

def user_to_string(ctx):
    return ctx.user.name + '#' + ctx.user.discriminator 

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
        return f'{int(seconds/hour)} hora{return_plural(seconds, hour)}'
    if seconds > minute:
        return f'{int(seconds/minute)} minuto{return_plural(seconds, minute)}'
    if  seconds < minute:
        return f'{int(seconds)} segundos'

def move_forward(arr, pos=0):
    lenght = len(arr) - 1
    print('len ' + str(lenght))
    next_position = pos + 1

    if next_position > lenght:
        return 0
    else:
        return next_position

def move_backwards(arr, pos):
    lenght = len(arr) - 1
    print('len ' + str(lenght))
    next_position = pos - 1

    if next_position < 0:
        return lenght
    else:
        return next_position
