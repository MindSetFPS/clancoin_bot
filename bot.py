from peewee import *
import datetime
from db import db
from Models import Users, Transaction
from dotenv import load_dotenv
import discord
from discord.ui import Modal, View, InputText
from discord.commands import Option
import os
from supabase.client import Client, create_client

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())
db.connect()
db.create_tables([Users, Transaction])

url = os.getenv("url")
key = os.getenv("public")

supabase: Client = create_client(url, key)

clancoin_emote = '<:clancoin:974120483693924464>'

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.event
async def on_member_join(member):
    # print(member.guild)
    discord_full_user = member.name + '#' + member.discriminator
    print(member.name)

    data = supabase.table("discord_user").insert({"discordUser":discord_full_user}).execute()
    assert len(data.data) > 0

    channel = discord.utils.get(member.guild.channels, name="👋・bienvenidas")
    await channel.send(f"<@{member.id}> recibiste 500 {clancoin_emote} Clan Coins.")

# @bot.slash_command(name="get_coins", description = "Get your 10 coins of the day.")
# async def get_coins(ctx):
#     username = ctx.author.name
#     discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
#     bot_full_user = bot.user.name + '#' + bot.user.discriminator

#     #get current coins number
#     coins = supabase.table("discord_user").select("coins").match({"discordUser":discord_full_user}).execute()
#     current_coins = coins.data[0]["coins"]
#     print(current_coins)

#     update = supabase.table("discord_user").update({"coins": current_coins + 10 }).match({"discordUser":discord_full_user}).execute()
#     transaction = supabase.table("transaction").insert({"transaction_type": "daily_reward", "amount": 10, "sent_by": bot_full_user, "received_by": discord_full_user}).execute()

#     # user = bot.get_user(user_id) or await bot.fetch_user(user_id)
#     await ctx.respond(f"Ya recibiste tus monedas diarias, tienes {current_coins + 10} <:omegalul:776917394428919808>", ephemeral=True)

@bot.slash_command(name="mis_clancoins", description="Mira cuantas Clan Coins tienes.")
async def check_clancoins(ctx):
    print("/mis_clancoins")
    discord_full_user = ctx.author.name + '#' + ctx.author.discriminator
    coins = supabase.table("discord_user").select("coins").match({"discordUser":discord_full_user}).execute()

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

        if len(self.children[4].value) > 0:
            code_and_amount = self.children[4].value.split(" ")
            print(code_and_amount)

            payload["code"] = code_and_amount[0]
            payload["amount"] = code_and_amount[1]

            embed.add_field(name="Codigo", value=code_and_amount[0])
            embed.add_field(name="Cantidad", value=code_and_amount[1])

        supabase.table("item").insert(payload).execute()

        embed = discord.Embed(title="Nuevo objeto")
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

bot.run(os.getenv('CLAN_ACADMEY_DISCORD_TOKEN'))
db.close()  