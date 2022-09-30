import sys
import os
import io
import discord
from dotenv import load_dotenv
from discord.commands import Option
from discord.ext import commands, pages
from helpers import user_is_mod, user_time, user_to_string
from league_of_legends import iron, bronze, silver, gold, platinum, diamond, master, grandmaster, challenger
from transaction import get_user_coins, insert_welcome_gift_transaction, create_new_prediction, insert_daily_transaction, insert_gift_transaction, user_got_welcome_gift, insert_portrait_transaction
from custom_views import ApproveView, Store, Create_add_item_view, BetView
from PIL import Image, ImageFont, ImageDraw
from urllib.request import urlopen
from portadas import portadas

tiers = [iron, bronze, silver, gold, platinum, diamond, master, grandmaster, challenger]
bot = discord.Bot(intents=discord.Intents.all())

if sys.argv[1] == "dev":
    load_dotenv('.env.development')
elif sys.argv[1] == "prod":
    load_dotenv('.env.production')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
clancoin_emote = '<:clancoin:974120483693924464>'

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_member_join(member):
    bot_full_user = bot.user.name + '#' + bot.user.discriminator
    discord_full_user = member.name + '#' + member.discriminator
    insert_welcome_gift_transaction(amount=500, sent_by=bot_full_user, received_by=discord_full_user)
    channel = discord.utils.get(member.guild.channels, name="👋・bienvenidas")
    await channel.send(f"<@{member.id}> recibiste 500 {clancoin_emote} Clan Coins.")

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(content=f'Vuelve a intentar en {user_time(error.retry_after)}', ephemeral=True) 
    else: 
        raise error

@bot.slash_command(name="recompensa_promo", description="Reclama tu recompensa por ganar tu promo.")
async def recompensa_division(
    ctx: discord.ApplicationContext,
    img: Option(discord.SlashCommandOptionType.attachment, "Atachment"),
    tier: Option(str, "Tier", choices=[iron.display_name , bronze.display_name , silver.display_name, gold.display_name, platinum.display_name, diamond.display_name, master.display_name, grandmaster.display_name, challenger.display_name ]),
    division: Option(str, "Division", choices=["IV", "III", "II", "I"]),
    mensaje: Option(str, "Deja un mensaje libre.") = " "
):
    print('/recompensa_promo')
    img_to_file = await img.to_file()
    await ctx.respond(f'{mensaje} {tier} {division}', file=img_to_file)
    await ctx.respond(f'{ctx.guild.owner.mention}', view=ApproveView(ctx=ctx, tier=tier, division=division, command="recompensa_promo"))

@bot.slash_command(name="recompensa_jugada", description="Reclama tu recompensa por jugada. Enfriamiento: 24 horas.")
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def recompensa_jugada(
    ctx: discord.ApplicationContext, 
    jugada: Option(str, "Jugada", choices=["TripleKill", "QuadraKill", "PentaKill"]),
    video:Option(discord.SlashCommandOptionType.attachment, "Usa video para subir un archivo grabado en tu pc. (Maximo 8MB).", required=False),
    link: Option(str, "Usa link si su1biste tu jugada a una plataforma como Youtube, Twitch, etc.", required=False)
):
    await ctx.defer()
    print('/recompensa_jugada')
    submission = link if link else ""
    if video:
        video_file = await video.to_file()
        # video_file = video
        await ctx.send_followup(content=f'{jugada}', file=video_file)
    else:
        await ctx.respond(f' {jugada} {submission}')

    await ctx.respond(f"{ctx.guild.owner.mention}", view=ApproveView(command="recompensa_jugada", ctx=ctx, play=jugada))

@bot.slash_command(name="monedas_diarias", description ="Obtén tus monedas diarias.")
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def get_coins(ctx):
    discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
    bot_full_user = bot.user.name + '#' + bot.user.discriminator

    #get current coins number
    coins = get_user_coins(user=user_to_string(ctx.author))
    current_coins = coins.data[0]["coins"]
    transaction = insert_daily_transaction(sent_by=bot_full_user, received_by=discord_full_user, amount=10 )
    await ctx.respond(f"Recibiste tus monedas diarias, ahora tienes {current_coins + 10} {clancoin_emote}", ephemeral=True)

@bot.slash_command(name="mis_clancoins", description="Mira cuantas Clan Coins tienes.")
async def check_clancoins(ctx):
    print("/mis_clancoins")
    discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
    
    coins = get_user_coins(user=discord_full_user)

    if len(coins.data) > 0:
        current_coins = coins.data[0]["coins"]
        await ctx.respond(f"Tienes {current_coins} {clancoin_emote}", ephemeral=True)
    else:
        await ctx.respond(f"Tienes {0} {clancoin_emote}", ephemeral=True)

@bot.slash_command(name="dar_monedas_a_usuario", description="Da ClanCoins a un usario.")
async def give_clancoins(ctx, member: discord.Member, amount: int):
    if user_is_mod(ctx=ctx):
        discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
        discord_member_full_username = member.name + '#' + member.discriminator
        transaction = insert_gift_transaction(sent_by=discord_full_user, received_by=discord_member_full_username, amount=amount)
        
        await ctx.respond(f'Le diste {amount} {clancoin_emote} a {member.mention}.')
    else:
        await ctx.respond("No tienes permiso para hacer eso.")

@bot.slash_command(name="dar_monedas_a_muchos_usuarios", description="Da a la misma cantidad de ClanCoins a un monton de usarios.")
async def give_coins_to_many_users(ctx, users_list: str, amount: int):
    await ctx.defer()
    # time.sleep(4)
    # Por limitaciones de discord, primero tenemos que asegurarnos que cada nombre#discriminator estan separados por una coma
    # La lista de usuarios no puede ser mayor a 2000 caracteres 
    new_list = users_list.replace('\t', '') #si copias de excel la lista de usuarios, te añade un tab, esta linea lo elimina
    new_list = new_list.split(",") #usa la coma para separar cada usuario

    received = []
    if user_is_mod(ctx=ctx):
        for user in new_list:
            user_clean = user.lstrip()
            discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
            transaction = insert_gift_transaction(sent_by=discord_full_user, received_by=user_clean, amount=amount)
                
            received.append(user)

        received = ', '.join(received)
        await ctx.send_followup(content=f'Le diste {amount} {clancoin_emote} a {received}.')
    else:
        await ctx.send_followup(content="No tienes permiso para hacer eso.")

@bot.slash_command(name="tienda", description="Mira la tienda de Clan y compra tus items favoritos.")
async def shop(ctx: discord.ApplicationContext):
    paginator = Store(user_to_string(ctx=ctx.author)).paginator
    await paginator.respond(ctx.interaction, ephemeral=True)

@bot.slash_command(name = "add_new_item", description = "Add a new item to the store.")
async def add_new_item(ctx):
    if user_is_mod(ctx=ctx):
        modal = Create_add_item_view(title="Creando un nuevo objeto para la tienda.")
        await ctx.send_modal(modal)
    else:
        await ctx.respond("No tienes el rol necesario para usar este comando.", ephemeral=True)

@bot.slash_command(name="nueva_prediccion", description="Crear nueva predicción.")
async def create_new_bet(
    ctx: discord.ApplicationContext, 
    question: Option(str, "Pregunta de la prediccion."), 
    team_option0: Option(str, "Equipo 1", choices=['isurus', 'beyond', 'drx', 'fnatic', 'rng', 'dnf','evil_geniuses', 'mad_lions', 'saigon_buffalo', 'loud', 'istambul_wildcats', 'chiefs']), 
    team_option1: Option(str, "Equipo 2", choices=['isurus', 'beyond', 'drx', 'fnatic', 'rng', 'dnf','evil_geniuses', 'mad_lions', 'saigon_buffalo', 'loud', 'istambul_wildcats', 'chiefs']),
    channel: Option(discord.TextChannel, "Canal donde se publicara esta prediccion."),
    prize: Option(int, "Cuantas Clan Coins recibiran los ganadores de la prediccion.") = 75,
    costo: Option(int, "Costo por entrar a la prediccion.") = 25,
):

    if user_is_mod(ctx=ctx):
        # print("User is mod, continue")
        prediction = create_new_prediction(option0=team_option0, option1=team_option1, prize=prize, text=question)
        print(prediction[0]["id"])

        embed = discord.Embed(title=question)
        embed.add_field(name="Entrada: ", value=f"{clancoin_emote} {costo}")
        embed.add_field(name="Premio: ", value=f"{clancoin_emote} {prize}")

        betView = BetView(ctx=ctx, teamOption0=team_option0, teamOption1=team_option1, question=question, id=prediction[0]["id"], prize=prize, entry_cost=costo)

        await channel.send(content=None, view=betView, embed=embed)
        await ctx.respond(content=f'Creada encuesta "{question}" en el canal {channel.mention}')
    else:
        await ctx.respond("No tienes el rol necesario para usar este comando.", ephemeral=True)

@bot.slash_command(name="portada", description="Consigue una portada de Equipo de Worlds por 200 ClanCoins.")
async def portada(
    ctx: discord.ApplicationContext, 
    red: Option(str, '¿Para que red social quiere la portada?', choices=['Facebook', 'Twitter']), 
    equipo: Option(str, 'El equipo del que quieres la portada.', choices=['Isurus', 'Fnatic']),
    nombre: Option(str=None, description="Nombre (Opcional, si no escribes ninguno, usa tu nombre de Discord)", required=False)
):
    coins = get_user_coins(user=user_to_string(ctx=ctx.user))

    if len(coins.data) > 0:
        if coins.data[0]["coins"] > 200:
            current_coins = coins.data[0]["coins"]
            await ctx.defer()

            portada_template = portadas.return_team(team=equipo)
            portada_template_url = portada_template.return_social_media_link(sm=red)

            image = Image.open(urlopen(portada_template_url))

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('./SEQUEL/SEQUEL/Sequel100Black-76.ttf', portada_template.size[red])
            text = ctx.author.name
            draw.text(
                text=nombre if nombre else text, 
                xy=(portada_template.x[red], portada_template.y[red]), 
                font=font, 
                fill=portada_template.color, 
                anchor='rm'
            )

            porta = io.BytesIO()    
            image.save(porta, format='png')
            porta.seek(0)

            await ctx.send_followup(content="Aqui tienes tu portada personalizada.", file=discord.File(fp=porta, filename='portada.png'))
            insert_portrait_transaction(sent_by=user_to_string(ctx=bot.user), received_by=user_to_string(ctx=ctx.user), amount=-200)
        else:
            await ctx.respond(f"No tienes suficientes Clan Coins {clancoin_emote}", ephemeral=True)
    else:
        await ctx.respond(f"Tienes {0} {clancoin_emote}", ephemeral=True)

@bot.slash_command(name="marco", description="Obten una foto de perfil para apoyar a tu equipo favorito durante #Worlds2022.")
async def profile_picture(ctx: discord.ApplicationContext, equipo: Option(str, '¿De que equipo es el diseño de tu marco?', choices=['Isurus', 'Fnatic'])):
    coins = get_user_coins(user=user_to_string(ctx=ctx.user))
    if len(coins.data) > 0:
        if coins.data[0]["coins"] > 150:
            current_coins = coins.data[0]["coins"]
            await ctx.defer()

            team = portadas.return_team(team=equipo)

            fpbuffer = io.BytesIO(await ctx.author.display_avatar.read())

            photo = Image.open(fpbuffer)
            marco =  Image.open(urlopen(team.portrait))

            marco_resized = marco.resize((photo.height, photo.width), Image.Resampling.LANCZOS)

            photo.paste(marco_resized, (0, 0), marco_resized)
            buffer = io.BytesIO()
            photo.save(buffer, format='png')
            buffer.seek(0)

            await ctx.send_followup(content=f"Aqui tienes tu foto de perfil personalizada.", file=discord.File(fp=buffer, filename='foto.png'), ephemeral=True)

            insert_portrait_transaction(sent_by=user_to_string(ctx=bot.user), received_by=user_to_string(ctx=ctx.user), amount=-200)
        else:
            await ctx.respond(f"No tienes suficientes Clan Coins {clancoin_emote}", ephemeral=True)
    else:
        await ctx.respond(f"Tienes {0} {clancoin_emote}", ephemeral=True)

bot.run(DISCORD_TOKEN)