from unicodedata import name
from peewee import *
from dotenv import load_dotenv
import discord
from discord.ui import Modal, View, InputText, Button
from discord.commands import Option
from discord.ext import commands, pages
import os
import sys
from helpers import user_time, user_is_mod, move_backwards, move_forward, iron, bronze, silver, gold, platinum, diamond, master, grandmaster, challenger
from transaction import get_store_items, supabase, insert_promo_reward_transaction, insert_play_reward


tiers = [iron, bronze, silver, gold, platinum, diamond, master, grandmaster, challenger]
load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())

if sys.argv[1] == "dev":
    DISCORD_TOKEN = os.getenv('DEVELOPMENT_DISCORD_TOKEN')
elif sys.argv[1] == "prod":
    DISCORD_TOKEN = os.getenv('CLAN_ACADEMY_DISCORD_TOKEN')

clancoin_emote = '<:clancoin:974120483693924464>'
clancoin_emote_id = 974120483693924464
pepega = '<:pepega:776918257785241630>'

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_member_join(member):
    # print(member.guild)
    bot_full_user = bot.user.name + '#' + bot.user.discriminator
    discord_full_user = member.name + '#' + member.discriminator
    print(member.name)

    transaction = supabase.table("transaction").insert({
            "transaction_type": "welcome_gift", 
            "amount" : 500, 
            "sent_by": bot_full_user, 
            "received_by": discord_full_user
        }).execute()


    insertion = supabase.table("discord_user").insert({"discordUser":discord_full_user, "coins": 500}).execute()

    channel = discord.utils.get(member.guild.channels, name="👋・bienvenidas")
    await channel.send(f"<@{member.id}> recibiste 500 {clancoin_emote} Clan Coins.")

@bot.slash_command(name="check_mod", description="¿Tienes el rango mas alto del servidor?")
@commands.cooldown(1, 60*60*24*3, commands.BucketType.user)
async def check_mod(ctx):
    print('/check_mod')
    await ctx.respond(user_is_mod(ctx))

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(content=f'Vuelve a intentar en {user_time(error.retry_after)}', ephemeral=True)
    else:
        raise error

class ApproveView(discord.ui.View):
    def __init__(self, ctx, command, division=None, tier=None, play=None):
        super().__init__()

        self.author = ctx.author
        self.command = command
        self.division = division
        self.tier = tier
        self.play = play

        aprove_button = Button(label="Aceptar", style=discord.ButtonStyle.primary, emoji="👍")
        async def aprove_callback(interaction):
            if user_is_mod(interaction):
                if self.command == "recompensa_jugada":
                    aprover_mod = interaction.user.name + '#' + interaction.user.discriminator
                    author_name = self.author.name + '#' + self.author.discriminator
                    print("reclamando recompensa por jugada")
                    if self.play == "TripleKill":
                        print('Recompensa de triple') 
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=50, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 50 Clan Coins.", view=None)
                    if self.play == "QuadraKill": 
                        print('Recompensa de quadra')
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=150, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 150 Clan Coins.", view=None)
                    if self.play == "PentaKill":
                        print('Recompensa de penta') 
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=250, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 250 Clan Coins.", view=None)


                if self.command == "recompensa_promo":
                    for tier in tiers:
                        print(self.tier)
                        print(tier.display_name)
                        reward = 0
                        if tier.display_name == self.tier:
                            print("player is " + tier.display_name)
                            aprover_mod = interaction.user.name + '#' + interaction.user.discriminator
                            author_name = self.author.name + '#' + self.author.discriminator
                            reward = tier.reward
                            if self.division == "IV":
                                print(tier.multiplier * tier.reward)
                                reward = reward * tier.multiplier
                            insert_promo_reward_transaction(sent_by=aprover_mod, received_by=author_name, amount=reward, transaction_type=f'{tier.name}_{self.division}')
                            print('reward sent')
                            await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} {int(reward)} Clan Coins.", view=None)
                            break
                        # insert_promo_reward_transaction(sent_by=interaction.user, received_by=self.author_id, amount=tier.reward, transaction_type=f'{tier.name}_{self.tier.lower()}')
            else:
                await interaction.response.send_message("Un moderador te dará tu recompensa.", ephemeral=True)
        
        reject_button = Button(label="Rechazar", style=discord.ButtonStyle.red, emoji="👎")
        async def reject_callback(interaction):
            if user_is_mod(interaction):
                await interaction.response.edit_message(content="Revisa tu aporte.", view=None)
            else:
                await interaction.response.send_message("Un moderador te dará tu recompensa.", ephemeral=True)

        print_button = Button(label="test", style=discord.ButtonStyle.grey, emoji="🔥")
        async def test_callback(interaction):
            await interaction.response.send_message(self.command)
        
        aprove_button.callback = aprove_callback
        reject_button.callback = reject_callback
        print_button.callback = test_callback

        self.add_item(aprove_button)
        self.add_item(reject_button)
        self.add_item(print_button)

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
    # await ctx.respond(f"Felicidades <@{ctx.author.id}> por llegar a {name} {division}.", file=await img.to_file())
    await ctx.respond(f'{mensaje} {tier} {division}', file=img_to_file)
    await ctx.respond(f'{ctx.guild.owner_id}', view=ApproveView(ctx=ctx, tier=tier, division=division, command="recompensa_promo"))

@bot.slash_command(name="recompensa_jugada", description="Reclama tu recompensa por jugada.")
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

    await ctx.respond("", view=ApproveView(command="recompensa_jugada", ctx=ctx, play=jugada))

@bot.slash_command(name="get_coins", description = "Get your 10 coins of the day.")
@commands.cooldown(1, 20, commands.BucketType.user)
async def get_coins(ctx):
    username = ctx.author.name
    discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
    bot_full_user = bot.user.name + '#' + bot.user.discriminator

    # #get current coins number
    # coins = supabase.table("discord_user").select("coins").match({"discordUser":discord_full_user}).execute()
    # current_coins = coins.data[0]["coins"]
    # print(current_coins)

    # update = supabase.table("discord_user").update({"coins": current_coins + 10 }).match({"discordUser":discord_full_user}).execute()
    # transaction = supabase.table("transaction").insert({"transaction_type": "daily_reward", "amount": 10, "sent_by": bot_full_user, "received_by": discord_full_user}).execute()

    # user = bot.get_user(user_id) or await bot.fetch_user(user_id)
    current_coins = 20
    await ctx.respond(f"Ya recibiste tus monedas diarias, tienes {current_coins + 10} <:omegalul:776917394428919808>", ephemeral=True)

@bot.slash_command(name="mis_clancoins", description="Mira cuantas Clan Coins tienes.")
async def check_clancoins(ctx):
    print("/mis_clancoins")
    discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
    coins = supabase.table("discord_user").select("coins").match({"discordUser":discord_full_user}).execute()

    # transactions = supabase.table("transaction").select('*').eq('transaction_type', 'welcome_gift').eq('received_by', user).execute()

    if len(coins.data) > 0:
        current_coins = coins.data[0]["coins"]
        print(current_coins)
        await ctx.respond(f"Tienes {current_coins} <:clancoin:974120483693924464> ", ephemeral=True)
    else:
        await ctx.respond(f"Tienes {0} <:clancoin:974120483693924464> ", ephemeral=True)


@bot.slash_command(name="dar_monedas_a_usuario", description="Da ClanCoins a un usario.")
async def give_clancoins(ctx, member: discord.Member, amount: int):
    user_roles = ctx.author.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name
    
    if highest_guild_rol == highest_user_rol:
        discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
        discord_member_full_username = member.name + '#' + member.discriminator
        transaction = supabase.table("transaction").insert({"transaction_type": "gift", "amount" : amount, "sent_by": discord_full_user, "received_by": discord_member_full_username}).execute()
        assert len(transaction.data) > 0
        await ctx.respond(f'Le diste {amount} {clancoin_emote} a {discord_member_full_username}.')
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
    
    user_roles = ctx.author.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name

    received = []
    
    if highest_guild_rol == highest_user_rol:
        for user in new_list:
            print(user)
            user_clean = user.lstrip()
            discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
            transaction_exists = supabase.table("transaction").select('*').eq('transaction_type', 'welcome_gift').eq('received_by', user_clean).execute()

            if len(transaction_exists.data) > 0:
                print(user_clean + ' already got welcome gift')
            else:
                transaction = supabase.table("transaction").insert({
                        "transaction_type": "welcome_gift", 
                        "amount" : amount, 
                        "sent_by": discord_full_user, 
                        "received_by": user_clean
                    }).execute()

                assert len(transaction.data) > 0

                user_row = supabase.table("discord_user").select("*").eq("discordUser", user_clean).execute()
                assert len(transaction.data) > 0

                if len(user_row.data) > 0:
                    print(user_row)
                    print(user_row.data)
                    print(user_row.data[0]["coins"])
                    new_coin_amount = user_row.data[0]["coins"] + amount
                    supabase.table("discord_user").update({"coins": new_coin_amount}).eq("discordUser", user_clean).execute()
                
                received.append(user)

        received = ', '.join(received)
        await ctx.send_followup(content=f'Le diste {amount} {clancoin_emote} a {received}.')
    else:
        await ctx.send_followup(content="No tienes permiso para hacer eso.")


class Store():
    def __init__(self) -> None:
        self.buy_button = None
        self.cancel_button = None
        self.items = get_store_items()
        self.index = 0
        self.interaction_buttons = self.view(self.index)
        self.prev = pages.PaginatorButton(button_type="prev", emoji="⏪", disabled=False, style=discord.ButtonStyle.blurple)
        self.indicator = pages.PaginatorButton(button_type="page_indicator", disabled=True)
        self.next = pages.PaginatorButton(button_type="next", emoji="⏩", style=discord.ButtonStyle.blurple)

        async def next_item(interaction: discord.Interaction):
            print(self.paginator.current_page)
            self.index = self.paginator.current_page
            print(self.paginator.current_page)
            self.interaction_buttons.clear_items()
            self.interaction_buttons.add_item(
                 discord.ui.Button(
                    label=f'Comprar por {self.items.data[move_forward(self.items.data, self.paginator.current_page)]["price"]} Clan Coins', 
                    row=1,
                    style=discord.ButtonStyle.green, 
                    emoji=clancoin_emote, 
                )
            )
            self.interaction_buttons.add_item(
                discord.ui.Button(
                    label="Cancelar",
                    style=discord.ButtonStyle.red,
                    emoji="✖️",
                    row=1
                )
            )
            await self.paginator.goto_page(move_forward(self.items.data, self.paginator.current_page), interaction=interaction)
        self.next.callback = next_item

        self.paginator = pages.Paginator(
            pages=self.embed(), 
            custom_view=self.interaction_buttons, 
            loop_pages=True, 
            use_default_buttons=False
        )
        # self.index = self.paginator.current_page
        self.paginator.add_button(self.prev)
        self.paginator.add_button(self.indicator)
        self.paginator.add_button(self.next)

    def embed(self):
        embeds = []
        for store_item in self.items.data:
            emb = discord.Embed(title=store_item["name"], description=f'{store_item["description"]} {clancoin_emote} ')
            emb.set_image(url=store_item["image_url"])
            # emb.add_field(name=store_item["price"], value="dfsd")
            emb.set_footer(text=f'{store_item["price"]} {clancoin_emote}')
            embeds.append(emb)
        return embeds
    
    def view(self, index):
        view = discord.ui.View()
        print(index)
        self.buy_button = discord.ui.Button(
            label=f'Comprar por {self.items.data[index]["price"]} Clan Coins', 
            style=discord.ButtonStyle.green,
            emoji=clancoin_emote, 
            row=1
        )

        cancel_button = discord.ui.Button(
            label="Cancelar",
            style=discord.ButtonStyle.red,
            emoji="✖️",
            row=1
        )
        view.add_item(self.buy_button)
        view.add_item(cancel_button)
        return view

@bot.slash_command(name="strings")
async def pagetest_strings(ctx: discord.ApplicationContext):
    """Demonstrates passing a list of strings as pages."""

    # paginator = pages.Paginator(pages=Store.embed(), custom_view=Store.view(), loop_pages=True )
    # store = Store()
    paginator = Store().paginator
    await paginator.respond(ctx.interaction, ephemeral=True)

@bot.slash_command(name="tienda", description="Mira los objetos en la tienda de Clan.")
async def store(ctx):
    items = supabase.table("item").select("*").execute()
    assert len(items.data) > 0

    embeds = []

    for item in items.data:
        print(item)
        emb = discord.Embed(title=item["name"], )
        emb.add_field(name="Precio", value=item["price"] )
        embeds.append(emb)

    last_emb = discord.Embed(title="Usa /buy para comprar.")
    embeds.append(last_emb)

    await ctx.respond(embeds=embeds, ephemeral=True)


@bot.slash_command(name="comprar", description="Compra el objeto que quieras con tus Clan Coins.")
async def buy(ctx: discord.ApplicationContext, name: str = False):
    if name:
        await ctx.respond(f'Comprar {name}')
    else:
        await ctx.respond("Mira los objetos de la tienda")


@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    # print(ctx.guild.members)
    user_id = ctx.author.id
    user = bot.get_user(user_id) or await bot.fetch_user(user_id)
    await user.send('whatever')

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Nombre"))
        self.add_item(discord.ui.InputText(label="Precio"))
        self.add_item(discord.ui.InputText(label="Descripcion", style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Image URL"))
        self.add_item(discord.ui.InputText(label="Codigo - Cantidad", required=False))

    async def callback(self, interaction: discord.Interaction):

        payload = {
            "name": self.children[0].value,
            "price": self.children[1].value,
            "description": self.children[2].value,
            "image_url": self.children[3].value,
        }

        embed = discord.Embed(title="Nuevo objeto")

        if len(self.children[4].value) > 0:
            code_and_amount = self.children[4].value.split(" ")
            print(code_and_amount)

            payload["code"] = code_and_amount[0]
            payload["amount"] = code_and_amount[1]

            embed.add_field(name="Codigo", value=code_and_amount[0])
            embed.add_field(name="Cantidad", value=code_and_amount[1])

        supabase.table("item").insert(payload).execute()

        embed.add_field(name="Nombre", value=self.children[0].value)
        embed.add_field(name="Precio", value=self.children[1].value)
        embed.add_field(name="Descripcion", value=self.children[2].value)
        embed.set_image(url=self.children[3].value)

        await interaction.response.send_message(embeds=[embed], ephemeral=True)

@bot.slash_command(name = "add_new_item", description = "Add a new item to the store.")
async def add_new_item(ctx):
    user_roles = ctx.author.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name
    
    if highest_guild_rol == highest_user_rol:
        print("User is in the highest role, he is authorized to use this command")
        modal = MyModal(title="Modal via Slash Command")
        await ctx.send_modal(modal)
    else:
        await ctx.respond("No tienes el rol necesario para usar este comando.", ephemeral=True)

bot.run(DISCORD_TOKEN)